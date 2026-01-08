# Experimentation & Incrementality Platform

A production-grade platform for running A/B tests, CUPED variance reduction, and Uplift Modeling.

## Tech Stack
- **Postgres**: Data Warehouse & Metadata Store
- **Dagster**: Orchestration
- **Python**: Analysis (statsmodels, scikit-uplift)
- **Superset**: Dashboards
- **Docker**: Containerization

## Architecture

```mermaid
graph TD
    subgraph Ingestion
        A[HuggingFace/Synthetic] -->|download_data.py| B(CSV File)
        B -->|load_to_postgres.py| C[(Postgres: raw.criteo_uplift)]
    end

    subgraph Data Marts
        C -->|dbt/Pandas| D[(Postgres: experiment_observations)]
        D -->|JSONB Features| E[Feature Extraction]
    end

    subgraph Analysis Engine
        D --> F[SRM Checks]
        F -->|Pass/Fail| G{Health Check}
        G -->|Pass| H[Frequentist A/B]
        G -->|Pass| I[CUPED Variance Reduction]
        G -->|Pass| J[Uplift Modeling (S-Learner)]
    end

    subgraph Reporting
        H --> K[(Postgres: Results)]
        I --> K
        J --> K
        K --> L[Decision Engine]
        L --> M(Markdown Decision Report)
    end
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.10+

### Setup
1. **Clone & Install**
   ```bash
   make setup    # copy .env
   make install  # pip install dependencies
   ```

2. **Start Infrastructure**
   ```bash
   make up       # start Postgres & Superset
   ```

3. **Run Orchestration**
   ```bash
   make dagster-dev
   ```
   Open [localhost:3000](http://localhost:3000) for Dagster.

4. **Access UI**
   - **Superset**: [localhost:8088](http://localhost:8088) (Default: admin/admin)

## Project Structure
- `/analysis`: Statistical code (A/B, CUPED, Uplift)
- `/orchestration`: Dagster assets & jobs
- `/db`: SQL schemas and init scripts
- `/scripts`: Utility scripts
