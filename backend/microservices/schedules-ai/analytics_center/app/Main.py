"""Streamlit entry point for Analytics Control Center.

Educational Purpose:
Provides a centralized UI for schedule generation analysis with sidebar configuration
and dynamic page loading. Demonstrates clean separation between navigation, state
management, and page rendering.

Architecture Notes:
- Single Main.py entry point for Streamlit app
- Dynamic page module loading via PAGES registry
- Centralized state management through AppState
- API client configuration in sidebar
"""
from __future__ import annotations
import streamlit as st
import sys
import os
from typing import Dict, Any

# Add analytics_center to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.ui import AppState, PresetStore, EnergyWindow
from models.enhanced_ui import AppState as EnhancedAppState, InputCollection
from utils.state import init_state, get_state
from services.presets import load_presets, save_presets
from services.client import APIClient, APISettings

PAGES: Dict[str, str] = {
    "enhanced_inputs_page": "modules.enhanced_inputs_page",
    "generate_page": "modules.generate_page",
}

def _import_render(module_path: str):
    """
    Dynamically imports render function from page module.
    
    Educational Note:
    Using dynamic imports allows adding new pages without modifying
    the main routing logic. This follows the Open-Closed Principle
    (open for extension, closed for modification).
    
    Args:
        module_path: Dotted path to page module (e.g., 'modules.generate_page')
        
    Returns:
        render function from the module
        
    Raises:
        ImportError: If module or render function cannot be found
    """
    try:
        module = __import__(module_path, fromlist=['render'])
        return getattr(module, 'render')
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to import render from {module_path}: {e}")

def _sidebar(state: AppState) -> None:
    """
    Renders sidebar with API configuration.
    
    Educational Note:
    Minimal sidebar configuration for cleaner, competition-ready UI.
    Focuses on essential API connectivity without clutter.
    
    Args:
        state: Application state for reading/writing configuration
    """
    with st.sidebar.expander("🔌 API Settings", expanded=False):
        base = st.text_input("API Base URL", state.api_base_url, help="Backend API endpoint")
        
        if state.api_client:
            st.success("🟢 Connected")
        else:
            st.warning("🟡 Not Connected")
        
        if base != state.api_base_url:
            state.api_base_url = base
            state.api_client = APIClient(APISettings(
                base_url=base, 
                timeout=300
            ))

def main() -> None:
    """
    Main application entry point with page routing.
    
    Educational Note:
    This function orchestrates the entire application flow: page configuration,
    state initialization, sidebar rendering, and dynamic page loading. It
    demonstrates the Front Controller pattern for web applications.
    """
    st.set_page_config(
        page_title="Schedules Analytics", 
        layout="wide",
        page_icon="📊",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced CSS for professional dark theme styling
    st.markdown("""
        <style>
        /* Dark theme base */
        .stApp {
            background-color: #0e1117;
        }
        
        /* Main header styling */
        .main-header {
            padding: 1.5rem 0;
            border-bottom: 3px solid #667eea;
            margin-bottom: 2rem;
            background: linear-gradient(90deg, rgba(102,126,234,0.2) 0%, rgba(14,17,23,0) 100%);
        }
        
        /* Metric cards with dark theme */
        .metric-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        /* Button enhancements */
        .stButton>button {
            border-radius: 0.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            border: 1px solid #262730;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
            border-color: #667eea;
        }
        
        /* Primary button special styling */
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            font-size: 1.2rem !important;
            padding: 0.8rem 2rem !important;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
            border: none !important;
        }
        .stButton>button[kind="primary"]:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
            box-shadow: 0 8px 28px rgba(102, 126, 234, 0.7) !important;
            transform: translateY(-3px) scale(1.02) !important;
        }
        
        /* Expander styling - Dark theme */
        div[data-testid="stExpander"] {
            border: 1px solid #262730;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            background-color: #1a1d26;
        }
        div[data-testid="stExpander"]:hover {
            border-color: #667eea;
            box-shadow: 0 2px 12px rgba(102, 126, 234, 0.2);
        }
        
        /* Tab styling - Dark theme */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 0.5rem 0.5rem 0 0;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            background-color: #1a1d26;
            border: 1px solid #262730;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-color: #667eea !important;
        }
        
        /* Info/Warning/Success boxes - Dark theme */
        .stAlert {
            border-radius: 0.5rem;
            border-left: 4px solid;
            background-color: rgba(26, 29, 38, 0.8);
        }
        
        /* Data editor styling - Dark theme */
        div[data-testid="stDataFrame"] {
            border-radius: 0.5rem;
            overflow: hidden;
            border: 1px solid #262730;
        }
        
        /* Schedule table styling */
        .schedule-table {
            background: #1a1d26;
            border-radius: 0.75rem;
            padding: 1rem;
            margin: 1rem 0;
            border: 1px solid #667eea;
        }
        
        .schedule-row {
            background: linear-gradient(90deg, rgba(102,126,234,0.1) 0%, rgba(26,29,38,1) 100%);
            border-left: 3px solid #667eea;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
        }
        
        .schedule-row:hover {
            background: linear-gradient(90deg, rgba(102,126,234,0.2) 0%, rgba(26,29,38,1) 100%);
            border-left-color: #764ba2;
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }
        
        .schedule-time {
            color: #667eea;
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        .schedule-task {
            color: #e0e0e0;
            font-weight: 500;
            font-size: 1rem;
        }
        
        /* Metric box styling */
        div[data-testid="stMetric"] {
            background: rgba(26, 29, 38, 0.6);
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #262730;
        }
        
        div[data-testid="stMetric"]:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)
    
    init_state()
    state = get_state()
    if state.api_client is None:
        state.api_client = APIClient(APISettings(
            base_url=state.api_base_url, 
            timeout=state.timeout_seconds
        ))
    
    st.sidebar.title("📊 Schedules Analytics")
    
    page_options = {
        "📊 Schedule Data": "enhanced_inputs_page",
        " Generate": "generate_page"
    }
    
    page_display = st.sidebar.radio("📍 Navigate to:", list(page_options.keys()))
    page_module = page_options[page_display]
    
    _sidebar(state)
    
    # Main content area with header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title(f"Auratyme {page_display}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Render selected page
    try:
        module_path = PAGES.get(page_module)
        if module_path:
            render_func = _import_render(module_path)
            render_func(state)
        else:
            st.error(f"❌ Page module '{page_module}' not found in registry.")
            st.info(f"Available modules: {list(PAGES.keys())}")
            st.info(f"Selected module: {page_module}")
    except Exception as e:
        st.error(f"❌ Error rendering page: {str(e)}")
        with st.expander("🔍 Error Details"):
            st.exception(e)
            st.code(f"Page module: {page_module}")
            st.code(f"Module path: {PAGES.get(page_module, 'Not found')}")
            st.code(f"Available pages: {list(PAGES.keys())}")

if __name__ == "__main__":  # pragma: no cover
    main()
