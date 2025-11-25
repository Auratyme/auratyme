"""Explain page: heuristics placeholder.

Will surface solver, chronotype, sleep, LLM internals when backend
provides them. For now shows fallback derivations.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.ui import AppState
from utils.heuristics import build_heuristics

def render(state: AppState) -> None:
    """Enhanced explanation page with detailed analytics and insights."""
    
    st.markdown("### 🧠 Schedule Explanation & Insights")
    
    """Check if we have data to analyze"""
    if not state.current_inputs.tasks:
        st.warning("📝 No input data available. Please add some tasks in the Inputs page first!")
        return
    
    """Response Explanations (if available from backend)"""
    if state.last_response:
        st.markdown("### 📊 Backend Response Analysis")
        
        explanations = state.last_response.get("explanations")
        if explanations:
            st.success("✅ Backend provided detailed explanations:")
            with st.expander("🔍 View Backend Explanations", expanded=True):
                st.json(explanations)
        else:
            st.info("ℹ️ Backend response available, but no explanations provided.")
            
        """Show generated schedule if available"""
        schedule = state.last_response.get("generated_schedule")
        if schedule:
            st.markdown("### 📅 Generated Schedule Summary")
            st.info(f"📝 Total tasks scheduled: {len(schedule)}")
            
            if schedule:
                schedule_df = pd.DataFrame(schedule)
                if not schedule_df.empty:
                    st.dataframe(schedule_df, width="stretch")
    else:
        st.info("🚀 Generate a schedule first to see AI explanations and insights!")
    
    """Heuristic Analysis (our local analysis)"""
    st.markdown("### 🎯 Heuristic Analysis")
    st.info("💡 This analysis is performed locally based on your input data.")
    
    try:
        rows = [r.model_dump() for r in state.current_inputs.tasks]
        prime_windows = [w.model_dump() for w in state.prime_windows]
        metrics = build_heuristics(rows, prime_windows)
        
        if metrics:
            """Display metrics in a nice format"""
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📈 Productivity Metrics**")
                for key, value in metrics.items():
                    if key in ['utilization_ratio', 'prime_energy_alignment']:
                        if isinstance(value, (int, float)):
                            st.metric(
                                label=key.replace('_', ' ').title(),
                                value=f"{value:.2f}",
                                delta="Good" if value > 0.7 else "Could be improved"
                            )
            
            with col2:
                st.markdown("**⚖️ Balance Indicators**")
                for key, value in metrics.items():
                    if key in ['break_density', 'rounding_compliance']:
                        if isinstance(value, (int, float)):
                            st.metric(
                                label=key.replace('_', ' ').title(),
                                value=f"{value:.2f}",
                                delta="Balanced" if 0.3 <= value <= 0.7 else "Review"
                            )
            
            """Full metrics details"""
            with st.expander("🔍 Detailed Heuristic Metrics", expanded=False):
                st.json(metrics)
                
        else:
            st.warning("⚠️ Unable to calculate heuristics. Check your input data.")
            
    except Exception as e:
        st.error(f"❌ Error calculating heuristics: {str(e)}")
        with st.expander("🐛 Error Details"):
            st.exception(e)
    
    """Deep Internals (if available from backend)"""
    if state.deep_internals:
        st.markdown("### 🔧 Deep System Internals")
        st.success("✅ Advanced debugging data available from backend:")
        with st.expander("🔍 View Deep Internals", expanded=False):
            st.json(state.deep_internals)
    
    """Recommendations section"""
    st.markdown("### 💡 Optimization Recommendations")
    
    if len(state.current_inputs.tasks) < 3:
        st.info("📝 Add more tasks to get better scheduling recommendations.")
    
    if not any(r.is_fixed_time for r in state.current_inputs.tasks):
        st.info("📌 Consider marking some critical tasks as 'fixed' for better schedule stability.")
    
    total_duration = sum((r.duration_hours or 1.0) * 60 for r in state.current_inputs.tasks)
    if total_duration > 480:  # 8 hours
        st.warning("⏰ Total task duration exceeds 8 hours. Consider breaking down larger tasks or spreading across multiple days.")
    
    st.markdown("---")
    st.caption("💭 Explanations help you understand how the AI makes scheduling decisions and optimize your productivity.")
