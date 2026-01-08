# Case Study: Building a Production-Grade Experimentation Platform
**Role:** Analytics Engineer / Data Analyst
**Status:** Completed (January 2026)

---

## 1. Executive Summary
Traditional A/B testing often answers the wrong question ("Does this work on average?") rather than the profitable question ("Who does this work for?"). 

To demonstrate advanced decision science capabilities, I architected and built an end-to-end **Experimentation & Incrementality Platform**. This system automates the lifecycle of causal inference—from data ingestion to decision reporting—enabling marketing teams to identify "Persuadable" customers and double campaign ROI through **Uplift Modeling**.

---

## 2. The Business Problem
Marketing campaigns usually waste budget on two types of users:
1.  **Sure Things**: Customers who would have bought anyway (Subsidy Cost).
2.  **Lost Causes**: Customers who will never buy (Waste).
3.  **Sleeping Dogs**: Customers who churn *because* of the ad (Negative Impact).

A standard A/B test cannot distinguish these groups. It only reports the "Average Treatment Effect" (ATE). To optimize ROI, we need to target only the **Persuadables** (those who buy *because* of the ad).

## 3. The Technical Solution
I built a modular, containerized data pipeline using **Dagster** to orchestrate the flow of data through four critical layers:

### A. Ingestion Layer (Robustness)
-   **Source**: Automated extraction of the **Kevin Hillstrom Email Marketing Dataset** (64k users).
-   **Validation**: Implemented schema enforcement on load to ensure data integrity.
-   **Fallback**: Engineered a synthetic data generator to allow disconnected local development.

### B. Trust Layer (validity)
-   **SRM Checks**: Before running any stats, the pipeline executes a **Sample Ratio Mismatch** test (Chi-Square).
-   **Logic**: If the Treatment/Control split deviates significantly from 50/50 (p < 0.001), the pipeline **halts automatically**. This prevents business decisions based on bug-ridden data.

### C. Intelligence Layer (Inference)
-   **Variance Reduction**: Implemented **CUPED** (Controlled-Experiment Using Pre-Experiment Data) using pre-exposure covariates (`history`, `recency`). This reduced metric variance, increasing statistical power without adding users.
-   **Uplift Modeling**: Trained a **Meta-Learner (S-Learner)** using `scikit-uplift` to predict individual conditional treatment effects (CATE).

### D. Reporting Layer (Visibility)
-   **Automated Docs**: The pipeline generates a human-readable Markdown report (`experiment_1_report.md`) with a clear "SHIP/HOLD" recommendation.
-   **Dashboarding**: Deployed **Apache Superset** for real-time visual monitoring of key metrics (Conversion Rate, Visit Rate).

---

## 4. Key Results (Hillstrom Analysis)
In the "Mens E-Mail" campaign experiment:

| Metric | Result | Insight |
|---|---|---|
| **A/B Lift** | **+0.68%** (p < 0.0001) | The email works on average, but the margin is slim. |
| **Uplift Strategy** | **+5.5%** (Estimated) | Targeting only the top 30% "Persuadables" yields 8x higher efficiency. |

**Conclusion**: Blanket marketing is inefficient. Using this platform's Uplift Model to target specific high-intent segments (e.g., Rural/Suburban recent buyers) significantly improves ROI.

---

## 5. Technology Stack
This project demonstrates "Full-Stack Data Science":
-   **Orchestration**: Dagster (Python-based asset definitions).
-   **Database**: PostgreSQL (Structured storage for logs and results).
-   **Containerization**: Docker & Docker Compose (Wait-for-it scripts, network isolation).
-   **Analysis**: `pandas`, `scipy.stats`, `scikit-uplift`.
-   **Visualization**: Apache Superset (connected via internal Docker network).
-   **CI/CD**: GitHub Actions (Linting with Ruff, Testing with Pytest).

## 6. Challenges Overcome
1.  **Networking**: Configuring Superset running in one container to talk to Postgres in another (Solved via Docker Service Discovery: `host=postgres`).
2.  **Data Quality**: The initial dataset had subtle imbalances. I engineered the **SRM Check** asset to catch these issues upstream before they corrupted the analysis.
3.  **Reproducibility**: Ensuring the sophisticated stats (CUPED) worked identically on my local machine and the CI environment.

---

## 7. Future Roadmap
-   **Auto-Deployment**: Connect the "SHIP" decision to a webhook that triggers the email campaign automatically.
-   **Switchback Testing**: Add support for time-based marketplace experiments.
-   **Bayesian Inference**: Add a module for Bayesian A/B testing (PyMC) to output probability distributions instead of point estimates.
