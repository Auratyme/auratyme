"""Enhanced inputs page with separated data sections.

Educational Rationale:
This redesign separates user-provided data from algorithm-computed data,
making it clear what the user controls vs. what the system computes.
Each section has a specific responsibility and validation rules.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
import sys
import os

# Add analytics_center to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.enhanced_ui import AppState, UserProfileData, TaskForSchedule, WearableData
from utils.sample_data_generator import generate_sample_user_profile, generate_sample_tasks, generate_sample_wearable_data, generate_sample_algorithm_results

def render(state: AppState) -> None:
    """Render the reorganized inputs interface with separated sections."""
    
    st.title("📊 Schedule Input Data")
    st.markdown("Configure your profile, tasks, and wearable data for optimal AI schedule generation.")
    
    # Prominent sample data button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 LOAD SAMPLE DATA", type="primary", use_container_width=True, 
                     help="Load complete sample dataset for competition demo"):
            _fill_complete_sample_data(state)
            st.success("✨ Sample data loaded successfully!")
            st.rerun()
    st.markdown("---")
    
    # Create tabs for different data sections
    tab1, tab2, tab3 = st.tabs([
        "👤 User Profile", 
        "📋 Tasks & Events",
        "⌚ Wearable Data"
    ])
    
    with tab1:
        _render_user_profile_section(state)
    
    with tab2:
        _render_tasks_section(state)
    
    with tab3:
        _render_wearable_section(state)


def _fill_complete_sample_data(state: AppState) -> None:
    """
    Fills complete sample data matching the competition demo format.
    
    Educational Note:
    Pre-configured sample data demonstrates the system's capabilities
    with realistic, well-structured inputs that showcase optimal usage.
    """
    from datetime import date
    
    state.current_inputs.user_profile = UserProfileData(
        name="Alex Johnson",
        age=30,
        role="Software Engineer",
        industry="Tech",
        meq_score=50,
        sleep_need="medium",
        start_time="08:00",
        end_time="16:00",
        commute_minutes=30,
        location="Office",
        type="office",
        lunch_duration_minutes=45,
        morning_duration_minutes=30,
        evening_duration_minutes=45
    )
    
    state.current_inputs.tasks = [
        TaskForSchedule(
            title="Code Review",
            priority=2,
            duration_hours=50/60,
            is_fixed_time=False
        ),
        TaskForSchedule(
            title="Documentation",
            priority=2,
            duration_hours=110/60,
            is_fixed_time=False
        ),
        TaskForSchedule(
            title="Bug Fix",
            priority=4,
            duration_hours=50/60,
            is_fixed_time=False
        ),
        TaskForSchedule(
            title="1:1 with Manager",
            priority=1,
            duration_hours=20/60,
            is_fixed_time=True,
            start_time="19:00",
            end_time="19:20"
        )
    ]
    
    state.current_inputs.wearable_data = WearableData(
        sleep_quality="Good",
        stress_level="Low",
        readiness_score=0.85,
        steps_yesterday=8500,
        avg_heart_rate=68,
        sleep_duration_hours=7.5,
        deep_sleep_percentage=22,
        rem_sleep_percentage=25,
        recovery_index=78
    )
    
    state.current_inputs.target_date = date.today().isoformat()


def _render_user_profile_section(state: AppState) -> None:
    """Render user profile and preferences section with enhanced styling."""
    st.header("👤 User Profile & Preferences")
    st.markdown("*Configure your personal information and daily preferences for optimal schedule generation.*")
    st.markdown("---")
    
    profile = state.current_inputs.user_profile
    
    # Basic Profile Information
    with st.expander("📝 Basic Information", expanded=True):
        st.markdown("**Personal details that influence schedule optimization.**")
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input(
                "👤 Full Name", 
                value=profile.name, 
                key="profile_name",
                help="Your full name for personalized schedule"
            )
            new_age = st.number_input(
                "🎂 Age", 
                min_value=16, 
                max_value=100, 
                value=profile.age, 
                key="profile_age",
                help="Age affects energy patterns and recovery needs"
            )
            new_industry = st.text_input(
                "🏢 Industry", 
                value=profile.industry, 
                key="profile_industry",
                help="Your professional field (Tech, Healthcare, Finance, etc.)"
            )
            
        with col2:
            new_meq = st.slider(
                "🌅 Chronotype (MEQ Score)", 
                min_value=16, 
                max_value=86, 
                value=profile.meq_score, 
                help="**16-30:** Night Owl 🦉 | **31-69:** Intermediate 🕊️ | **70-86:** Early Bird 🐦\n\nDetermines your natural peak performance hours", 
                key="profile_meq"
            )
            
            chronotype_label = "🦉 Night Owl" if new_meq < 31 else "🕊️ Intermediate" if new_meq < 70 else "🐦 Early Bird"
            st.info(f"**Detected: {chronotype_label}**")
            
            new_sleep_need = st.selectbox(
                "😴 Sleep Need", 
                options=["low", "medium", "high"],
                index=["low", "medium", "high"].index(profile.sleep_need if hasattr(profile, 'sleep_need') and profile.sleep_need in ["low", "medium", "high"] else "medium"),
                help="**Low:** 4 cycles (~6h) | **Medium:** 5 cycles (~7.5h) | **High:** 6 cycles (~9h)\n\nBased on sleep cycle research for optimal recovery",
                key="sleep_need"
            )
    
    # Work Preferences
    with st.expander("💼 Work Preferences", expanded=True):
        st.markdown("**Define your work schedule and environment for accurate planning.**")
        col1, col2 = st.columns(2)
        
        with col1:
            new_start_time = st.time_input(
                "🕐 Work Start Time", 
                value=pd.to_datetime(profile.start_time, format='%H:%M').time(), 
                key="work_start",
                help="When your workday typically begins"
            )
            new_end_time = st.time_input(
                "🕑 Work End Time", 
                value=pd.to_datetime(profile.end_time, format='%H:%M').time(), 
                key="work_end",
                help="When your workday typically ends"
            )
            
        with col2:
            new_type = st.selectbox(
                "🏠 Work Type", 
                ["office", "hybrid", "remote"], 
                index=["office", "hybrid", "remote"].index(profile.type), 
                key="work_type",
                help="**Office:** On-site work | **Hybrid:** Mix of office/remote | **Remote:** Work from home"
            )
            new_commute = st.number_input(
                "🚗 Commute Duration (minutes)", 
                min_value=0, 
                max_value=180,
                value=profile.commute_minutes, 
                key="commute",
                help="One-way commute time (applies to office and hybrid work)"
            )
    
    # Meal Preferences  
    with st.expander("🍽️ Meal Preferences", expanded=True):
        st.info("ℹ️ Lunch is scheduled separately. Breakfast/Dinner are included in Morning/Evening Routines.")
        
        st.subheader("� Lunch")
        new_lunch_duration = st.number_input(
            "Duration (minutes)", 
            min_value=15, 
            max_value=120,
            value=profile.lunch_duration_minutes, 
            key="lunch_duration",
            help="Lunch will be scheduled around 12:30 based on availability and your preferences"
        )
    
    # Routines
    with st.expander("🔄 Daily Routines", expanded=True):
        st.markdown("**Morning and evening routines that bookend your productive day.**")
        st.info("ℹ️ **Morning Routine** includes breakfast, hygiene, getting ready. **Evening Routine** includes dinner, wind-down activities, and sleep preparation.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_morning_duration = st.number_input(
                "🌅 Morning Routine Duration (minutes)", 
                min_value=10, 
                max_value=120,
                value=profile.morning_duration_minutes, 
                key="morning_duration",
                help="Time needed for breakfast, hygiene, getting ready for the day"
            )
            st.caption("💡 *Typical: 30-60 minutes*")
        
        with col2:
            new_evening_duration = st.number_input(
                "🌙 Evening Routine Duration (minutes)", 
                min_value=10, 
                max_value=120,
                value=profile.evening_duration_minutes, 
                key="evening_duration",
                help="Time for dinner, relaxation, and preparing for quality sleep"
            )
            st.caption("💡 *Typical: 45-90 minutes*")
    
    # Update profile data
    if st.button("💾 Update Profile", type="primary", use_container_width=True):
        state.current_inputs.user_profile = UserProfileData(
            name=new_name,
            age=new_age,
            role=profile.role,
            industry=new_industry,
            meq_score=new_meq,
            sleep_need=new_sleep_need,
            start_time=new_start_time.strftime('%H:%M'),
            end_time=new_end_time.strftime('%H:%M'),
            commute_minutes=new_commute,
            location=profile.location,
            type=new_type,
            lunch_duration_minutes=new_lunch_duration,
            morning_duration_minutes=new_morning_duration,
            evening_duration_minutes=new_evening_duration
        )
        st.success("✅ Profile updated successfully!")
        st.rerun()

def _render_tasks_section(state: AppState) -> None:
    """Render tasks and events section with enhanced UI."""
    st.header("📋 Tasks & Events for Scheduling")
    st.markdown("*Add tasks that need to be scheduled. The AI will find optimal times based on your profile and energy patterns.*")
    st.markdown("---")
    
    # Target date selection
    col_date, col_info = st.columns([1, 2])
    with col_date:
        from datetime import date, timedelta
        today = date.today()
        
        # Safely parse the current target_date, fallback to today if invalid
        try:
            current_date = date.fromisoformat(state.current_inputs.target_date) if state.current_inputs.target_date else today
            # Ensure the current date is within valid range
            if current_date < today:
                current_date = today
            elif current_date > today + timedelta(days=365):
                current_date = today + timedelta(days=365)
        except (ValueError, TypeError):
            current_date = today
            
        target_date = st.date_input(
            "🗓️ Target Date",
            value=current_date,
            min_value=today,
            max_value=today + timedelta(days=365),
            help="Select the date for schedule generation"
        )
        state.current_inputs.target_date = target_date.isoformat()
    
    with col_info:
        st.info(f"📅 Scheduling tasks for: **{target_date.strftime('%A, %B %d, %Y')}**")
    
    st.divider()
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add Task", width="stretch"):
            state.current_inputs.tasks.append(TaskForSchedule(
                title="New Task",
                priority=2,
                duration_hours=1.0,
                is_fixed_time=False
            ))
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All Tasks", width="stretch", type="secondary"):
            if st.session_state.get("confirm_clear_tasks", False):
                state.current_inputs.tasks = []
                st.session_state["confirm_clear_tasks"] = False
                st.success("Tasks cleared!")
                st.rerun()
            else:
                st.session_state["confirm_clear_tasks"] = True
                st.warning("Click again to confirm!")
    
    if not state.current_inputs.tasks:
        st.info("👋 No tasks yet! Add your first task above.")
        return
    
    # Convert to DataFrame for editing
    tasks_data = []
    for i, task in enumerate(state.current_inputs.tasks):
        total_minutes = int(task.duration_hours * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if hours > 0 and minutes > 0:
            duration_display = f"{hours}h {minutes}m"
        elif hours > 0:
            duration_display = f"{hours}h"
        else:
            duration_display = f"{minutes}m"
        
        tasks_data.append({
            "index": i,
            "title": task.title,
            "priority": task.priority,
            "duration_display": duration_display,
            "duration_hours": task.duration_hours,
            "is_fixed_time": task.is_fixed_time,
            "start_time": task.start_time if hasattr(task, 'start_time') else "",
            "end_time": task.end_time if hasattr(task, 'end_time') else ""
        })
    
    df = pd.DataFrame(tasks_data)
    
    # Configure columns for editing
    column_config = {
        "index": None,  # Hide index
        "title": st.column_config.TextColumn("📝 Task Title", width="large"),
        "priority": st.column_config.SelectboxColumn("⭐ Priority", 
                                                   options=[1, 2, 3, 4, 5], 
                                                   help="1=Highest, 2=High, 3=Medium, 4=Low, 5=Lowest"),
        "duration_display": st.column_config.TextColumn("⏱️ Duration", 
                                                       width="small",
                                                       help="Time in hours and minutes"),
        "duration_hours": None,  # Hidden - used internally only
        "is_fixed_time": st.column_config.CheckboxColumn("📌 Fixed Time", 
                                                        help="Cannot be rescheduled"),
        "start_time": st.column_config.TextColumn("🕐 Start Time",
                                                help="Required for fixed-time tasks (HH:MM format)"),
        "end_time": st.column_config.TextColumn("🕐 End Time", 
                                              help="Required for fixed-time tasks (HH:MM format)")
    }
    
    # Show editable table
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        num_rows="dynamic",
        width="stretch",
        key="tasks_editor",
        height=300
    )
    
    # Update tasks from edited data
    try:
        new_tasks = []
        validation_errors = []
        
        for idx, row in edited_df.iterrows():
            if pd.notna(row['title']) and row['title'].strip():  # Only add non-empty tasks
                is_fixed = bool(row['is_fixed_time'])
                start_time = None
                end_time = None
                
                if is_fixed:
                    if pd.notna(row.get('start_time')) and str(row['start_time']).strip():
                        start_time = str(row['start_time'])
                    else:
                        validation_errors.append(f"Task '{row['title']}': Fixed Time requires Start Time")
                    
                    if pd.notna(row.get('end_time')) and str(row['end_time']).strip():
                        end_time = str(row['end_time'])
                    else:
                        validation_errors.append(f"Task '{row['title']}': Fixed Time requires End Time")
                else:
                    if pd.notna(row.get('start_time')) and str(row['start_time']).strip():
                        validation_errors.append(f"Task '{row['title']}': Start Time only allowed for Fixed Time tasks")
                    if pd.notna(row.get('end_time')) and str(row['end_time']).strip():
                        validation_errors.append(f"Task '{row['title']}': End Time only allowed for Fixed Time tasks")
                
                new_tasks.append(TaskForSchedule(
                    title=row['title'],
                    priority=int(row['priority']),
                    duration_hours=float(row['duration_hours']),
                    is_fixed_time=is_fixed,
                    start_time=start_time,
                    end_time=end_time
                ))
        
        if validation_errors:
            for error in validation_errors:
                st.warning(f"⚠️ {error}")
        
        state.current_inputs.tasks = new_tasks
        
        # Show summary
        if new_tasks:
            total_minutes = sum(int(task.duration_hours * 60) for task in new_tasks)
            total_hours = total_minutes // 60
            remaining_minutes = total_minutes % 60
            fixed_count = sum(1 for task in new_tasks if task.is_fixed_time)
            
            if total_hours > 0 and remaining_minutes > 0:
                total_time_display = f"{total_hours}h {remaining_minutes}m"
            elif total_hours > 0:
                total_time_display = f"{total_hours}h"
            else:
                total_time_display = f"{remaining_minutes}m"
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tasks", len(new_tasks))
            with col2:
                st.metric("Total Time", total_time_display)
            with col3:
                st.metric("Fixed Tasks", fixed_count)
        
    except Exception as e:
        st.error(f"❌ Error processing tasks: {str(e)}")


def _render_wearable_section(state: AppState) -> None:
    """
    Render wearable data section with enhanced styling.
    
    Educational Note:
    Wearable data provides physiological insights that enhance schedule
    optimization by considering actual sleep quality, recovery state,
    and activity patterns for more personalized recommendations.
    """
    st.header("⌚ Wearable Device Data")
    st.markdown("*Data from your smartwatch or fitness tracker to optimize schedule based on your physical state.*")
    st.markdown("---")
    
    wearable = state.current_inputs.wearable_data or WearableData()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("😴 Sleep Metrics")
        st.markdown("**Last night's sleep quality indicators**")
        
        new_sleep_quality = st.selectbox(
            "Sleep Quality", 
            ["Poor", "Fair", "Good", "Excellent"],
            index=["Poor", "Fair", "Good", "Excellent"].index(wearable.sleep_quality),
            key="sleep_quality",
            help="Overall subjective or device-measured sleep quality"
        )
        
        new_sleep_duration = st.number_input(
            "Sleep Duration (hours)", 
            min_value=3.0, 
            max_value=12.0,
            value=wearable.sleep_duration_hours, 
            step=0.5, 
            key="sleep_duration",
            help="Total time spent sleeping last night"
        )
        
        new_deep_sleep = st.slider(
            "Deep Sleep %", 
            0, 100, 
            wearable.deep_sleep_percentage, 
            key="deep_sleep",
            help="Percentage of total sleep in deep/slow-wave sleep stage (optimal: 15-25%)"
        )
        
        new_rem_sleep = st.slider(
            "REM Sleep %", 
            0, 100, 
            wearable.rem_sleep_percentage, 
            key="rem_sleep",
            help="Percentage of total sleep in REM stage (optimal: 20-25%)"
        )
        
        # Sleep quality indicator
        if new_sleep_quality == "Excellent" and new_sleep_duration >= 7:
            st.success("💚 Excellent recovery - optimal for high-performance tasks")
        elif new_sleep_quality == "Good":
            st.info("💙 Good recovery - ready for productive work")
        elif new_sleep_quality == "Fair":
            st.warning("💛 Moderate recovery - consider lighter task load")
        else:
            st.error("❤️ Poor recovery - prioritize rest and essential tasks only")
    
    with col2:
        st.subheader("💪 Activity & Health")
        st.markdown("**Physical activity and health indicators**")
        
        new_steps = st.number_input(
            "Steps Yesterday", 
            min_value=0, 
            max_value=50000,
            value=wearable.steps_yesterday, 
            key="steps",
            help="Total steps taken yesterday (target: 8,000-10,000)"
        )
        
        new_heart_rate = st.number_input(
            "Avg Resting Heart Rate (bpm)", 
            min_value=40, 
            max_value=200,
            value=wearable.avg_heart_rate, 
            key="heart_rate",
            help="Average resting heart rate (lower generally indicates better fitness)"
        )
        
        new_stress_level = st.selectbox(
            "Stress Level",
            ["Very Low", "Low", "Moderate", "High", "Very High"],
            index=["Very Low", "Low", "Moderate", "High", "Very High"].index(wearable.stress_level),
            key="stress_level",
            help="Current stress level from HRV or self-assessment"
        )
        
        new_readiness = st.slider(
            "Readiness Score", 
            0.0, 1.0, 
            wearable.readiness_score, 
            step=0.05, 
            key="readiness",
            help="Overall readiness for physical and mental performance (0-1 scale)"
        )
        
        new_recovery = st.slider(
            "Recovery Index %", 
            0, 100, 
            wearable.recovery_index, 
            key="recovery",
            help="Recovery from previous day's activities (100% = fully recovered)"
        )
        
        # Activity indicator
        if new_steps >= 10000:
            st.success("🎯 Great activity level!")
        elif new_steps >= 7000:
            st.info("👍 Good activity level")
        else:
            st.warning("🚶 Consider adding more movement")
    
    st.markdown("---")
    
    if st.button("💾 Update Wearable Data", type="primary", use_container_width=True):
        state.current_inputs.wearable_data = WearableData(
            sleep_quality=new_sleep_quality,
            stress_level=new_stress_level,
            readiness_score=new_readiness,
            steps_yesterday=new_steps,
            avg_heart_rate=new_heart_rate,
            sleep_duration_hours=new_sleep_duration,
            deep_sleep_percentage=new_deep_sleep,
            rem_sleep_percentage=new_rem_sleep,
            recovery_index=new_recovery
        )
        st.success("✅ Wearable data updated successfully!")
        st.rerun()
    
    # Educational info box
    with st.expander("💡 How Wearable Data Improves Scheduling", expanded=False):
        st.markdown("""
        **Why We Use Wearable Data:**
        
        1. **Sleep Quality** → Adjusts task difficulty and cognitive load
           - Poor sleep = lighter, less demanding tasks
           - Excellent sleep = complex, high-priority tasks
        
        2. **Recovery & Readiness** → Determines optimal work intensity
           - Low recovery = more breaks, shorter focus blocks
           - High recovery = longer focus sessions, challenging work
        
        3. **Stress Levels** → Influences task scheduling
           - High stress = avoid back-to-back meetings, add buffer time
           - Low stress = can handle denser schedule
        
        4. **Activity Patterns** → Suggests movement integration
           - Low steps = schedule walking breaks, standing tasks
           - High activity = adequate rest periods
        
        **Result:** A schedule that adapts to your actual physical and mental state,
        not just your calendar preferences, maximizing productivity while preventing burnout.
        """)
