# 🎗️ Cancer Detective: Full System Setup & Deployment Guide

This guide provides the complete blueprint for deploying the **Cancer Detective** Clinical Dashboard on any Windows, macOS, or Linux machine.

---

## 📋 Prerequisites
Ensure the target machine has the following:
1.  **Python 3.9 - 3.11** (Download from [python.org](https://www.python.org/downloads/))
2.  **6GB+ RAM** (To handle the Deep Learning models)
3.  **Internet Access** (For initial component installation)

---

## 🛠️ Step-by-Step Installation

### 1. Clone or Copy the Project
You can either clone the repository directly or copy the project folder:

**Option A: Clone via Git (Recommended)**
```bash
git clone https://github.com/anshuman444/cancer-detetction.git
cd cancer-detetction
```

**Option B: Manual Copy**
Copy the entire `cancer detection` directory to the target machine. Ensure the `models/` folder contains the `.h5` files.

### 2. Environment Configuration
Navigate to the project root in your terminal (Command Prompt, PowerShell, or Terminal):
```bash
cd "path/to/cancer detection"
```

Create and activate a clean virtual environment:
```bash
# Create environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Dependency Installation
Install the clinical core and AI engines:
```bash
pip install -r requirements.txt
```

### 4. Database & System Initialization
Initialize the clinical database to set up patient records and scan history:
```bash
python database.py
```
*Note: This creates the `cancer_detection.db` file required for 'History' and 'Patients' modules.*

---

## 🏃‍♂️ Launching the Dashboard

Execute the following command to start the Clinical Server:
```bash
streamlit run app.py
```

The system will automatically launch in your browser at:
`http://localhost:8501`

---

## 📁 Critical System Folders
For optimal performance, verify these directories are present:
- `app.py`: Main system orchestrator.
- `models/`: Contains the pre-trained `.h5` neural networks.
- `images/`: Stores the hero banner and clinical iconography.
- `json_files/`: Contains training history metrics for the Analytics Dashboard.
- `database.py`: The core data initialization script.

---

## ⚠️ Troubleshooting & Support
- **Model Loading Errors**: Ensure the `models/` folder is NOT empty and files are named exactly `lung_cancer_model.h5` and `skin_cancer_model.h5`.
- **Layout Alignment**: The dashboard is optimized for **Wide View**. If it looks narrow, ensure your browser window is maximized.
- **Missing Data**: If the 'Visualizing' or 'Patients' sections are empty, ensure you have run `python database.py` at least once.

---
**Prepared for Academic & Clinical Presentation.**
