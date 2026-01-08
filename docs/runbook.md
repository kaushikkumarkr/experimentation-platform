# Experimentation Platform Runbook

## Common Issues

### 1. Data Ingestion Fails
- **Symptom**: `load_to_postgres.py` errors.
- **Fix**: Check internet connection for Hugging Face download. If slow, use the cached `data/criteo_sample.csv` or reduce `--sample-size` in `dagster_app/assets_ingest.py`.

### 2. SRM Failures
- **Symptom**: `experiment_health_checks` status is FAIL.
- **Action**: Do not analyze. Check upstream assignment logs. Check if a segment of users was excluded non-randomly.

### 3. Pipeline Latency
- **Optimization**: The current implementation loads data via pandas `to_sql`. For production (>10M rows), switch to `COPY` command or dbt external tables.

## Maintenance
- **Backups**: `pg_dump experimentation_db > backup.sql`.
- **Updates**: `pip install -r requirements.txt` (or pyproject.toml).
