import streamlit as st
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model # type: ignore
from PIL import Image, ImageOps
import numpy as np
import io
import base64
import logging
import warnings
from database import get_connection
import pdf_utils

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load the improved trained model for skin cancer detection
try:
    skin_model = load_model('models/skin_cancer_model.h5')
    logging.info("Skin cancer model loaded successfully")
except Exception as e:
    logging.error(f"Error loading skin cancer model: {e}")
    skin_model = None

# Prediction function for skin cancer
def predict_skin_image(image):
    if skin_model is None:
        logging.error("Skin cancer model is not loaded.")
        return np.array([[0, 0]])
    
    try:
        img = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)
        img = np.asarray(img) / 255.0
        img = np.expand_dims(img, axis=0)
        logging.debug(f"Image shape for skin prediction: {img.shape}")

        prediction = skin_model.predict(img)
        logging.debug(f"Skin prediction: {prediction}")
        
        return prediction
    except Exception as e:
        logging.error(f"Error during skin prediction: {e}")
        return np.array([[0, 0]])

# Load the trained models
try:
    lung_model = load_model('models/lung_cancer_model.h5')
    logging.info("Models loaded successfully")
except Exception as e:
    logging.error(f"Error loading models: {e}")
    lung_model = None
    
# Function to convert image to base64
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


# Define the class mapping with exact cancer types
index = {
    'lung_aca': 'Lung Adenocarcinoma (Cancerous)',
    'lung_n': 'Lung Benign Tissue (Non-Cancerous)',
    'lung_scc': 'Lung Squamous Cell Carcinoma (Cancerous)'
}

def predict_lung_image(image):
    if lung_model is None:
        logging.error("Lung cancer model is not loaded.")
        return None

    try:
        # Preprocess the image to match the input shape of the model
        img = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)
        img = np.asarray(img) / 255.0
        img = np.expand_dims(img, axis=0)
        logging.debug(f"Image shape for prediction: {img.shape}")

        # Get the model prediction
        prediction = lung_model.predict(img)
        logging.debug(f"Lung Cancer Prediction: {prediction}")
        
        # The prediction returns probabilities for each class
        lung_aca_prob = prediction[0][0]  # Probability of Lung Adenocarcinoma (cancerous)
        lung_n_prob = prediction[0][1]    # Probability of Lung Benign Tissue (non-cancerous)
        lung_scc_prob = prediction[0][2]  # Probability of Lung Squamous Cell Carcinoma (cancerous)

        # Get the class index with the highest probability
        predicted_class_index = np.argmax(prediction, axis=1)[0]

        # Map the predicted class index to the corresponding cancer type
        if predicted_class_index == 0:  # lung_aca
            predicted_class = 'Lung Adenocarcinoma'
            cancer_status = 'Cancerous'
        elif predicted_class_index == 1:  # lung_n
            predicted_class = 'Lung Benign Tissue'
            cancer_status = 'Non-Cancerous'
        elif predicted_class_index == 2:  # lung_scc
            predicted_class = 'Lung Squamous Cell Carcinoma'
            cancer_status = 'Cancerous'

        return predicted_class, cancer_status, lung_aca_prob, lung_n_prob, lung_scc_prob
    except Exception as e:
        logging.error(f"Error during lung cancer prediction: {e}")
        return None

def save_scan_result(patient_id, user_id, cancer_type, result, confidence):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scans (patient_id, user_id, cancer_type, prediction_result, confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_id, user_id, cancer_type, result, confidence))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Error saving scan result: {e}")
        return False

def app():
    st.markdown('<h1 class="title-font">📸 Case Diagnostics</h1>', unsafe_allow_html=True)

    # Tabs for different cancer types
    tabs = st.tabs(["🫁 Lung Cancer", "🧬 Skin Lesion"])

    with tabs[0]:
        st.markdown('<h2 class="sub-title">Lung Histopathology Analysis</h2>', unsafe_allow_html=True)
        st.markdown("""
            Perform automated screening on lung tissue histopathology slides. The system differentiates between 
            Adenocarcinoma, Squamous Cell Carcinoma, and Benign tissue.
        """)
        
        # Patient Selection Logic
        conn = get_connection()
        patients_df = pd.read_sql_query("SELECT id, name FROM patients", conn)
        conn.close()
        
        patient_options = ["None (Anonymous)"] + [f"ID: {row['id']} - {row['name']}" for _, row in patients_df.iterrows()]
        selected_patient = st.selectbox("Link to Patient", options=patient_options, key="lung_patient")
        patient_id = int(selected_patient.split(":")[1].split("-")[0].strip()) if "ID:" in selected_patient else None

        uploaded_file = st.file_uploader("Upload Tissue Slide Image", type=["jpg", "jpeg", "png"], key="lung_upload")
    
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_resized = image.resize((600, 600))
            img_base64 = image_to_base64(image_resized)
            
            st.markdown(f"""
                <div style='text-align: center; margin: 30px 0;'>
                    <img src="data:image/png;base64,{img_base64}" width="100%" style='max-width: 600px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 30px rgba(0,0,0,0.5);'/>
                </div>
            """, unsafe_allow_html=True)
    
            prediction = predict_lung_image(image)
    
            if prediction is not None:
                predicted_class, cancer_status, lung_aca_prob, lung_n_prob, lung_scc_prob = prediction
                
                # Save result to database
                user_id = st.session_state.user['id'] if 'user' in st.session_state else None
                save_scan_result(patient_id, user_id, "Lung Cancer", predicted_class, 
                                float(max(lung_aca_prob, lung_n_prob, lung_scc_prob)))
    
                st.markdown(f"""
                    <div class='dmain'>
                        <h4 style='color: #334155; margin-bottom: 20px;'>Classification Probability Matrix</h4>
                        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                            <div style='padding:15px; background:#fef2f2; border-radius:12px; border: 1px solid #fecaca;'>
                                <div style='font-size:0.8rem; color:#991b1b; opacity:0.8;'>Adenocarcinoma</div>
                                <div style='font-size:1.2rem; font-weight:700; color:#dc2626;'>{lung_aca_prob * 100:.2f}%</div>
                            </div>
                            <div style='padding:15px; background:#fef2f2; border-radius:12px; border: 1px solid #fecaca;'>
                                <div style='font-size:0.8rem; color:#991b1b; opacity:0.8;'>Squamous Cell</div>
                                <div style='font-size:1.2rem; font-weight:700; color:#dc2626;'>{lung_scc_prob * 100:.2f}%</div>
                            </div>
                            <div style='padding:15px; background:#f0fdf4; border-radius:12px; border: 1px solid #bbf7d0; grid-column: span 2;'>
                                <div style='font-size:0.8rem; color:#166534; opacity:0.8;'>Benign Tissue</div>
                                <div style='font-size:1.2rem; font-weight:700; color:#16a34a;'>{lung_n_prob * 100:.2f}%</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
                if cancer_status == "Cancerous":
                    st.markdown(f"""
                        <div class="cprob">
                            <h2 style='color: #991b1b; margin-bottom: 10px;'>🚨 Lung Malignancy Detected</h2>
                            <p style='color: #b91c1c; font-size: 1.1rem;'>Primary Diagnosis: <b>{predicted_class}</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.error("URGENT: Oncological consultation and biopsy validation required. 🫁")
                else:
                    st.markdown(f"""
                        <div class="ncprob">
                            <h2 style='color: #166534; margin-bottom: 10px;'>✅ Benign Tissue Identified</h2>
                            <p style='color: #15803d; font-size: 1.1rem;'>Classification: <b>{predicted_class}</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.success("SAFE: Tissue structures appear benign. Periodic follow-up recommended. 🥗")
                
                # PDF Download Button
                patient_info = {}
                if patient_id:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, age, gender, contact FROM patients WHERE id = ?", (patient_id,))
                    row = cursor.fetchone()
                    conn.close()
                    if row:
                        patient_info = {"name": row[0], "age": row[1], "gender": row[2], "contact": row[3]}
                
                scan_info = {
                    "cancer_type": "Lung Cancer",
                    "prediction_result": predicted_class,
                    "confidence": float(max(lung_aca_prob, lung_n_prob, lung_scc_prob)),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                from datetime import datetime
                pdf_bytes = pdf_utils.generate_scan_report(patient_info, scan_info)
                st.download_button(
                    label="📄 Generate & Download Clinical Diagnostic Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"Lung_Report_{patient_info.get('name', 'Anonymous')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="lung_pdf_btn"
                )
                
    with tabs[1]:
        st.header("🔍 Skin Lesion Screening")
        st.markdown("""
            AI-powered dermoscopic analysis for skin lesions. This tool assists in differentiating between 
            malignant melanoma and benign melanocytic nevi.
        """)
        
        # Patient Selection Logic
        conn = get_connection()
        patients_df = pd.read_sql_query("SELECT id, name FROM patients", conn)
        conn.close()
        
        patient_options = ["None (Anonymous)"] + [f"ID: {row['id']} - {row['name']}" for _, row in patients_df.iterrows()]
        selected_patient = st.selectbox("Link to Patient", options=patient_options, key="skin_patient")
        patient_id = int(selected_patient.split(":")[1].split("-")[0].strip()) if "ID:" in selected_patient else None

        uploaded_file = st.file_uploader("Upload Lesion Image", type=["jpg", "jpeg", "png"], key="skin_upload")

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_resized = image.resize((600, 600))
            img_base64 = image_to_base64(image_resized)
            
            st.markdown(f"""
                <div style='text-align: center; margin: 30px 0;'>
                    <img src="data:image/png;base64,{img_base64}" width="100%" style='max-width: 600px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 30px rgba(0,0,0,0.5);'/>
                </div>
            """, unsafe_allow_html=True)

            prediction = predict_skin_image(image)

            if prediction is not None:
                benign_prob = prediction[0][0]
                malignant_prob = prediction[0][1]
                
                # Save result to database
                user_id = st.session_state.user['id'] if 'user' in st.session_state else None
                save_scan_result(patient_id, user_id, "Skin Lesion", 
                                "Malignant" if malignant_prob > 0.5 else "Benign", 
                                float(max(benign_prob, malignant_prob)))
                
                st.markdown(f"""
                    <div class='dmain'>
                        <h4 style='color: #334155; margin-bottom: 20px;'>Dermoscopic Risk Profile</h4>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 10px; color: #475569;'>
                            <span>Malignancy Risk (Melanoma):</span>
                            <span style='color: #dc2626; font-weight: 700;'>{malignant_prob * 100:.2f}%</span>
                        </div>
                        <div style='display: flex; justify-content: space-between; color: #475569;'>
                            <span>Benign (Nevus/Mole):</span>
                            <span style='color: #16a34a; font-weight: 700;'>{benign_prob * 100:.2f}%</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                    
                threshold = 0.5
                if malignant_prob > threshold:
                    st.markdown(f"""
                        <div class="cprob">
                            <h2 style='color: #991b1b; margin-bottom: 10px;'>🚨 Melanoma Markers Identified</h2>
                            <p style='color: #b91c1c; font-size: 1.1rem;'>High risk lesion detection. Requires specialist review.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.error("ACTION: Immediate dermatological examination with dermoscopy is vital. 🧴")
                else:
                    st.markdown(f"""
                        <div class="ncprob">
                            <h2 style='color: #166534; margin-bottom: 10px;'>✅ Benign Indicators</h2>
                            <p style='color: #15803d; font-size: 1.1rem;'>Lesion structures currently present low-risk morphological features.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.success("STABLE: Observe for any changes in shape, border, or color. 🧖‍♀️")

                # PDF Download Button
                patient_info = {}
                if patient_id:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, age, gender, contact FROM patients WHERE id = ?", (patient_id,))
                    row = cursor.fetchone()
                    conn.close()
                    if row:
                        patient_info = {"name": row[0], "age": row[1], "gender": row[2], "contact": row[3]}
                
                scan_info = {
                    "cancer_type": "Skin Lesion",
                    "prediction_result": "Malignant" if malignant_prob > 0.5 else "Benign",
                    "confidence": float(max(benign_prob, malignant_prob)),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                from datetime import datetime
                pdf_bytes = pdf_utils.generate_scan_report(patient_info, scan_info)
                st.download_button(
                    label="📄 Generate & Download Dermatological Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"Skin_Report_{patient_info.get('name', 'Anonymous')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="skin_pdf_btn"
                )

if __name__ == "__main__":
    app()
