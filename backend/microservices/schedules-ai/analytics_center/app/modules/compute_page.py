"""Enhanced algorithm integration for generating computed insights.

Educational Rationale:
This page demonstrates the integration point between user data and algorithm
outputs, showing how to trigger computation and display results in an 
educational format that teaches about the underlying algorithms.
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

from models.enhanced_ui import AppState
from services.algorithm_engine import compute_algorithm_results

def render(state: AppState) -> None:
    """Render algorithm computation and insights page."""
    st.title("🧠 Compute Algorithm Insights")
    st.markdown("Generate computed insights from your profile and wearable data.")
    
    # Check if we have enough data to compute insights
    has_profile = bool(state.current_inputs.user_profile.name != "User")
    has_wearable = bool(state.current_inputs.wearable_data)
    has_tasks = bool(state.current_inputs.tasks)
    
    # Show data availability status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if has_profile:
            st.success("✅ **Profile Data**")
            st.caption(f"User: {state.current_inputs.user_profile.name}")
        else:
            st.warning("⚠️ **Profile Data Missing**")
            st.caption("Complete your profile first")
    
    with col2:
        if has_wearable:
            st.success("✅ **Wearable Data**")
            st.caption(f"Sleep: {state.current_inputs.wearable_data.sleep_quality}")
        else:
            st.info("ℹ️ **Wearable Data Optional**")
            st.caption("Add for better insights")
    
    with col3:
        if has_tasks:
            st.success("✅ **Tasks Data**")
            st.caption(f"{len(state.current_inputs.tasks)} tasks")
        else:
            st.warning("⚠️ **No Tasks**")
            st.caption("Add tasks to schedule")
    
    st.markdown("---")
    
    # Compute insights button
    if has_profile:
        if st.button("🚀 Compute Algorithm Insights", type="primary", width="stretch"):
            with st.spinner("Computing insights..."):
                try:
                    # Compute all algorithm results
                    results = compute_algorithm_results(
                        user_profile=state.current_inputs.user_profile,
                        wearable_data=state.current_inputs.wearable_data
                    )
                    
                    # Update state with computed results
                    state.current_inputs.algorithm_results = results
                    
                    st.success("✅ Algorithm insights computed successfully!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error computing insights: {e}")
                    st.exception(e)
        
        # Show computed results if available
        if (state.current_inputs.algorithm_results.detected_chronotype or 
            state.current_inputs.algorithm_results.energy_level):
            _render_computed_results(state)
            
    else:
        st.info("👆 Complete your profile in the **Schedule Data** tab to enable algorithm computation.")

def _render_computed_results(state: AppState) -> None:
    """Render the computed algorithm results with explanations."""
    st.header("📊 Computed Insights")
    
    results = state.current_inputs.algorithm_results
    
    # Chronotype Analysis Section
    if results.detected_chronotype:
        with st.expander("🌅 Chronotype Analysis", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Detected Chronotype", 
                    results.detected_chronotype,
                    help="Based on your MEQ score"
                )
                
                if results.chronotype_confidence:
                    confidence_pct = f"{results.chronotype_confidence:.0%}"
                    st.metric(
                        "Confidence Level",
                        confidence_pct,
                        help="How certain we are about this classification"
                    )
            
            with col2:
                st.info(f"""
                **Algorithm Explanation:**
                Your MEQ score of {state.current_inputs.user_profile.meq_score} indicates a 
                {results.detected_chronotype.lower()} chronotype with {results.chronotype_confidence:.0%} confidence.
                
                This affects your optimal work windows and sleep timing.
                """)
    
    # Sleep Optimization Section  
    if results.recommended_bedtime:
        with st.expander("😴 Sleep Optimization", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Optimal Bedtime", results.recommended_bedtime)
                st.metric("Optimal Wake Time", results.recommended_wake_time)
                
                if results.sleep_quality_score:
                    st.metric("Sleep Quality Score", f"{results.sleep_quality_score:.1f}/100")
            
            with col2:
                st.info(f"""
                **Algorithm Explanation:**
                Based on your work schedule ({state.current_inputs.user_profile.start_time}) and 
                {state.current_inputs.user_profile.commute_minutes}-minute commute, plus your 
                {results.detected_chronotype.lower()} chronotype.
                
                This ensures adequate sleep while aligning with your natural rhythm.
                """)
    
    # Energy Analysis Section
    if results.energy_level:
        with st.expander("⚡ Energy & Performance Analysis", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                _render_energy_gauge("Energy Level", results.energy_level, "🔋")
            
            with col2:
                _render_energy_gauge("Fatigue Level", results.fatigue_level, "😴")
            
            with col3:
                _render_energy_gauge("Motivation Level", results.motivation_level, "🎯")
            
            if state.current_inputs.wearable_data:
                st.info(f"""
                **Algorithm Explanation:**
                Energy levels computed from your wearable data:
                • Sleep Quality: {state.current_inputs.wearable_data.sleep_quality}
                • Readiness Score: {state.current_inputs.wearable_data.readiness_score:.1%}
                • Stress Level: {state.current_inputs.wearable_data.stress_level}
                • Recovery Index: {state.current_inputs.wearable_data.recovery_index}%
                
                These combine to predict your current performance capacity.
                """)
    
    # Work Optimization Section
    if results.optimal_work_windows:
        with st.expander("💼 Work Optimization", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🕐 Optimal Work Windows")
                for i, window in enumerate(results.optimal_work_windows, 1):
                    st.success(f"**Focus Block {i}:** {window}")
                
                if results.optimal_break_times:
                    st.subheader("☕ Suggested Break Times")
                    for break_time in results.optimal_break_times:
                        st.info(f"Break at **{break_time}**")
            
            with col2:
                st.info(f"""
                **Algorithm Explanation:**
                Optimal windows calculated for {results.detected_chronotype.lower()} chronotype:
                
                • **Morning Peak:** Higher cognitive performance early
                • **Afternoon Window:** Secondary productivity period
                • **Strategic Breaks:** Prevent fatigue accumulation
                
                This maximizes your productivity within your work schedule.
                """)
    
    # Navigation hint
    st.markdown("---")
    st.info("💡 **Next Step:** Go to the **Generate** tab to create your personalized schedule using these insights!")

def _render_energy_gauge(title: str, value: int, emoji: str) -> None:
    """Render a visual gauge for energy-related metrics."""
    # Create a simple progress-style gauge
    colors = ["🔴", "🟠", "🟡", "🟢", "🔵"]
    color = colors[min(value - 1, 4)] if value else "⚪"
    
    st.metric(
        f"{emoji} {title}",
        f"{value}/5",
        help=f"Current {title.lower()}: {value} out of 5"
    )
    
    # Visual representation
    progress_bar = "█" * value + "░" * (5 - value)
    st.caption(f"`{progress_bar}`")
