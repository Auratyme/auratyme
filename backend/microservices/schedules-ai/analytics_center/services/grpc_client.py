"""
gRPC client for Analytics Center to communicate with schedules-ai.

Educational Note:
This client demonstrates microservice communication pattern where
Analytics Center (UI layer) communicates with schedules-ai service
via gRPC protocol with FULL scheduler data.

NEW: Uses schedule_generation.proto with complete fields:
- Tasks with duration_minutes, priority
- Fixed events with time windows
- User preferences (meals, routines, work hours)
- User profile (MEQ score, age, sleep_need)

Purpose:
- Connect Analytics Center to schedules-ai via gRPC
- Send FULL task data from UI to scheduler
- Receive generated schedules
- Handle connection errors gracefully
"""

import grpc
import logging

logger = logging.getLogger(__name__)

try:
    import sys
    
    if '/app/src' not in sys.path:
        sys.path.insert(0, '/app/src')
    
    from grpc_generated import schedule_generation_pb2  # type: ignore
    from grpc_generated import schedule_generation_pb2_grpc  # type: ignore
    GRPC_AVAILABLE = True
except ImportError as e:
    logger.error(f"Cannot import gRPC generated files: {e}")
    logger.error("Make sure to run: python -m grpc_tools.protoc to generate files")
    schedule_generation_pb2 = None  # type: ignore
    GRPC_AVAILABLE = False


class ScheduleGrpcClient:
    """
    gRPC client for schedule generation service with FULL data support.
    
    Educational Note:
        This client now sends complete scheduler data via gRPC
        including tasks with duration/priority, preferences, and profile.
    """
    
    def __init__(self, host="schedules-ai-grpc", port=50051):
        """Initialize gRPC client connection."""
        self.address = f"{host}:{port}"
        self.channel = None
        self.stub = None
        logger.info(f"📡 gRPC Client initialized for {self.address}")
    
    def connect(self):
        """Establishes connection to gRPC server."""
        if not GRPC_AVAILABLE:
            raise ImportError("gRPC generated files not available")
        
        try:
            logger.info(f"🔗 Attempting to connect to gRPC server at {self.address}...")
            self.channel = grpc.insecure_channel(
                self.address,
                options=[
                    ('grpc.max_send_message_length', -1),
                    ('grpc.max_receive_message_length', -1),
                ]
            )
            
            grpc.channel_ready_future(self.channel).result(timeout=5)
            self.stub = schedule_generation_pb2_grpc.ScheduleGenerationServiceStub(self.channel)
            logger.info(f"✅ Connected to gRPC server at {self.address}")
            return True
        except grpc.FutureTimeoutError:
            logger.error(f"❌ Timeout: gRPC server not responding at {self.address}")
            self.channel = None
            self.stub = None
            return False
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            self.channel = None
            self.stub = None
            return False
    
    def generate_schedule(self, payload_data: dict):
        """
        Requests schedule generation via gRPC with FULL data.
        
        Args:
            payload_data: Complete payload dict with:
                - user_id, target_date
                - tasks: [{"name", "duration_minutes", "priority"}]
                - fixed_events: [{"name", "start_time", "end_time"}]
                - preferences: {"meals", "routines", "work"}
                - user_profile: {"meq_score", "age", "sleep_need"}
        
        Returns:
            Dictionary with generated schedule
        """
        if not self.stub:
            if not self.connect():
                logger.error("❌ Cannot establish gRPC connection")
                return {"success": False, "error": "gRPC server unavailable"}
        
        try:
            logger.info(f"📤 === Sending FULL schedule request via gRPC ===")
            logger.info(f"   🆔 User: {payload_data.get('user_id')}")
            logger.info(f"   📅 Date: {payload_data.get('target_date')}")
            logger.info(f"   📋 Tasks: {len(payload_data.get('tasks', []))}")
            logger.info(f"   📍 Fixed Events: {len(payload_data.get('fixed_events', []))}")
            
            request = self._build_grpc_request(payload_data)
            logger.info(f"   🔨 Built request, sending to {self.address}...")
            
            # Timeout musi być duży - LLM generowanie zajmuje 40-60+ sekund
            response = self.stub.GenerateSchedule(request, timeout=300)
            
            logger.info(f"📥 === Received gRPC Response ===")
            logger.info(f"   📊 Schedule ID: {response.schedule_id}")
            logger.info(f"   ✅ Items count: {len(response.scheduled_items)}")
            logger.info(f"   💬 Message: {response.message}")
            
            logger.info(f"📝 SCHEDULED ITEMS RECEIVED:")
            for i, item in enumerate(response.scheduled_items):
                logger.info(f"   [{i}] type={item.type}, name={item.name}, {item.start_time} -> {item.end_time}")
            
            result = self._convert_response(response)
            logger.info(f"   🔄 Converted to dict format")
            return result
            
        except grpc.RpcError as e:
            logger.error(f"❌ gRPC RPC Error: {e.code()}")
            logger.error(f"   Details: {e.details()}")
            return {"success": False, "error": f"gRPC Error: {e.details()}"}
        except grpc.FutureTimeoutError:
            logger.error(f"❌ gRPC Timeout: Request took longer than 300s")
            return {"success": False, "error": "gRPC timeout - schedule generation took too long"}
        except Exception as e:
            logger.error(f"❌ Error: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Closes gRPC channel connection."""
        if self.channel:
            self.channel.close()
            logger.info("🔌 Closed gRPC connection")
    
    def _convert_priority_to_int(self, priority):
        """Converts priority string/int to integer (1-5)."""
        if isinstance(priority, str):
            priority_map = {
                "low": 1,
                "medium": 3,
                "high": 5,
                "critical": 5
            }
            return priority_map.get(priority.lower(), 3)
        try:
            val = int(priority) if priority else 3
            return max(1, min(5, val))  # Clamp to 1-5
        except (ValueError, TypeError):
            return 3
    
    def _safe_int(self, value, default: int = 0) -> int:
        """Safely convert value to int with fallback."""
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def _safe_str(self, value, default: str = "") -> str:
        """Safely convert value to str with fallback."""
        if value is None:
            return default
        try:
            return str(value)
        except (ValueError, TypeError):
            return default
    
    def is_server_available(self):
        """
        Checks if gRPC server is available.
        
        Returns:
            bool: True if server responds, False otherwise
        """
        try:
            if not self.stub:
                self.connect()
            
            with grpc.insecure_channel(self.address) as channel:
                grpc.channel_ready_future(channel).result(timeout=2)
            
            logger.info("✅ gRPC server is available")
            return True
            
        except grpc.FutureTimeoutError:
            logger.warning(f"⚠️ gRPC server not available at {self.address}")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Cannot connect to gRPC server: {e}")
            return False
    
    def _build_grpc_request(self, payload_data: dict):
        """Converts payload dict to gRPC request message."""
        logger.info("=" * 100)
        logger.info("� BUILDING gRPC REQUEST")
        logger.info("=" * 100)
        logger.info(f"📊 Payload keys: {list(payload_data.keys())}")
        logger.info(f"   user_id: {payload_data.get('user_id')}")
        logger.info(f"   target_date: {payload_data.get('target_date')}")
        
        tasks = []
        try:
            task_list = payload_data.get("tasks", [])
            logger.info(f"� Processing {len(task_list)} TASKS:")
            for i, t in enumerate(task_list):
                logger.info(f"   [{i}] name={t.get('name')}, duration={t.get('duration_minutes')}min, priority={t.get('priority')}, deadline={t.get('deadline')}")
                task = schedule_generation_pb2.TaskInput(
                    id=str(t.get("id", "")),
                    name=str(t.get("name", "")),
                    duration_minutes=int(t.get("duration_minutes", 60)) if t.get("duration_minutes") else 60,
                    priority=self._convert_priority_to_int(t.get("priority", 3)),
                    deadline=t.get("deadline") or ""
                )
                tasks.append(task)
        except Exception as e:
            logger.error(f"❌ Task building error: {e}")
            raise
        
        logger.info(f"✅ {len(tasks)} tasks converted to gRPC")
        
        fixed_events = payload_data.get("fixed_events", [])
        logger.info(f"📍 Processing {len(fixed_events)} FIXED EVENTS:")
        for i, e in enumerate(fixed_events):
            logger.info(f"   [{i}] name={e.get('name')}, {e.get('start_time')} -> {e.get('end_time')}")
        
        fixed_events = [
            schedule_generation_pb2.FixedEventInput(
                id=str(e.get("id", "")),
                name=str(e.get("name", "")),
                start_time=str(e.get("start_time", "")),
                end_time=str(e.get("end_time", ""))
            )
            for e in fixed_events
        ]
        logger.info(f"✅ {len(fixed_events)} fixed events converted to gRPC")
        
        prefs = payload_data.get("preferences", {})
        meals = prefs.get("meals", {})
        routines = prefs.get("routines", {})
        work = prefs.get("work", {})
        
        logger.info(f"🔧 PREFERENCES DETAILS:")
        logger.info(f"   🍽️  Meals:")
        logger.info(f"      breakfast_enabled: {meals.get('breakfast_enabled')} | lunch_enabled: {meals.get('lunch_enabled')} | dinner_enabled: {meals.get('dinner_enabled')}")
        logger.info(f"      breakfast_duration: {meals.get('breakfast_duration')} | lunch_duration: {meals.get('lunch_duration')} | dinner_duration: {meals.get('dinner_duration')}")
        logger.info(f"   🌅 Routines:")
        logger.info(f"      morning_routine_minutes: {routines.get('morning_routine_minutes')}")
        logger.info(f"      evening_routine_minutes: {routines.get('evening_routine_minutes')}")
        logger.info(f"      enable_afternoon_break: {routines.get('enable_afternoon_break')}")
        logger.info(f"      afternoon_break_minutes: {routines.get('afternoon_break_minutes')}")
        logger.info(f"   💼 Work:")
        logger.info(f"      start: {work.get('start')} | end: {work.get('end')}")
        
        preferences = schedule_generation_pb2.SchedulePreferences(
            rounding=prefs.get("rounding", True),
            meals=schedule_generation_pb2.MealPreferences(
                breakfast_enabled=meals.get("breakfast_enabled", False),
                lunch_enabled=meals.get("lunch_enabled", True),
                dinner_enabled=meals.get("dinner_enabled", False),
                breakfast_duration=self._safe_int(meals.get("breakfast_duration"), 0),
                lunch_duration=self._safe_int(meals.get("lunch_duration"), 60),
                dinner_duration=self._safe_int(meals.get("dinner_duration"), 0)
            ),
            routines=schedule_generation_pb2.RoutinePreferences(
                morning_routine_minutes=self._safe_int(routines.get("morning_routine_minutes"), 45),
                evening_routine_minutes=self._safe_int(routines.get("evening_routine_minutes"), 45),
                enable_afternoon_break=routines.get("enable_afternoon_break", False),
                afternoon_break_minutes=self._safe_int(routines.get("afternoon_break_minutes"), 0)
            ),
            work=schedule_generation_pb2.WorkHours(
                start=self._safe_str(work.get("start"), "09:00"),
                end=self._safe_str(work.get("end"), "17:00"),
                work_type=self._safe_str(work.get("work_type"), "remote"),
                commute_minutes=self._safe_int(work.get("commute_minutes"), 0)
            )
        )
        
        logger.info(f"✅ Preferences converted to gRPC")
        
        profile_data = payload_data.get("user_profile", {})
        logger.info(f"� USER PROFILE:")
        logger.info(f"   meq_score: {profile_data.get('meq_score')}")
        logger.info(f"   age: {profile_data.get('age')}")
        logger.info(f"   sleep_need: {profile_data.get('sleep_need')}")
        try:
            meq = int(profile_data.get("meq_score", 50)) if profile_data.get("meq_score") else 50
            age = int(profile_data.get("age", 30)) if profile_data.get("age") else 30
            sleep_need = str(profile_data.get("sleep_need", "medium"))
            logger.info(f"✅ Profile converted: meq={meq}, age={age}, sleep_need='{sleep_need}'")
        except Exception as e:
            logger.error(f"❌ Profile conversion error: {e}, profile_data={profile_data}")
            raise
        
        user_profile = schedule_generation_pb2.UserProfile(
            meq_score=meq,
            age=age,
            sleep_need=sleep_need
        )
        
        request = schedule_generation_pb2.ScheduleGenerationRequest(
            user_id=str(payload_data.get("user_id", "")),
            target_date=str(payload_data.get("target_date", "")),
            tasks=tasks,
            fixed_events=fixed_events,
            preferences=preferences,
            user_profile=user_profile
        )
        
        logger.info("=" * 100)
        logger.info("✅ gRPC REQUEST BUILT SUCCESSFULLY")
        logger.info("=" * 100)
        
        return request
    
    def _convert_response(self, response):
        """Converts gRPC response to dict format."""
        logger.info("=" * 100)
        logger.info("🔄 CONVERTING gRPC RESPONSE TO DICT")
        logger.info("=" * 100)
        
        scheduled_items = []
        logger.info(f"📝 Converting {len(response.scheduled_items)} items:")
        for i, item in enumerate(response.scheduled_items):
            logger.info(f"   [{i}] id={item.id}, type={item.type}, name={item.name}, {item.start_time} -> {item.end_time}")
            scheduled_items.append({
                "id": item.id,
                "type": item.type,
                "name": item.name,
                "start_time": item.start_time,
                "end_time": item.end_time
            })
        
        result = {
            "success": True,
            "schedule_id": response.schedule_id,
            "user_id": response.user_id,
            "message": response.message,
            "scheduled_items": scheduled_items
        }
        
        logger.info(f"✅ Conversion complete - {len(scheduled_items)} items in final dict")
        logger.info("=" * 100)
        
        return result


def create_grpc_client():
    """
    Factory function to create gRPC client instance.
    
    Returns:
        ScheduleGrpcClient instance or None if not available
    """
    if not GRPC_AVAILABLE:
        logger.warning("⚠️ gRPC client not available - proto files not generated")
        return None
    
    return ScheduleGrpcClient()
