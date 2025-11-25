"""Diagnostics page: shows logs + last request/response.

Extensible area for latency metrics, cache inspection, and preset state.
"""
from __future__ import annotations
import streamlit as st
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.ui import AppState

def render(state: AppState) -> None:
    """Enhanced diagnostics page with comprehensive system information."""
    
    st.markdown("### 🔍 System Diagnostics")
    
    """API Status Overview"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🌐 API Status", 
            value="Connected" if state.api_client else "Not Connected",
            delta="Online" if state.api_client else "Check Configuration"
        )
    
    with col2:
        st.metric(
            label="⏱️ Last Response Time", 
            value=f"{state.last_latency_ms or 0}ms",
            delta="Good" if (state.last_latency_ms or 0) < 1000 else "Slow"
        )
    
    with col3:
        st.metric(
            label="💾 Saved Presets", 
            value=len(state.preset_store.presets) if state.preset_store else 0,
            delta="Available"
        )
    
    """Last API Interaction"""
    st.markdown("### 📡 Last API Request/Response")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔄 Request Payload**")
        if state.last_request:
            with st.expander("View Request Details", expanded=False):
                st.json(state.last_request)
        else:
            st.info("No requests made yet. Try generating a schedule first!")
    
    with col2:
        st.markdown("**📨 Response Data**")
        if state.last_response:
            with st.expander("View Response Details", expanded=False):
                st.json(state.last_response)
        else:
            st.info("No responses received yet.")
    
    """Configuration Status"""
    st.markdown("### ⚙️ Configuration Status")
    
    config_data = {
        "API Base URL": state.api_base_url,
        "Timeout": f"{state.timeout_seconds}s",
        "Current Inputs": len(state.current_inputs.tasks),
        "Prime Windows": len(state.prime_windows)
    }
    
    for key, value in config_data.items():
        st.text(f"• {key}: {value}")
    
    """Preset Management"""
    if state.preset_store and state.preset_store.presets:
        st.markdown("### 💾 Preset Details")
        for name, preset in state.preset_store.presets.items():
            with st.expander(f"📋 {name}", expanded=False):
                st.json(preset)
    
    """Debug Information"""
    st.markdown("### 🐛 Debug Information")
    with st.expander("Show Debug Data", expanded=False):
        debug_info = {
            "state_type": type(state).__name__,
            "api_client_type": type(state.api_client).__name__ if state.api_client else None,
            "current_inputs_count": len(state.current_inputs.tasks),
            "deep_internals_available": state.deep_internals is not None
        }
        st.json(debug_info)
