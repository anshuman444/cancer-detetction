import streamlit as st
import pandas as pd
from database import get_connection
import pdf_utils
from datetime import datetime

def app():
    st.markdown('<h1 class="title-font">👤 Patient Management</h1>', unsafe_allow_html=True)
    
    st.markdown("""
        Manage patient records, view clinical history, and register new patients in the system. 
        Linking scans to patients ensures organized longitudinal tracking of disease progression.
    """)
    
    tab1, tab2 = st.tabs(["👥 Patient Directory", "➕ Register New Patient"])
    
    with tab1:
        st.markdown('<h2 class="sub-title">Clinical Records</h2>', unsafe_allow_html=True)
        conn = get_connection()
        patients_df = pd.read_sql_query("SELECT * FROM patients ORDER BY created_at DESC", conn)
        
        if not patients_df.empty:
            st.dataframe(patients_df, use_container_width=True)
            
            # Interactive patient search/selection
            st.markdown("---")
            selected_patient_id = st.selectbox("Select Patient to view history", 
                                             options=patients_df['id'].tolist(),
                                             format_func=lambda x: f"ID: {x} - {patients_df[patients_df['id']==x]['name'].values[0]}")
            
            if selected_patient_id:
                st.markdown(f"### History for ID: {selected_patient_id}")
                
                # Scans History
                scans_query = "SELECT timestamp, cancer_type, prediction_result, confidence FROM scans WHERE patient_id = ?"
                scans_history = pd.read_sql_query(scans_query, conn, params=(selected_patient_id,))
                
                # Reports History
                reports_query = "SELECT timestamp, report_text, prediction FROM reports WHERE patient_id = ?"
                reports_history = pd.read_sql_query(reports_query, conn, params=(selected_patient_id,))
                
                h_col1, h_col2 = st.columns(2)
                with h_col1:
                    st.markdown("**Imaging Scans**")
                    if not scans_history.empty:
                        st.dataframe(scans_history, use_container_width=True)
                        for idx, row in scans_history.iterrows():
                            # For each scan in history, provide a download button
                            scan_data = {
                                "cancer_type": row['cancer_type'],
                                "prediction_result": row['prediction_result'],
                                "confidence": row['confidence'],
                                "timestamp": row['timestamp']
                            }
                            patient_row = patients_df[patients_df['id']==selected_patient_id].iloc[0]
                            p_info = {"name": patient_row['name'], "age": patient_row['age'], "gender": patient_row['gender'], "contact": patient_row['contact']}
                            
                            pdf_bytes = pdf_utils.generate_scan_report(p_info, scan_data)
                            st.download_button(
                                label=f"Download {row['cancer_type']} PDF ({row['timestamp']})",
                                data=pdf_bytes,
                                file_name=f"Scan_{row['timestamp']}.pdf",
                                mime="application/pdf",
                                key=f"scan_dl_{idx}"
                            )
                    else:
                        st.info("No scans found for this patient.")
                        
                with h_col2:
                    st.markdown("**Medical Reports**")
                    if not reports_history.empty:
                        st.dataframe(reports_history, use_container_width=True)
                        for idx, row in reports_history.iterrows():
                            patient_row = patients_df[patients_df['id']==selected_patient_id].iloc[0]
                            p_info = {"name": patient_row['name']}
                            pdf_bytes = pdf_utils.generate_report_pdf(p_info, row['report_text'], row['prediction'])
                            st.download_button(
                                label=f"Download Report PDF ({row['timestamp']})",
                                data=pdf_bytes,
                                file_name=f"Report_{row['timestamp']}.pdf",
                                mime="application/pdf",
                                key=f"rpt_dl_{idx}"
                            )
                    else:
                        st.info("No reports found for this patient.")
        else:
            st.info("No patients registered yet. Use the 'Register' tab to add a record.")
        conn.close()

    with tab2:
        st.markdown('<div class="main">', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-title" style="margin-top:0;">Patient Registration</h2>', unsafe_allow_html=True)
        
        with st.form("registration_form"):
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=0, max_value=120, value=30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
            contact = st.text_input("Contact Info (Phone/Email)")
            
            submit = st.form_submit_button("Register Patient", use_container_width=True)
            
            if submit:
                if name:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO patients (name, age, gender, contact)
                            VALUES (?, ?, ?, ?)
                        """, (name, age, gender, contact))
                        conn.commit()
                        conn.close()
                        st.success(f"Patient '{name}' registered successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error registering patient: {e}")
                else:
                    st.warning("Please provide at least a name.")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    app()
