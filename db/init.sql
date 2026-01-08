-- Create schemas
CREATE SCHEMA IF NOT EXISTS experimentation;
CREATE SCHEMA IF NOT EXISTS raw;

-- 1. Experiment Registry (Metadata)
CREATE TABLE IF NOT EXISTS experimentation.experiment_registry (
    experiment_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'planning', -- planning, active, analyzed, archived
    primary_metric VARCHAR(100),
    hypothesis TEXT
);

-- 2. Experiment Observations (The "Mart")
-- Optimized for analysis. One row per user per experiment.
CREATE TABLE IF NOT EXISTS experimentation.experiment_observations (
    experiment_id INT REFERENCES experimentation.experiment_registry(experiment_id),
    unit_id VARCHAR(255),
    treatment INT, -- 0 = Control, 1 = Treatment
    features JSONB, -- Pre-experiment covariates for CUPED/Uplift
    outcome_visit INT, -- Auxiliary metric
    outcome_conversion INT, -- Primary metric (spend > 0)
    batch_date DATE
);

-- 3. Results Store (Aggregated stats)
CREATE TABLE IF NOT EXISTS experimentation.experiment_results (
    experiment_id INT REFERENCES experimentation.experiment_registry(experiment_id),
    metric_name VARCHAR(100),
    method VARCHAR(50), -- z_test, t_test, cuped, bayesian
    segment VARCHAR(100) DEFAULT 'all',
    effect_estimate FLOAT, -- Lift or Difference
    ci_low FLOAT,
    ci_high FLOAT,
    p_value FLOAT,
    sample_size INT,
    computed_at TIMESTAMP DEFAULT NOW()
);

-- 4. Health Checks (SRM, etc.)
CREATE TABLE IF NOT EXISTS experimentation.experiment_health_checks (
    experiment_id INT REFERENCES experimentation.experiment_registry(experiment_id),
    check_name VARCHAR(100),
    status VARCHAR(50), -- PASS, FAIL, WARN
    details JSONB, -- P-values, observed counts
    computed_at TIMESTAMP DEFAULT NOW()
);

-- 5. Uplift/Policy Results
CREATE TABLE IF NOT EXISTS experimentation.uplift_policy_results (
    experiment_id INT REFERENCES experimentation.experiment_registry(experiment_id),
    model_name VARCHAR(100),
    qini_auc FLOAT,
    uplift_auc FLOAT,
    expected_value_lift FLOAT, -- e.g. "Expected lift matches random targeting * 1.5"
    targeting_fraction FLOAT, -- e.g. 0.3 (Top 30%)
    computed_at TIMESTAMP DEFAULT NOW()
);

-- 6. Decision Reports
CREATE TABLE IF NOT EXISTS experimentation.decision_reports (
    experiment_id INT REFERENCES experimentation.experiment_registry(experiment_id),
    decision VARCHAR(50), -- SHIP, HOLD, ITERATE
    rationale_markdown TEXT,
    risks_and_guardrails TEXT,
    next_steps TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- RAW DATA (Hillstrom)
DROP TABLE IF EXISTS raw.criteo_uplift;
DROP TABLE IF EXISTS raw.hillstrom;

CREATE TABLE raw.hillstrom (
    recency INT,
    history_segment VARCHAR(100),
    history FLOAT,
    mens INT,
    womens INT,
    zip_code VARCHAR(50),
    newbie INT,
    channel VARCHAR(50),
    segment VARCHAR(50), -- Mens E-Mail, Womens E-Mail, No E-Mail
    visit INT,
    conversion INT,
    spend FLOAT
);
