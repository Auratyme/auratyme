"""
gRPC server for receiving schedule generation requests.

Educational Note:
This server receives schedule data via gRPC and forwards it to
the HTTP API endpoint /generate-simple which returns the schedule.

Architecture:
1. gRPC receives data (tasks, preferences, profile)
2. HTTP API generates schedule via /generate-simple
3. gRPC returns the schedule response
"""

import sys
import grpc
import logging
import httpx
from concurrent import futures
from pathlib import Path
from datetime import datetime
from uuid import uuid4

sys.path.insert(0, '/app/src')

try:
    from grpc_generated import schedule_generation_pb2  # type: ignore
    from grpc_generated import schedule_generation_pb2_grpc  # type: ignore
except ImportError as e:
    logging.error(f"Cannot import gRPC generated files: {e}")
    logging.error("Run: python -m grpc_tools.protoc to generate proto files")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Inside Docker network, use service name instead of localhost
HTTP_API_URL = "http://schedules-ai:8000/v1/schedule/generate-simple"


class ScheduleGenerationServicer(schedule_generation_pb2_grpc.ScheduleGenerationServiceServicer):
    """
    gRPC servicer that forwards requests to HTTP API.
    
    Educational Note:
        This servicer converts gRPC requests to HTTP JSON,
        calls the /generate-simple endpoint, and converts
        the JSON response back to gRPC format.
    """
    
    def GenerateSchedule(self, request, context):
        """Handles schedule generation by calling HTTP API."""
        logger.info(f"\n{'='*80}")
        logger.info(f"� gRPC REQUEST RECEIVED")
        logger.info(f"{'='*80}")
        logger.info(f"📍 User ID: {request.user_id}")
        logger.info(f"📅 Target Date: {request.target_date}")
        logger.info(f"📋 Tasks Count: {len(request.tasks)}")
        
        if request.tasks:
            for i, task in enumerate(request.tasks[:3]):
                logger.info(f"   Task {i+1}: {task.name} ({task.duration_minutes}min, priority={task.priority})")
            if len(request.tasks) > 3:
                logger.info(f"   ... and {len(request.tasks) - 3} more tasks")
        
        logger.info(f"📍 Fixed Events Count: {len(request.fixed_events)}")
        logger.info(f"👤 User Profile: MEQ={request.user_profile.meq_score}, Sleep need={request.user_profile.sleep_need}")
        
        try:
            logger.info(f"🔄 Converting gRPC request to HTTP JSON...")
            http_payload = self._convert_grpc_to_http_json(request)
            logger.info(f"✅ Payload converted: {len(str(http_payload))} bytes")
            
            logger.info(f"📡 Calling HTTP API: {HTTP_API_URL}")
            
            # Timeout musi być duży - LLM czasami czeka 40-60 sekund
            with httpx.Client(timeout=300.0) as client:
                http_response = client.post(HTTP_API_URL, json=http_payload)
                http_response.raise_for_status()
            
            response_data = http_response.json()
            logger.info(f"✅ HTTP API Response received ({len(str(response_data))} bytes)")
            logger.info(f"   📋 Response keys: {list(response_data.keys())}")
            logger.info(f"   Message: {response_data.get('message', 'N/A')[:100]}")
            
            # Debug: sprawdzenie struktury response
            if 'scheduled_tasks' in response_data:
                logger.info(f"   📊 Found 'scheduled_tasks': {len(response_data.get('scheduled_tasks', []))} items")
            if 'simplified_schedule' in response_data:
                logger.info(f"   📊 Found 'simplified_schedule': keys={list(response_data['simplified_schedule'].keys())}")
            if 'schedule' in response_data:
                logger.info(f"   📊 Found 'schedule': {len(response_data.get('schedule', []))} items")
            
            logger.info(f"🔄 Converting HTTP response to gRPC format...")
            grpc_response = self._convert_http_json_to_grpc(response_data, request.user_id)
            
            logger.info(f"✅ Schedule generation COMPLETE")
            logger.info(f"   📊 Schedule ID: {grpc_response.schedule_id}")
            logger.info(f"   ✅ Items: {len(grpc_response.scheduled_items)}")
            logger.info(f"   💬 Message: {grpc_response.message[:100]}")
            logger.info(f"{'='*80}\n")
            
            return grpc_response
            
        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP API CALL FAILED")
            logger.error(f"   Error: {type(e).__name__}: {e}")
            logger.error(f"{'='*80}\n")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"HTTP API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ SCHEDULE GENERATION FAILED")
            logger.error(f"   Error: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.error(f"{'='*80}\n")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise
    
    def _convert_grpc_to_http_json(self, request):
        """Converts gRPC request to HTTP JSON payload."""
        return {
            "user_id": request.user_id,
            "target_date": request.target_date,
            "tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority,
                    "deadline": t.deadline if t.deadline else None
                }
                for t in request.tasks
            ],
            "fixed_events": [
                {
                    "id": e.id,
                    "name": e.name,
                    "start_time": e.start_time,
                    "end_time": e.end_time
                }
                for e in request.fixed_events
            ],
            "preferences": {
                "meals": {
                    "lunch_enabled": request.preferences.meals.lunch_enabled,
                    "lunch_duration": request.preferences.meals.lunch_duration
                },
                "routines": {
                    "morning_routine_minutes": request.preferences.routines.morning_routine_minutes,
                    "evening_routine_minutes": request.preferences.routines.evening_routine_minutes
                },
                "work": {
                    "start": request.preferences.work.start,
                    "end": request.preferences.work.end,
                    "work_type": request.preferences.work.work_type if request.preferences.work.work_type else "remote",
                    "commute_minutes": request.preferences.work.commute_minutes if request.preferences.work.commute_minutes else 0
                }
            },
            "user_profile": {
                "meq_score": request.user_profile.meq_score,
                "age": request.user_profile.age,
                "sleep_need": request.user_profile.sleep_need
            }
        }
    
    def _convert_http_json_to_grpc(self, json_data, user_id):
        """Converts HTTP JSON response to gRPC response."""
        response = schedule_generation_pb2.ScheduleGenerationResponse(
            message=json_data.get("message", "Schedule generated successfully"),
            schedule_id=json_data.get("schedule_id", str(uuid4())),
            user_id=user_id
        )
        
        # API zwraca dane w polu "data"
        data = json_data.get("data", {})
        logger.info(f"   🔍 Data keys: {list(data.keys())}")
        
        # Szukaj tasks (nie scheduled_tasks!)
        scheduled_tasks = data.get("tasks", [])
        
        logger.info(f"   🔍 Extracting scheduled_tasks from data: found {len(scheduled_tasks)} items")
        
        for i, task in enumerate(scheduled_tasks):
            # Debug: inspect task structure
            if i == 0:
                logger.info(f"   🔍 Sample task keys: {list(task.keys())}")
                logger.info(f"   🔍 Sample task data: {task}")
            
            # Try multiple field names for task name
            task_name = task.get("name") or task.get("task_name") or task.get("task") or "Unknown"
            
            logger.info(f"   ✅ Task {i}: '{task_name}' from {task.get('start_time')} to {task.get('end_time')}")
            
            item = schedule_generation_pb2.ScheduledItem(
                id=str(task.get("id", "")),
                name=task_name,
                start_time=task.get("start_time", "00:00"),
                end_time=task.get("end_time", "00:00"),
                type=task.get("type", "task")
            )
            response.scheduled_items.append(item)
        
        return response


def serve():
    """Starts gRPC server that forwards to HTTP API."""
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    schedule_generation_pb2_grpc.add_ScheduleGenerationServiceServicer_to_server(
        ScheduleGenerationServicer(),
        server
    )
    
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    
    logger.info("\n" + "="*60)
    logger.info(f"🚀 gRPC Server: Listening on port {port}")
    logger.info("="*60)
    logger.info(f"📡 Forwarding requests to: {HTTP_API_URL}")
    logger.info("🔌 Press Ctrl+C to stop server\n")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down gRPC server...")
        server.stop(0)


if __name__ == "__main__":
    serve()
