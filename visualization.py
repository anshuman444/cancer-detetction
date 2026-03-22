import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import json
from database import get_connection

def load_training_history(file_path):
    try:
        with open(file_path, 'r') as file:
            history = json.load(file)
        return history
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        return None

def load_test_accuracy(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data['test_accuracy']
    except Exception:
        return None

def apply_chart_theme(fig):
    fig.update_layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        font_color='#475569',
        xaxis=dict(showgrid=True, gridcolor='#e2e8f0', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', zeroline=False),
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified"
    )
    return fig

def plot_training_accuracy(history):
    if history is None:
        return
    epochs = range(1, len(history['accuracy']) + 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(epochs), y=history['accuracy'], mode='lines+markers', name='Training', line=dict(color='#0d9488', width=3)))
    fig.add_trace(go.Scatter(x=list(epochs), y=history['val_accuracy'], mode='lines+markers', name='Validation', line=dict(color='#94a3b8', width=2, dash='dot')))
    fig.update_layout(title='Accuracy Evolution', xaxis_title='Epochs', yaxis_title='Accuracy')
    st.plotly_chart(apply_chart_theme(fig), use_container_width=True)

def plot_training_loss(history):
    if history is None:
        return
    epochs = range(1, len(history['loss']) + 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(epochs), y=history['loss'], mode='lines+markers', name='Training', line=dict(color='#0f766e', width=3)))
    fig.add_trace(go.Scatter(x=list(epochs), y=history['val_loss'], mode='lines+markers', name='Validation', line=dict(color='#94a3b8', width=2, dash='dot')))
    fig.update_layout(title='Loss Reduction', xaxis_title='Epochs', yaxis_title='Loss')
    st.plotly_chart(apply_chart_theme(fig), use_container_width=True)

def plot_confusion_matrix(cm, classes):
    if cm is None:
        return
    cm_df = pd.DataFrame(cm, index=classes, columns=classes)
    fig = px.imshow(cm_df, text_auto=True, color_continuous_scale=['#f0fdfa', '#0d9488'])
    fig.update_layout(title='Confusion Matrix Analysis', xaxis_title='Predicted Label', yaxis_title='True Label')
    st.plotly_chart(apply_chart_theme(fig), use_container_width=True)

def app():
    st.markdown('<h1 class="title-font">📊 Performance Analytics</h1>', unsafe_allow_html=True)
    
    # --- Live Clinical Data Section (The 'Everything' View) ---
    conn = get_connection()
    query = """
    SELECT 
        s.timestamp as Date,
        p.name as Patient,
        s.cancer_type as 'Type',
        s.prediction_result as Result,
        s.confidence as Confidence
    FROM scans s
    LEFT JOIN patients p ON s.patient_id = p.id
    ORDER BY s.timestamp DESC
    LIMIT 10
    """
    history_df = pd.read_sql_query(query, conn)
    conn.close()

    if not history_df.empty:
        # Summary Row at the top
        col1, col2, col3 = st.columns(3)
        with col1:
             st.metric("Total Scans", len(history_df))
        with col2:
             cancerous_count = len(history_df[history_df['Result'].str.contains('Cancerous|Malignant|ACA|SCC', case=False, na=False)])
             st.metric("Infections Detected", cancerous_count)
        with col3:
             avg_conf = history_df['Confidence'].mean()
             st.metric("Avg. Confidence", f"{avg_conf*100:.1f}%")
        
        with st.expander("📋 View Recent Clinical Diagnostic History", expanded=False):
            st.dataframe(
                history_df,
                column_config={
                    "Confidence": st.column_config.ProgressColumn(
                        "Confidence",
                        format="%.2f",
                        min_value=0,
                        max_value=1,
                    )
                },
                use_container_width=True
            )
    else:
        st.info("No clinical scans recorded yet. Perform a scan in the 'Detection' section to see live data summary here.")

    st.markdown("---")
    st.markdown("""
        Review the technical validation metrics of our deep learning models below. These visualizations represent 
        the model's learning curve and classification reliability across our clinical datasets.
    """)
    
    tab1, tab2 = st.tabs(["🫁 Lung Cancer", "📸 Skin Cancer"])

    with tab1:
        st.markdown('<h2 class="sub-title">Lung Cancer Model Metrics</h2>', unsafe_allow_html=True)
        
        test_acc = load_test_accuracy('json_files/lung cancer/test_accuracy_and_training_history.json')
        if test_acc:
            st.markdown(f"""
                <div class="feature-box" style="text-align: center; border-left: none; border-top: 4px solid #eb1948;">
                    <span style="font-size: 0.9rem; opacity: 0.6; display: block;">TEST ACCURACY</span>
                    <span style="font-size: 2.5rem; font-weight: 800; color: #eb1948;">{test_acc * 100:.2f}%</span>
                </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        history = load_training_history('json_files/lung cancer/training_history.json')
        with col1:
            plot_training_accuracy(history)
        with col2:
            plot_training_loss(history)
            
        cm = np.array([[515, 0, 0], [0, 492, 0], [0, 0, 493]])
        plot_confusion_matrix(cm, ['Lung ACA', 'Benign', 'Lung SCC'])

    with tab2:
        st.markdown('<h2 class="sub-title">Skin Cancer Model Metrics</h2>', unsafe_allow_html=True)
        
        test_acc = load_test_accuracy('json_files/skin cancer/test_accuracy.json')
        if test_acc:
            st.markdown(f"""
                <div class="feature-box" style="text-align: center; border-left: none; border-top: 4px solid #eb1948;">
                    <span style="font-size: 0.9rem; opacity: 0.6; display: block;">TEST ACCURACY</span>
                    <span style="font-size: 2.5rem; font-weight: 800; color: #eb1948;">{test_acc * 100:.2f}%</span>
                </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        history = load_training_history('json_files/skin cancer/training_history.json')
        with col1:
            plot_training_accuracy(history)
        with col2:
            plot_training_loss(history)
            
        cm = np.array([[447, 53], [135, 365]])
        plot_confusion_matrix(cm, ['Benign', 'Malignant'])


if __name__ == "__main__":
    app()
