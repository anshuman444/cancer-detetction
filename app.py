import streamlit as st
from streamlit_option_menu import option_menu
import home
import detection
import visualization
import auth
from database import initialize_db

# Initialize database on startup
initialize_db()

# Set page configuration with wide layout, page title, and icon
st.set_page_config(layout="wide", page_title="Cancer Detective", page_icon="🎗️")

# Clinical Premium Design System CSS
st.markdown("""
    <style>
    /* Hide Streamlit components */
    [data-testid="stHeader"], [data-testid="stFooter"], .css-1iyw2u1 {
        display: none;
    }

    /* Fix Streamlit's default container padding to prevent 'left-heavy' look */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }
        
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }

    /* Professional Sidebar narrowing */
    [data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 280px !important;
    }

    /* Fix Streamlit's default container padding */
    .block-container {
        padding: 2rem 4rem !important;
    }

    /* Clean Clinical Background */
    .stApp {
        background: #f8fafc;
        color: #1e293b;
    }

    /* Typography */
    .title-font {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #0d9488; /* Deep Teal */
        margin-bottom: 20px;
        letter-spacing: -1px;
    }
    
    .sub-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 20px;
    }
    
    .custom-font {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: #475569;
    }
    
    /* Professional Clinical Cards */
    .main {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 40px;
        margin: 0 auto;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        max-width: 1700px;
        width: 100%;
        display: block;
    }
    
    .main h2 {
        color: #0d9488;
        font-weight: 700;
        margin-top: 0;
    }
    
    .main p {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #475569;
    }

    /* Interactive Feature Cards */
    .feature-box {
        background: #f1f5f9;
        border-left: 5px solid #0d9488;
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
    }
    
    /* Modern Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #ffffff;
        border-radius: 10px;
        color: #64748b;
        font-weight: 600;
        padding: 0 20px;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: #0d9488 !important;
        color: #ffffff !important;
        border: none !important;
    }

    /* Detection Insight Cards */
    .dmain {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
    }
    
    .cprob {
        text-align: center; 
        background: #fef2f2;
        border: 2px solid #ef4444;
        padding: 30px; 
        border-radius: 20px; 
        color: #991b1b;
        margin-bottom: 25px;
    }
    
    .ncprob {
        text-align: center; 
        background: #f0fdf4;
        border: 2px solid #22c55e;
        padding: 30px; 
        border-radius: 20px; 
        color: #166534;
        margin-bottom: 25px;
    }
    
    /* Premium File Uploader */
    [data-testid="stFileUploadDropzone"] {
        background: #ffffff;
        border: 2px dashed #cbd5e1;
        border-radius: 15px;
        padding: 40px;
    }
    
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #0d9488;
        background: #f0fdfa;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    
    </style>
    """, 
    unsafe_allow_html=True
    )

# Automatically set session state for open access
if 'user' not in st.session_state:
    # Use a default Administrator profile
    st.session_state.user = {
        'id': 1,
        'username': 'Clinical_Guest',
        'name': 'Clinical User',
        'role': 'Administrator'
    }

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func, roles=None):
        self.apps.append({"title": title, "function": func, "roles": roles})

    def run(self):
        current_user = st.session_state.user
        
        # In open access mode, we show all apps
        allowed_apps = self.apps

        with st.sidebar:
            selected_app = option_menu(
                menu_title="🎗️ Cancer Detective",
                options=[app["title"] for app in allowed_apps],
                icons=["house", "camera", "bar-chart-line", "file-text", "people", "shield-lock"],
                menu_icon="none",
                default_index=0,
                styles={
                    "container": {
                        "padding": "10px", 
                        "background-color": "#ffffff",
                        "border-radius": "0",
                        "border": "none",
                    },
                    "icon": {
                        "color": "#0d9488",  
                        "font-size": "18px",  
                    },
                    "nav-link": {
                        "font-size": "15px",
                        "color": "#475569",
                        "padding": "10px",
                    },
                    "nav-link-selected": {
                        "background-color": "#f0fdfa",
                        "color": "#0d9488",
                        "font-weight": "700",
                        "border-left": "4px solid #0d9488",
                    },
                }
            )
            
            # Simplified Profile View
            st.markdown(f"""
                <div style="padding: 20px; border-top: 1px solid #e2e8f0; margin-top: 20px;">
                    <span style="display: block; font-size: 0.8rem; color: #64748b; font-weight: 600;">ENVIRONMENT</span>
                    <span style="display: block; font-size: 1rem; color: #0d9488; font-weight: 700;">Clinical Dashboard</span>
                </div>
            """, unsafe_allow_html=True)



        # Run the selected app from the sidebar menu (OUTSIDE the sidebar block)
        for app in allowed_apps:
            if app["title"] == selected_app:
                app["function"]()

# Add the individual apps to the MultiApp instance
app_runner = MultiApp()
app_runner.add_app("Home", home.app)
app_runner.add_app("Detection", detection.app, roles=["Doctor", "Lab Technician", "Researcher"])
app_runner.add_app("Visualizing", visualization.app, roles=["Researcher", "Doctor"])


try:
    import patient_management
    app_runner.add_app("Patients", patient_management.app, roles=["Doctor", "Lab Technician"])
except ImportError:
    pass
    
try:
    import admin_panel
    app_runner.add_app("Admin Console", admin_panel.app, roles=["Administrator"])
except ImportError:
    pass
    
app_runner.run()
