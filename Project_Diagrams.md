# 🏥 Cancer Detection: Project Architecture & ER Diagrams

This document summarizes the technical design of the Cancer Detection system. It includes the software architecture and the database relationship models.

---

## 📐 1. System Architecture
This diagram illustrates the flow of data from the user interface through the AI processing layer to the final storage.

```mermaid
graph TD
    User([User / Doctor]) -->|Uploads Image| UI[Streamlit Frontend]
    
    subgraph "Application Layer (Python)"
        UI --> Auth[Authentication Module]
        UI --> Logic[Detection Logic]
        UI --> Viz[Visualization Module]
    end
    
    subgraph "AI Engine (Deep Learning)"
        Logic -->|Preprocessed Pixels| LungModel["Lung CNN (.h5)"]
        Logic -->|Preprocessed Pixels| SkinModel["Skin CNN (.h5)"]
    end
    
    subgraph "Data Storage"
        Auth -->|Read/Write| DB[(SQLite Database)]
        Logic -->|Save Results| DB
        Viz -->|Read History| JSON[JSON Training Files]
    end
    
    LungModel -->|Predictions| Logic
    SkinModel -->|Predictions| Logic
    Logic -->|Confidence Scores| UI
```

---

## 🗄️ 2. Modern ER Model
A relational map showing the connections between Users, Patients, Scans, and Reports.

```mermaid
erDiagram
    USERS {
        int id PK
        string username
        string name
        string role
    }
    
    PATIENTS {
        int id PK
        string name
        int age
        string gender
    }
    
    SCANS {
        int id PK
        int patient_id FK
        int user_id FK
        string cancer_type
        string prediction_result
        float confidence
    }
    
    REPORTS {
        int id PK
        int patient_id FK
        int user_id FK
        string report_text
    }

    USERS ||--o{ SCANS : "performs"
    USERS ||--o{ REPORTS : "generates"
    PATIENTS ||--o{ SCANS : "undergoes"
    PATIENTS ||--o{ REPORTS : "has"
```

---

## 🎨 3. Classical ER Diagram (Chen Notation)
A traditional representation using standard symbols (Rectangles for Entities, Ovals for Attributes, Diamonds for Relationships).

```mermaid
flowchart TD
    %% Entities
    User[/"User"\]
    Patient[/"Patient"\]
    Scan[/"Scan"\]
    Report[/"Report"\]
    
    %% Relationships
    Performs{{"Performs"}}
    Undergoes{{"Undergoes"}}
    Generates{{"Generates"}}
    Has{{"Has"}}
    
    %% User Attributes
    U_ID((ID)) --- User
    U_Username((Username)) --- User
    U_Role((Role)) --- User
    
    %% Patient Attributes
    P_ID((ID)) --- Patient
    P_Name((Name)) --- Patient
    P_Age((Age)) --- Patient
    
    %% Scan Attributes
    S_ID((ID)) --- Scan
    S_Type((Cancer Type)) --- Scan
    S_Conf((Confidence)) --- Scan
    
    %% Connections
    User --- Performs --- Scan
    Patient --- Undergoes --- Scan
    User --- Generates --- Report
    Patient --- Has --- Report

    %% Styling
    style User fill:#fff,stroke:#333,stroke-width:2px
    style Patient fill:#fff,stroke:#333,stroke-width:2px
    style Scan fill:#fff,stroke:#333,stroke-width:2px
    style Report fill:#fff,stroke:#333,stroke-width:2px
    style Performs fill:#fff,stroke:#333,stroke-width:2px
    style Undergoes fill:#fff,stroke:#333,stroke-width:2px
    style Generates fill:#fff,stroke:#333,stroke-width:2px
    style Has fill:#fff,stroke:#333,stroke-width:2px
```
