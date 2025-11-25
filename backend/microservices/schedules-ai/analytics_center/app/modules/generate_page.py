"""Generate page: builds payload and calls API client.

Displays returned schedule (simple table placeholder) and stores
request/response for downstream Explain/Diagnostics.
"""
from __future__ import annotations
import streamlit as st
import sys
import os
from uuid import uuid4
import json
import logging

# Add analytics_center to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.ui import AppState
from utils.timeline import schedule_to_rows
from utils.kpis import build_kpis
from utils.payload_builder import build_api_payload
from utils.time_validator import repair_schedule_data

try:
    from services.grpc_client import create_grpc_client, GRPC_AVAILABLE
except ImportError:
    GRPC_AVAILABLE = False

logger = logging.getLogger(__name__)


def _render_comprehensive_analytics(state: AppState, rows: list, data: dict) -> None:
    """
    Renders comprehensive analytics about the generated schedule.
    
    Educational Note:
    This function provides deep insights into schedule quality, including
    sleep calculations, energy alignment, task distribution, and optimization
    metrics to demonstrate the AI's decision-making process.
    """
    from datetime import datetime, timedelta
    
    # Calculate sleep-related metrics
    st.markdown("#### 😴 Sleep & Recovery Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Extract sleep-related tasks from schedule
    sleep_start = None
    sleep_end = None
    morning_routine_end = None
    evening_routine_start = None
    
    for row in rows:
        task_name = row.get("Task", "").lower()
        if "sleep" in task_name:
            sleep_start = row.get("Start", "")
            sleep_end = row.get("End", "")
        elif "morning routine" in task_name:
            morning_routine_end = row.get("End", "")
        elif "evening routine" in task_name:
            evening_routine_start = row.get("Start", "")
    
    # Calculate sleep duration
    sleep_duration_hours = 0
    if sleep_start and sleep_end:
        try:
            start_t = datetime.strptime(sleep_start, "%H:%M")
            end_t = datetime.strptime(sleep_end, "%H:%M")
            
            # Handle sleep crossing midnight
            if end_t <= start_t:
                end_t += timedelta(days=1)
            
            sleep_duration = (end_t - start_t).total_seconds() / 3600
            sleep_duration_hours = sleep_duration
            
            with col1:
                st.metric(
                    "💤 Sleep Duration", 
                    f"{sleep_duration_hours:.1f}h",
                    help="Total sleep time calculated from schedule"
                )
        except:
            with col1:
                st.metric("💤 Sleep Duration", "N/A")
    else:
        with col1:
            st.metric("💤 Sleep Duration", "Not scheduled")
    
    # Calculate sleep cycles (90 min each)
    if sleep_duration_hours > 0:
        sleep_cycles = sleep_duration_hours / 1.5
        with col2:
            st.metric(
                "🔄 Sleep Cycles", 
                f"{sleep_cycles:.1f}",
                delta="Optimal" if 4 <= sleep_cycles <= 6 else "Review",
                help="Number of complete 90-minute sleep cycles (optimal: 4-6 cycles)"
            )
    else:
        with col2:
            st.metric("🔄 Sleep Cycles", "N/A")
    
    # Bedtime and wake time
    with col3:
        if sleep_start:
            st.metric(
                "🌙 Bedtime", 
                sleep_start,
                help="Recommended sleep start time based on your chronotype"
            )
        else:
            st.metric("🌙 Bedtime", "N/A")
    
    with col4:
        if morning_routine_end:
            st.metric(
                "☀️ Wake Time", 
                morning_routine_end,
                help="Wake time includes morning routine completion"
            )
        elif sleep_end:
            st.metric("☀️ Wake Time", sleep_end)
        else:
            st.metric("☀️ Wake Time", "N/A")
    
    # Sleep quality explanation
    if sleep_duration_hours > 0:
        with st.expander("💡 Why This Sleep Schedule?", expanded=True):
            user_profile = state.current_inputs.user_profile if hasattr(state.current_inputs, 'user_profile') else None
            
            if user_profile:
                meq_score = user_profile.meq_score
                sleep_need = user_profile.sleep_need
                
                chronotype = "Night Owl 🦉" if meq_score < 31 else "Intermediate 🕊️" if meq_score < 70 else "Early Bird 🐦"
                
                st.markdown(f"""
                **Sleep Schedule Rationale:**
                
                - **Your Chronotype:** {chronotype} (MEQ: {meq_score})
                - **Sleep Need:** {sleep_need.title()} (~{sleep_duration_hours:.1f}h recommended)
                - **Sleep Cycles:** {sleep_cycles:.1f} complete cycles
                
                **Why These Times?**
                
                The AI scheduled your sleep based on your chronotype's natural circadian rhythm. 
                {"Night owls naturally sleep later and wake later, with peak alertness in evening hours." if meq_score < 31 else 
                 "Your intermediate chronotype allows flexibility with moderate morning and evening productivity." if meq_score < 70 else
                 "Early birds naturally wake earlier and have peak alertness in morning hours."}
                
                Your {sleep_cycles:.1f} sleep cycles provide optimal recovery through deep sleep and REM phases,
                ensuring you wake feeling refreshed and cognitively sharp.
                """)
            else:
                st.markdown(f"""
                **Sleep Duration:** {sleep_duration_hours:.1f} hours ({sleep_cycles:.1f} complete 90-minute cycles)
                
                This duration allows for proper progression through all sleep stages including deep sleep and REM,
                which are critical for physical recovery, memory consolidation, and cognitive function.
                """)
    
    st.markdown("---")
    st.markdown("#### ⚡ Energy & Productivity Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate task distribution
    total_tasks = len([r for r in rows if r.get("Task", "") not in ["Sleep", "Morning Routine", "Evening Routine", "Lunch", "Commute to School/Work", "Commute from School/Work", "School/Work"]])
    fixed_tasks = len([r for r in rows if "fixed" in r.get("Task", "").lower() or r.get("Task", "") in ["School/Work", "1:1 with Manager"]])
    flexible_tasks = total_tasks - fixed_tasks
    
    # Calculate work hours
    work_hours = 0
    for row in rows:
        task_name = row.get("Task", "")
        if task_name not in ["Sleep", "Morning Routine", "Evening Routine", "Lunch", "Commute to School/Work", "Commute from School/Work"]:
            minutes = row.get("Minutes", 0)
            work_hours += minutes / 60
    
    with col1:
        st.metric(
            "📝 Total Tasks", 
            total_tasks,
            help="Number of tasks scheduled (excluding routines)"
        )
    
    with col2:
        st.metric(
            "⏱️ Productive Hours", 
            f"{work_hours:.1f}h",
            help="Total time allocated to tasks and work"
        )
    
    with col3:
        if work_hours > 0:
            efficiency = min(100, (work_hours / 8) * 100)
            st.metric(
                "⚙️ Schedule Efficiency", 
                f"{efficiency:.0f}%",
                delta="Optimal" if 70 <= efficiency <= 90 else "Review",
                help="How efficiently the schedule uses available time"
            )
        else:
            st.metric("⚙️ Schedule Efficiency", "N/A")
    
    with col4:
        if total_tasks > 0:
            flexibility_ratio = (flexible_tasks / total_tasks) * 100
            st.metric(
                "🔄 Flexibility", 
                f"{flexibility_ratio:.0f}%",
                delta="Good" if flexibility_ratio >= 50 else "Limited",
                help="Percentage of tasks that can be rescheduled if needed"
            )
        else:
            st.metric("🔄 Flexibility", "N/A")
    
    # Task breakdown
    st.markdown("---")
    st.markdown("#### 📊 Task Distribution & Timing")
    
    # Group tasks by category
    work_tasks = []
    personal_tasks = []
    routine_tasks = []
    
    for row in rows:
        task_name = row.get("Task", "")
        if task_name in ["Morning Routine", "Evening Routine", "Lunch", "Sleep", "Commute to School/Work", "Commute from School/Work"]:
            routine_tasks.append(row)
        elif task_name == "School/Work" or "work" in task_name.lower() or "meeting" in task_name.lower():
            work_tasks.append(row)
        else:
            personal_tasks.append(row)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💼 Work Tasks**")
        if work_tasks:
            for task in work_tasks:
                st.caption(f"🕐 {task['Start']}-{task['End']}: {task['Task']}")
        else:
            st.caption("No work tasks")
    
    with col2:
        st.markdown("**🎯 Personal Tasks**")
        if personal_tasks:
            for task in personal_tasks:
                st.caption(f"🕐 {task['Start']}-{task['End']}: {task['Task']}")
        else:
            st.caption("No personal tasks")
    
    with col3:
        st.markdown("**🔄 Routines & Breaks**")
        if routine_tasks:
            for task in routine_tasks:
                st.caption(f"🕐 {task['Start']}-{task['End']}: {task['Task']}")
        else:
            st.caption("No routines")
    
    # Energy alignment explanation
    st.markdown("---")
    with st.expander("🧠 AI Scheduling Intelligence", expanded=True):
        user_profile = state.current_inputs.user_profile if hasattr(state.current_inputs, 'user_profile') else None
        
        if user_profile:
            meq_score = user_profile.meq_score
            chronotype = "Night Owl 🦉" if meq_score < 31 else "Intermediate 🕊️" if meq_score < 70 else "Early Bird 🐦"
            
            st.markdown(f"""
            **How the AI Optimized Your Schedule:**
            
            1. **Chronotype-Aware Scheduling** ({chronotype})
               - Your MEQ score ({meq_score}) indicates your natural energy patterns
               - {"Peak performance hours: 17:00-22:00 (evening)" if meq_score < 31 else 
                  "Peak performance hours: 10:00-16:00 (midday)" if meq_score < 70 else
                  "Peak performance hours: 08:00-12:00 (morning)"}
               - High-priority tasks scheduled during your peak energy windows
            
            2. **Task Priority Optimization**
               - Priority 1-2 (High): Scheduled during peak energy hours
               - Priority 3 (Medium): Placed in moderate energy periods
               - Priority 4-5 (Low): Assigned to off-peak times or recovery periods
            
            3. **Break & Recovery Integration**
               - Lunch scheduled around midday for energy restoration
               - Commute times buffer work/home transitions
               - Evening routine allows proper wind-down before sleep
            
            4. **Work-Life Balance**
               - Fixed commitments (school/work, meetings) preserved
               - Flexible tasks optimally distributed around constraints
               - Sleep duration matches your stated needs ({user_profile.sleep_need})
            
            **Result:** A schedule that works *with* your biology, not against it, maximizing
            productivity while preventing burnout through strategic task placement and adequate recovery time.
            """)
        else:
            st.markdown("""
            **AI Scheduling Principles Applied:**
            
            - Energy-aware task placement for optimal cognitive performance
            - Priority-based scheduling during peak productive hours
            - Strategic break placement for sustained focus
            - Work-life balance through routine integration
            - Sleep optimization for proper recovery
            """)


def render(state: AppState) -> None:
    """Enhanced schedule generation interface with SSE streaming."""
    
    st.markdown("### 🚀 Generate AI Schedule")
    
    # Check prerequisites
    if not state.current_inputs.tasks:
        st.warning("📝 No tasks found! Please add some tasks in the **Inputs** page first.")
        if st.button("➡️ Go to Inputs Page"):
            st.info("Use the navigation sidebar to go to the Inputs page.")
        return
    
    # Show current configuration overview
    st.markdown("#### 📊 Current Configuration")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Total Tasks", len(state.current_inputs.tasks))
    with col2:
        fixed_count = sum(1 for t in state.current_inputs.tasks if t.is_fixed_time)
        st.metric("📌 Fixed Tasks", fixed_count)
    with col3:
        total_duration = sum(t.duration_hours * 60 for t in state.current_inputs.tasks)
        st.metric("⏱️ Total Duration", f"{int(total_duration)}min")
    with col4:
        st.metric("🔥 Prime Windows", len(state.prime_windows))
    
    # Generation controls
    st.markdown("---")
    st.markdown("### ⚡ Generate Your Personalized Schedule")
    st.markdown("Click below to start AI-powered schedule generation with real-time progress updates")
    
    if st.button("🚀 GENERATE AI SCHEDULE", type="primary", use_container_width=True, 
                 help="Start intelligent schedule generation with real-time SSE streaming"):
            try:
                payload = build_api_payload(state)
                state.last_request = payload
                
                # Show what we're sending
                with st.expander("📤 Request Payload Preview"):
                    st.json(payload)
                
                # SSE MODE - Real-time generation
                logger.info("=" * 80)
                logger.info("🚀 STARTING REAL-TIME AI SCHEDULE GENERATION")
                logger.info("=" * 80)
                
                import time
                import requests
                import json
                
                start_time = time.time()
                
                # Step 1: Start generation (POST)
                st.info("📤 Submitting your schedule request to AI engine...")
                response = requests.post(
                    f"{state.api_base_url}/v1/schedule/generate-simple",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 202:
                    raise Exception(f"API returned status {response.status_code}: {response.text}")
                
                result = response.json()
                job_id = result.get("job_id")
                
                if not job_id:
                    raise Exception("No job_id returned from API")
                
                logger.info(f"✅ Job created: {job_id}")
                st.success(f"✅ Generation started successfully! Job ID: `{job_id}`")
                
                # Step 2: Stream SSE updates with enhanced UI
                st.markdown("---")
                st.markdown("#### 🔄 Real-Time Generation Progress")
                st.markdown("*Watch your schedule being created in real-time by AI*")
                
                progress_bar = st.progress(0, text="🎯 Initializing AI engine...")
                status_container = st.container()
                
                with status_container:
                    col1, col2, col3 = st.columns(3)
                    metric_status = col1.empty()
                    metric_progress = col2.empty()
                    metric_time = col3.empty()
                
                final_result = None
                
                with requests.get(
                    f"{state.api_base_url}/v1/schedule/status/{job_id}",
                    stream=True,
                    headers={"Accept": "text/event-stream"}
                ) as sse_stream:
                    
                    if sse_stream.status_code != 200:
                        raise Exception(f"SSE stream error: {sse_stream.status_code}")
                    
                    for line in sse_stream.iter_lines():
                        if not line:
                            continue
                        
                        if line.startswith(b'data: '):
                            data = json.loads(line[6:])
                            
                            status = data.get("status")
                            progress = data.get("progress", 0)
                            elapsed = int(time.time() - start_time)
                            
                            # Map status to friendly display
                            status_emoji = {
                                "pending": "⏳",
                                "generating": "🤖",
                                "optimizing": "⚡",
                                "finalizing": "✨",
                                "complete": "✅"
                            }.get(status, "🔄")
                            
                            status_display = status.replace("_", " ").title()
                            
                            # Update UI with enhanced visuals
                            progress_bar.progress(
                                progress / 100, 
                                text=f"{status_emoji} {status_display}... {progress}%"
                            )
                            
                            metric_status.metric("Status", f"{status_emoji} {status_display}")
                            metric_progress.metric("Progress", f"{progress}%")
                            metric_time.metric("Elapsed", f"{elapsed}s")
                            
                            logger.info(f"📊 SSE Event: status={status}, progress={progress}%, elapsed={elapsed}s")
                            
                            # Check if complete
                            if status == "complete":
                                final_result = data.get("result")
                                logger.info(f"✅ Generation complete!")
                                break
                            elif status == "failed":
                                error = data.get("error", "Unknown error")
                                raise Exception(f"Generation failed: {error}")
                
                end_time = time.time()
                state.last_latency_ms = int((end_time - start_time) * 1000)
                
                progress_bar.empty()
                status_container.empty()
                
                if not final_result:
                    raise Exception("No result received from SSE stream")
                
                # Store response
                state.last_response = final_result
                
                logger.info(f"✅ Schedule generated via SSE in {state.last_latency_ms}ms")
                
                st.markdown("---")
                st.success(f"🎉 Schedule generated successfully in {state.last_latency_ms}ms!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Generation failed: {str(e)}")
                with st.expander("🐛 Error Details"):
                    st.exception(e)
    
    st.markdown("---")
    st.markdown("**💡 Tips for Better Results**")
    st.info("""
    - Add more task details for smarter scheduling
    - Set realistic task durations
    - Mark time-sensitive tasks as "Fixed Time"
    - Configure your chronotype for energy-aware scheduling
    """)
    
    # Show generated schedule
    if state.last_response:
        st.markdown("---")
        st.markdown("### 📅 Generated Schedule")
        
        data = state.last_response.get("data", {})
        
        logger.info(f"🔍 DEBUG generate_page: state.last_response keys = {list(state.last_response.keys())}")
        logger.info(f"🔍 DEBUG generate_page: data keys = {list(data.keys()) if isinstance(data, dict) else 'NOT_DICT'}")
        logger.info(f"🔍 DEBUG generate_page: data type = {type(data)}")
        if isinstance(data, dict) and 'tasks' in data:
            logger.info(f"🔍 DEBUG generate_page: data['tasks'] type = {type(data['tasks'])}, length = {len(data['tasks']) if isinstance(data['tasks'], list) else 'NOT_LIST'}")
            if isinstance(data['tasks'], list) and len(data['tasks']) > 0:
                logger.info(f"🔍 DEBUG generate_page: First task keys = {list(data['tasks'][0].keys())}")
                logger.info(f"🔍 DEBUG generate_page: First task = {data['tasks'][0]}")
        
        if data:
            # Ensure data is a dict and has proper structure
            if not isinstance(data, dict):
                logger.error(f"⚠️ Data is not a dict, type={type(data)}")
                st.error(f"❌ Invalid response format: data is {type(data).__name__}, expected dict")
                return
            
            # Repair data if needed
            data = repair_schedule_data(data)
            logger.info(f"🔧 Repaired data: {len(data.get('tasks', []))} tasks")
            
            if not data.get('tasks'):
                logger.warning("⚠️ No tasks in data after repair")
                st.warning("⚠️ No tasks found in response after repair")
                with st.expander("🔍 Raw Response Data"):
                    st.json(state.last_response)
                return
            
            # Schedule overview
            st.success("🎉 Your personalized schedule is ready!")
            
            # Convert to displayable format
            rows = schedule_to_rows(data)
            
            logger.info(f"🔍 DEBUG generate_page: schedule_to_rows returned {len(rows)} rows")
            
            if rows:
                # Display beautiful schedule timeline
                st.markdown("#### 📋 Your Personalized Schedule")
                
                # Create beautiful schedule cards
                st.markdown('<div class="schedule-table">', unsafe_allow_html=True)
                
                for row in rows:
                    task_name = row.get("Task", "")
                    start_time = row.get("Start", "")
                    end_time = row.get("End", "")
                    duration = row.get("Minutes", 0)
                    
                    # Choose emoji based on task type
                    if "Sleep" in task_name:
                        emoji = "😴"
                        color = "#667eea"
                    elif "Morning Routine" in task_name:
                        emoji = "🌅"
                        color = "#f093fb"
                    elif "Evening Routine" in task_name:
                        emoji = "🌙"
                        color = "#4facfe"
                    elif "Work" in task_name or "School" in task_name:
                        emoji = "💼"
                        color = "#43e97b"
                    elif "Lunch" in task_name:
                        emoji = "🍽️"
                        color = "#fa709a"
                    elif "Commute" in task_name:
                        emoji = "🚗"
                        color = "#30cfd0"
                    elif "Meeting" in task_name or "1:1" in task_name:
                        emoji = "👥"
                        color = "#a8edea"
                    else:
                        emoji = "📝"
                        color = "#667eea"
                    
                    st.markdown(f"""
                    <div class="schedule-row" style="border-left-color: {color};">
                        <span class="schedule-time">{emoji} {start_time} - {end_time}</span>
                        <span style="color: #666; margin: 0 0.5rem;">•</span>
                        <span class="schedule-task">{task_name}</span>
                        <span style="color: #666; margin: 0 0.5rem;">•</span>
                        <span style="color: #888; font-size: 0.9rem;">{duration}min</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # KPIs and analytics
                st.markdown("---")
                st.markdown("### 📊 Comprehensive Schedule Analytics")
                
                _render_comprehensive_analytics(state, rows, data)
                
                # Export options
                st.markdown("---")
                st.markdown("#### 💾 Export Options")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    request_json = json.dumps(state.last_request or {}, indent=2)
                    st.download_button(
                        "📤 Download Request",
                        data=request_json,
                        file_name="schedule_request.json",
                        mime="application/json",
                        width="stretch"
                    )
                
                with col2:
                    response_json = json.dumps(state.last_response or {}, indent=2)
                    st.download_button(
                        "📨 Download Response",
                        data=response_json,
                        file_name="schedule_response.json",
                        mime="application/json",
                        width="stretch"
                    )
                
                with col3:
                    csv_data = "Task,Start,End,Minutes\n" + "\n".join([
                        f"{r['Task']},{r['Start']},{r['End']},{r['Minutes']}" for r in rows
                    ])
                    st.download_button(
                        "📊 Download CSV",
                        data=csv_data,
                        file_name="generated_schedule.csv",
                        mime="text/csv",
                        width="stretch"
                    )
            
            else:
                st.warning("⚠️ Schedule generated but no displayable tasks found.")
                with st.expander("🔍 Raw Response Data"):
                    st.json(data)
        
        else:
            st.error("❌ No schedule data received from API.")
            if state.last_response:
                with st.expander("🔍 Full Response"):
                    st.json(state.last_response)
    
    # Instructions for new users
    else:
        st.markdown("---")
        st.markdown("### 🎯 Getting Started")
        st.info("""
        **Ready to generate your first AI schedule?**
        
        1. ✅ Add your tasks in the **Inputs** page
        2. ⚙️ Configure your preferences in the sidebar  
        3. 🚀 Click **Create AI Schedule** above
        4. 📊 Review and export your optimized schedule
        """)
    
    st.markdown("---")
    st.caption("🤖 AI-powered scheduling considers your preferences, energy patterns, and task priorities for optimal productivity.")
