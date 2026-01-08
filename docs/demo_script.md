# Experimentation Platform Demo Script (5 Minutes)

#### 1. Introduction (30s)
"Hi, I'm showcasing a production-grade Experimentation Platform built with Python, Dagster, and Postgres. It supports the full lifecycle: from ingestion to advanced uplift modeling."

#### 2. Architecture & Ingestion (1 min)
- **Show**: `docker-compose.yml` (Postgres, Superset).
- **Show**: Dagster UI (`localhost:3000`).
- **Action**: Run the `criteo_data_file` and `experiment_observations_mart` assets.
- **Explain**: "We ingest raw data, sample it for dev speed, and verify data quality automatically."

#### 3. Health Checks & Reliability (1 min)
- **Action**: Show `experiment_health_checks_asset` execution.
- **Explain**: "Before analyzing, we run rigorous SRM checks. If this fails (p < 0.001), the experiment typically auto-holds using our decision engine logic."

#### 4. Advanced Analysis (1.5 min)
- **Action**: Show `experiment_results_asset`.
- **Highlight**: "We run standard Frequentist A/B tests (Welch's t-test)."
- **Highlight**: "We also run CUPED to reduce variance using pre-experiment covariates, increasing our sensitivity."
- **Highlight**: "Finally, we train Uplift Models (S-Learner) to find 'persuadable' users."

#### 5. Decision & Reporting (1 min)
- **Action**: Open `reports/experiment_1_report.md`.
- **Explain**: "The system auto-generates this decision document. It recommends SHIP/HOLD based on significance and guardrails."
- **Closing**: "This platform is containerized, reproducible, and robust."
