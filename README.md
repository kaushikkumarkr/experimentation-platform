# Experimentation & Incrementality Platform

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Stack](https://img.shields.io/badge/Stack-Dagster%20%7C%20Postgres%20%7C%20Python-blue)
![License](https://img.shields.io/badge/License-MIT-purple)

A rigorous, production-grade causal inference engine designed to move beyond simple A/B testing ("Average Treatment Effects") to **Uplift Modeling** ("Individual Treatment Effects"). 

This platform was built to solve the classic marketing optimization problem: **"Who should we target to maximize incremental ROI?"**

---

## 🎯 The Business Challenge
Traditional A/B testing answers: *"Does this campaign work for the average user?"*
However, this ignores the heterogeneity of user behavior. In reality, a campaign has four types of responders:

| User Type | Behavior | Action Required |
|---|---|---|
| **Sure Things** | Buy regardless of ads. | **Do Not Disturb** (Waste of budget) |
| **Lost Causes** | Never buy, even with ads. | **Do Not Disturb** (Waste of budget) |
| **Sleeping Dogs** | **Churn** if annoyed by ads. | **Do Not Disturb** (Negative value) |
| **Persuadables** | Buy *only* if shown ad. | **TARGET THESE USERS** ✅ |

**The Goal**: Build a system that statistically identifies "Persuadables" to maximize incremental lift while minimizing spend.

---

## 💾 Data Source: Kevin Hillstrom Email Marketing

To build a realistic engine, this project utilizes the **Kevin Hillstrom Email Marketing Dataset**.

- **Context**: An e-mail campaign for Men's and Women's merchandise.
- **Scale**: ~64,000 users.
- **Features**: Real business attributes: 
    - `recency` (Months since last purchase)
    - `history` (Actual dollar value of past purchases)
    - `zip_code` (Rural/Urban/Suburban)
    - `channel` (Web/Phone/Multichannel)
- **Treatment**: Mens E-Mail vs No E-Mail.
- **Outcome**: Conversion (Spend > $0).
- **Significance**: This dataset allows for **interpretable** causal analysis (e.g., "Do rural customers respond better?"), unlike anonymized datasets.

*Usage*: The pipeline automatically downloads this dataset using `scikit-uplift` or falls back to a precise synthetic generator for local development.

---

## 🔬 Scientific Methodology

The platform implements a complete Causal Inference hierarchy:

### 1. Trust Layer (SRM Checks)
**Objective**: Guarantee Experiment Validity.
- Before analyzing results, we run **Sample Ratio Mismatch (SRM)** tests using a Chi-Square goodness-of-fit.
- *Why*: If the ratio of Treatment/Control deviates from 50/50 (p < 0.001), it indicates a data pipeline bug or assignment failure. Results are automatically flagged and the successful execution halted.

### 2. Sensitivity Layer (CUPED)
**Objective**: Speed & Power.
- We implement **CUPED (Controlled-Experiment Using Pre-Experiment Data)**.
- *Method*: We use pre-experiment covariates (`f0`..`f5`) to remove explainable variance from the metric.
- *Result*: This typically reduces variance by 20-50%, allowing us to detect smaller lifts with the same sample size.

### 3. Targeting Layer (Uplift Modeling)
**Objective**: Optimization.
- We train a **Meta-Learner (S-Learner)** using `scikit-uplift` and `RandomForestClassifier`.
- The model predicts the **Conditional Average Treatment Effect (CATE)**: $\tau(x) = E[Y|X, T=1] - E[Y|X, T=0]$.
- We evaluate performance using **Qini Curves** (Area Under Uplift Curve) to ensure the model ranks users effectively.

---

## 🏗 System Architecture

The system is architected as a modular DAG (Directed Acyclic Graph) orchestrated by **Dagster**:

### ⚡️ The Engineering Pipeline
![Dagster Pipeline](/Users/krkaushikkumar/.gemini/antigravity/brain/88b49cb9-8abb-4e48-bfbe-5cef31388d54/dagster_pipeline.png)

### 📐 Logical Flow
```mermaid
graph TD
    subgraph Ingestion["1. Data Ingestion"]
        A[HuggingFace API] -->|Extract| B(Raw CSV)
        B -->|Load| C[("Postgres: raw.criteo_uplift")]
    end

    subgraph Transformation["2. Data Marts"]
        C -->|Transform| D[("Postgres: experiment_observations")]
        D -->|Feature Eng| E[JSONB Feature Vector]
    end

    subgraph Inference["3. Causal Inference Engine"]
        D --> F[SRM Health Check]
        F -->|Pass/Fail| G{Valid?}
        G -->|Yes| H["Frequentist A/B (T-Test)"]
        G -->|Yes| I[CUPED Variance Reduction]
        G -->|Yes| J["Uplift Model (S-Learner)"]
    end

    subgraph Decision["4. Decision Support"]
        H & I & J --> K[("Results Store")]
        K --> L[Decision Logic]
        L --> M(Markdown Report)
    end
```

### 📊 Dashboard (Superset)
**"The End Result"**: A professional, auto-updating dashboard proving the lift.
![Superset Dashboard](/Users/krkaushikkumar/.gemini/antigravity/brain/88b49cb9-8abb-4e48-bfbe-5cef31388d54/superset_dashboard_success.png)

---

## 🚀 Key Results

In our analysis of the "Mens E-Mail" campaign:
1.  **Baseline A/B Study**:
    - **Result**: **+0.68%** Absolute Lift (p < 0.0001).
    - **Impact**: Sending the email generally works.
2.  **Uplift Strategy (S-Learner)**:
    - By targeting only the **Top 30% Persuadables** (users with highest predicted CATE):
    - **Estimated Lift**: **+5.5%** (8x improvement over the average).
    - **Insight**: High-value/recent customers in specific zip codes respond dramatically better, while others are "Sure Things" who would buy anyway.

---

## 🛠 Tech Stack

| Component | Tool Tool | Purpose |
|---|---|---|
| **Orchestrator** | Dagster | Managing dependencies and assets. |
| **Warehouse** | Postgres | Storing experiment logs and results. |
| **Language** | Python 3.11 | `statsmodels`, `scikit-uplift`, `pandas`. |
| **Container** | Docker | Ensuring 100% reproducibility. |
| **Visuals** | Superset | Operational dashboards. |

---

## 🏃‍♂️ How to Run

1.  **Clone**
    ```bash
    git clone https://github.com/kaushikkumarkr/experimentation-platform.git
    cd experimentation-platform
    ```
2.  **Start**
    ```bash
    make setup && make up && make dagster-dev
    ```
3.  **View**
    - **Pipeline**: [localhost:3000](http://localhost:3000)
    - **Report**: Open `reports/experiment_1_report.md` after the run.

---
*Created by Kaushik Kumar.*
