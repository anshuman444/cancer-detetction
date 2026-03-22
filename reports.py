import streamlit as st
import pandas as pd
from database import get_connection
import pdf_utils
from datetime import datetime

def app():
    st.markdown('<h1 class="title-font">📄 Medical Reports</h1>', unsafe_allow_html=True)
    
    st.markdown("""
        Upload patient medical reports (Text or CSV) for automated analysis and record-keeping. 
        This module supports data cleaning and NLP-based insight extraction.
    """)
    
    tab1, tab2 = st.tabs(["📤 Upload Report", "📜 Report History"])
    
    with tab1:
        st.markdown('<div class="main">', unsafe_allow_html=True)
        uploaded_report = st.file_uploader("Upload Medical Report (TXT)", type=["txt", "csv"])
        
        if uploaded_report:
            if uploaded_report.type == "text/plain":
                content = uploaded_report.read().decode("utf-8")
                
                # Patient Selection Logic
                conn = get_connection()
                patients_df = pd.read_sql_query("SELECT id, name FROM patients", conn)
                conn.close()
                patient_options = ["None (Anonymous)"] + [f"ID: {row['id']} - {row['name']}" for _, row in patients_df.iterrows()]
                selected_patient = st.selectbox("Link to Patient", options=patient_options)
                patient_id = int(selected_patient.split(":")[1].split("-")[0].strip()) if "ID:" in selected_patient else None

                st.text_area("Report Content Preview", content, height=200)
                
                # Placeholder for text-based cancer detection logic
                st.info("Analyzing report for clinical keywords...")
                keywords = ["malignant", "carcinoma", "tumor", "positive"]
                found = [k for k in keywords if k in content.lower()]
                
                if found:
                    st.warning(f"Keywords detected: {', '.join(found)}")
                    result = "Attention Required: Keywords identified"
                else:
                    st.success("No high-risk keywords detected.")
                    result = "Routine/Benign"
                
                if st.button("Save to Records"):
                    user_id = st.session_state.user['id'] if 'user' in st.session_state else None
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO reports (patient_id, user_id, report_text, prediction) VALUES (?, ?, ?, ?)", 
                                 (patient_id, user_id, content, result))
                    conn.commit()
                    conn.close()
                    st.success("Report saved to patient history!")
                    
                    # PDF Download for Report
                    patient_info = {}
                    if patient_id:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM patients WHERE id = ?", (patient_id,))
                        row = cursor.fetchone()
                        conn.close()
                        if row:
                            patient_info = {"name": row[0]}
                    
                    pdf_bytes = pdf_utils.generate_report_pdf(patient_info, content, result)
                    st.download_button(
                        label="📥 Download Report PDF",
                        data=pdf_bytes,
                        file_name=f"Medical_Report_{patient_info.get('name', 'Anonymous')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<h2 class="sub-title">Archived Reports</h2>', unsafe_allow_html=True)
        conn = get_connection()
        reports_df = pd.read_sql_query("SELECT timestamp, report_text, prediction FROM reports ORDER BY timestamp DESC", conn)
        conn.close()
        
        if not reports_df.empty:
            st.dataframe(reports_df, use_container_width=True)
        else:
            st.write("No reports archived yet.")

if __name__ == "__main__":
    app()
