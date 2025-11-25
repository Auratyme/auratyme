"""Smartwatch ingestion page (enhanced).

Enhanced interface for wearable data upload, mapping, and processing.
"""
from __future__ import annotations
import streamlit as st
import sys
import os

# Add analytics_center to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.ui import AppState, CanonicalInput
from models.enhanced_ui import WearableData
from models.wearable import WearableMapping
from services.wearable_ingest import ingest_wearable

def render(state: AppState) -> None:
    """Enhanced smartwatch data ingestion interface."""
    
    st.markdown("### 📱 Smartwatch Data Integration")
    st.info("🚧 Upload file or manually enter wearable device data for enhanced scheduling insights")
    
    # Tab selection for different input methods
    tab1, tab2 = st.tabs(["📁 Upload File", "✍️ Manual Entry"])
    
    with tab2:
        _render_manual_entry(state)
    
    with tab1:
        _render_file_upload(state)

def _render_manual_entry(state: AppState) -> None:
    """Manual data entry section for smartwatch metrics."""
    st.markdown("#### ✍️ Manual Smartwatch Data Entry")
    st.info("💡 Enter your daily health and activity metrics manually")
    
    with st.form("manual_smartwatch_entry"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**⏰ Sleep Data**")
            sleep_start = st.time_input("Sleep Start Time", value=None)
            sleep_end = st.time_input("Sleep End Time", value=None)
            sleep_quality = st.selectbox("Sleep Quality", ["Poor", "Fair", "Good", "Excellent"], index=2)
            
            st.markdown("**💪 Activity Data**")
            steps = st.number_input("Daily Steps", min_value=0, max_value=100000, value=8000)
            
        with col2:
            st.markdown("**❤️ Health Metrics**")
            heart_rate_avg = st.number_input("Average Heart Rate (bpm)", min_value=40, max_value=200, value=70)
            stress_level = st.selectbox("Stress Level", ["Low", "Moderate", "High"], index=0)
            
            st.markdown("**🎯 Wellness**")
            readiness_score = st.slider("Readiness Score", min_value=0.0, max_value=100.0, value=75.0, step=0.1)
            energy_level = st.slider("Energy Level (1-10)", min_value=1, max_value=10, value=7)
        
        date_entry = st.date_input("Date for this data", value=None)
        
        if st.form_submit_button("💾 Save Smartwatch Data", width="stretch"):
            if sleep_start and sleep_end and date_entry:
                try:
                    # Create wearable data entry
                    wearable_data = {
                        "date": str(date_entry),
                        "sleep_start": str(sleep_start),
                        "sleep_end": str(sleep_end),
                        "sleep_quality": sleep_quality,
                        "steps": steps,
                        "heart_rate_avg": heart_rate_avg,
                        "stress_level": stress_level,
                        "readiness_score": readiness_score,
                        "energy_level": energy_level
                    }
                    
                    # Initialize wearable_data list if not exists
                    if not hasattr(state, 'wearable_data') or state.wearable_data is None:
                        state.wearable_data = []
                    
                    # Add to state
                    state.wearable_data.append(wearable_data)
                    
                    st.success(f"✅ Saved smartwatch data for {date_entry}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error saving data: {e}")
            else:
                st.error("❌ Please fill in at least sleep start, sleep end, and date!")
    
    # Display saved data
    if hasattr(state, 'wearable_data') and state.wearable_data:
        st.markdown("#### 📊 Saved Smartwatch Data")
        
        import pandas as pd
        df = pd.DataFrame(state.wearable_data)
        
        if not df.empty:
            st.dataframe(
                df,
                width="stretch",
                column_config={
                    "date": "📅 Date",
                    "sleep_start": "😴 Sleep Start", 
                    "sleep_end": "🌅 Sleep End",
                    "sleep_quality": "💤 Quality",
                    "steps": "👟 Steps",
                    "heart_rate_avg": "❤️ HR Avg",
                    "stress_level": "😰 Stress",
                    "readiness_score": "🎯 Readiness",
                    "energy_level": "⚡ Energy"
                }
            )
            
            if st.button("🔄 Convert to Schedule Inputs", width="stretch"):
                _convert_wearable_to_inputs(state)

def _convert_wearable_to_inputs(state: AppState) -> None:
    """Convert wearable data to schedule input suggestions."""
    if not hasattr(state, 'wearable_data') or not state.wearable_data:
        st.warning("No wearable data to convert!")
        return
    
    try:
        # Get latest wearable entry
        latest_data = state.wearable_data[-1]
        
        # Create suggested inputs based on wearable data
        suggestions = []
        
        # Sleep block
        if latest_data.get('sleep_start') and latest_data.get('sleep_end'):
            # Convert to CanonicalInput for compatibility - ensure energy_level is within valid range
            energy_val = latest_data.get('energy_level')
            if energy_val and energy_val > 5:
                energy_val = 5  # Clamp to valid range
            
            suggestions.append(CanonicalInput(
                date=latest_data['date'],
                task_type="Sleep",
                start_time=latest_data['sleep_start'],
                end_time=latest_data['sleep_end'],
                fixed_task=True,
                sleep_quality=latest_data.get('sleep_quality'),
                energy_level=energy_val
            ))
        
        # Exercise suggestion based on steps
        steps = latest_data.get('steps', 0)
        if steps > 6000:  # If good step count, suggest exercise
            exercise_duration = min(60, max(30, steps // 200))  # 30-60 min based on steps
            # Ensure energy_level is within valid range for exercise suggestion
            energy_val = latest_data.get('energy_level')
            if energy_val and energy_val > 5:
                energy_val = 5
                
            suggestions.append(CanonicalInput(
                date=latest_data['date'],
                task_type="Exercise",
                duration=exercise_duration,
                task_priority=4 if steps > 10000 else 3,
                energy_level=energy_val
            ))
        
        # Add suggestions to current inputs - check if we're using new or old format
        # Convert to TaskForSchedule objects and add to tasks
        from models.enhanced_ui import TaskForSchedule
        for suggestion in suggestions:
            new_task = TaskForSchedule(
                title=suggestion.task_type,
                priority=min(3, max(1, 4 - (suggestion.task_priority or 3))),  # Convert 1-5 to 3-1
                duration_hours=(suggestion.duration or 60) / 60.0,
                is_fixed_time=getattr(suggestion, 'is_fixed_time', getattr(suggestion, 'fixed_task', False))
            )
            state.current_inputs.tasks.append(new_task)
        
        st.success(f"✅ Added {len(suggestions)} schedule suggestions based on your smartwatch data!")
        st.info("💡 Check the Schedule Data page to review and edit the suggested tasks.")
        
    except Exception as e:
        st.error(f"❌ Error converting wearable data: {e}")

def _render_file_upload(state: AppState) -> None:
    """File upload section (existing functionality)."""
    st.markdown("#### 📂 Data Upload")
    uploaded = st.file_uploader(
        "Upload your smartwatch data file", 
        type=["csv", "json"],
        help="Supported formats: CSV, JSON with sleep and activity data"
    )
    
    if uploaded:
        st.success(f"✅ File uploaded: **{uploaded.name}**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 File Size", f"{uploaded.size:,} bytes")
        with col2:
            st.metric("📋 File Type", uploaded.type or "Unknown")
        with col3:
            st.metric("📊 Status", "Ready to Process")
    
    # Column Mapping Configuration
    st.markdown("#### 🗺️ Column Mapping Configuration")
    st.info("💡 Map your data columns to our analytics fields for accurate processing")
    
    mapping = WearableMapping()
    
    with st.expander("🔧 Advanced Column Mapping", expanded=bool(uploaded)):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**⏰ Sleep Data Fields**")
            mapping.sleep_start = st.text_input(
                "Sleep Start Column", 
                value="sleep_start",
                help="Column containing sleep start times (e.g., '23:30')"
            )
            mapping.sleep_end = st.text_input(
                "Sleep End Column", 
                value="sleep_end",
                help="Column containing sleep end times (e.g., '07:30')"
            )
            mapping.sleep_quality = st.text_input(
                "Sleep Quality Column", 
                value="sleep_quality",
                help="Optional: Sleep quality score or rating"
            )
        
        with col2:
            st.markdown("**📊 Activity Data Fields**")
            mapping.steps = st.text_input(
                "Steps Column", 
                value="steps",
                help="Daily step count data"
            )
            mapping.heart_rate_avg = st.text_input(
                "Heart Rate Column", 
                value="heart_rate_avg",
                help="Average heart rate data"
            )
            mapping.intensity = st.text_input(
                "Activity Intensity Column", 
                value="intensity",
                help="Activity intensity or level"
            )
    
    # Processing Section
    if uploaded:
        st.markdown("#### ⚡ Data Processing")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 Process Wearable Data", type="primary", width="stretch"):
                try:
                    with st.spinner("Processing wearable data..."):
                        # Simulate processing
                        import time
                        time.sleep(1)
                        
                        result = ingest_wearable(uploaded, mapping)
                        
                        if result:
                            st.success("✅ Data processed successfully!")
                            
                            # Show processing results
                            st.markdown("**📈 Processing Results:**")
                            
                            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                            with metrics_col1:
                                st.metric("📊 Records Processed", len(result.get("processed_records", [])))
                            with metrics_col2:
                                st.metric("⚠️ Data Issues", len(result.get("warnings", [])))
                            with metrics_col3:
                                st.metric("✨ Insights Generated", len(result.get("insights", [])))
                            
                            # Show extracted features
                            if result.get("features"):
                                with st.expander("🔍 Extracted Features", expanded=True):
                                    st.json(result["features"])
                        else:
                            st.error("❌ Failed to process data. Please check your file format and column mappings.")
                            
                except Exception as e:
                    st.error(f"❌ Processing error: {str(e)}")
                    with st.expander("🐛 Error Details"):
                        st.exception(e)
        
        with col2:
            st.markdown("**🎯 Next Steps**")
            st.info("After processing, extracted insights will be available for schedule optimization.")
    
    # Integration Status
    st.markdown("#### 🔗 Integration Status")
    
    if hasattr(state, 'wearable_data') and state.wearable_data:
        st.success("✅ Wearable data integrated and ready for scheduling!")
        
        with st.expander("📊 Current Wearable Insights"):
            st.json(state.wearable_data)
            
        if st.button("🔄 Sync to Schedule Inputs", width="stretch"):
            st.info("🚧 Auto-sync feature coming soon! For now, use insights manually in the Inputs page.")
    else:
        st.warning("⏳ No wearable data processed yet. Upload and process a file to get started!")
    
    # Help Section
    with st.expander("ℹ️ Help & Examples", expanded=False):
        st.markdown("""
        **📋 Supported Data Formats:**
        - **CSV**: Comma-separated values with headers
        - **JSON**: Structured data with daily records
        
        **🔍 Expected Column Examples:**
        - `sleep_start`: "23:30", "11:45 PM"
        - `sleep_end`: "07:15", "7:15 AM"  
        - `steps`: 8542, 12000
        - `heart_rate`: 72, 85
        - `sleep_quality`: "Good", 8.5, "Poor"
        
        **💡 Tips:**
        - Ensure consistent date/time formats
        - Include at least sleep start/end times
        - More data = better scheduling insights!
        """)
    
    st.markdown("---")
    st.caption("📱 Smartwatch integration enhances AI scheduling with your personal health and activity patterns.")
