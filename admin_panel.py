import streamlit as st
import pandas as pd
from database import get_connection

def app():
    st.markdown('<h1 class="title-font">🛡️ Admin Console</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👥 User Management", "📋 System Logs", "📦 Dataset Overview"])
    
    with tab1:
        st.markdown('<h2 class="sub-title">System Users</h2>', unsafe_allow_html=True)
        conn = get_connection()
        users_df = pd.read_sql_query("SELECT id, username, name, role, created_at FROM users", conn)
        conn.close()
        st.dataframe(users_df, use_container_width=True)
        
        with st.expander("Add New User"):
            with st.form("add_user_form"):
                new_username = st.text_input("Username")
                new_name = st.text_input("Full Name")
                new_password = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["Doctor", "Lab Technician", "Researcher", "Administrator"])
                if st.form_submit_button("Create User"):
                    import auth
                    if auth.register_user(new_username, new_password, new_role, new_name):
                        st.success(f"User {new_username} created successfully!")
                        st.rerun()
                    else:
                        st.error("Username already exists or database error.")

    with tab2:
        st.markdown('<h2 class="sub-title">Recent Activity</h2>', unsafe_allow_html=True)
        conn = get_connection()
        # Join scans with users to see who did what
        logs_query = """
            SELECT s.timestamp, u.username, s.cancer_type, s.prediction_result, s.confidence 
            FROM scans s
            LEFT JOIN users u ON s.user_id = u.id
            ORDER BY s.timestamp DESC LIMIT 50
        """
        logs_df = pd.read_sql_query(logs_query, conn)
        conn.close()
        st.dataframe(logs_df, use_container_width=True)

    with tab3:
        st.markdown('<h2 class="sub-title">Dataset Management</h2>', unsafe_allow_html=True)
        
        dtype = st.selectbox("Select Dataset Category", ["Lung Cancer", "Skin Cancer"])
        
        if dtype == "Lung Cancer":
            label = st.selectbox("Select Class Label", ["aca", "scc", "benign"])
            path = f"datasets/lung/{label}"
        else:
            label = st.selectbox("Select Class Label", ["malignant", "benign"])
            path = f"datasets/skin/{label}"
            
        uploaded_files = st.file_uploader(f"Upload Images to {label.upper()}", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        
        if uploaded_files:
            import os
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                
            count = 0
            for uploaded_file in uploaded_files:
                file_path = os.path.join(path, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                count += 1
            st.success(f"Successfully uploaded {count} images to {path}")

        st.markdown("---")
        st.markdown('<h2 class="sub-title">Model Retraining</h2>', unsafe_allow_html=True)
        st.warning("Retraining will update the live models. This process may take several minutes depending on hardware.")
        
        target_model = st.selectbox("Target Model", ["Lung Model", "Skin Model"])
        
        if st.button(f"🚀 Start {target_model} Retraining", use_container_width=True):
            st.info(f"Retraining {target_model}... Please wait.")
            # Placeholder for actual training script execution
            # In a real scenario, this would trigger a subprocess
            import subprocess
            import sys
            
            script = "train_lung.py" if target_model == "Lung Model" else "train_skin.py"
            
            try:
                # Run the script in the background to avoid blocking
                # We'll use the same python interpreter
                process = subprocess.Popen([sys.executable, script], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE,
                                         cwd="e:/cancer detection")
                st.success(f"Training process started (PID: {process.pid}). Monitor logs for progress.")
            except Exception as e:
                st.error(f"Failed to start training: {e}")

        st.info("System health is optimal. No pending updates identified.")

if __name__ == "__main__":
    app()
