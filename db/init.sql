-- Init script for Postgres
CREATE SCHEMA IF NOT EXISTS experimentation;
CREATE SCHEMA IF NOT EXISTS raw;

-- 1) Experiment Registry
CREATE TABLE IF NOT EXISTS experimentation.experiment_registry (
    experiment_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    owner VARCHAR(255),
    hypothesis TEXT,
    start_date DATE,
    end_date DATE,
    population_definition TEXT,
    primary_metric VARCHAR(50),
    guardrails JSONB,
    segments JSONB,
    planned_power FLOAT,
    planned_mde FLOAT,
    status VARCHAR(50) DEFAULT 'draft', -- draft, running, stopped, analyzed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2) Experiment Observations (Unit Level)
CREATE TABLE IF NOT EXISTS experimentation.experiment_observations (
    row_id SERIAL PRIMARY KEY,
    experiment_id INT REFERENCES experimentation.experiment_registry(experiment_id),
    unit_id VARCHAR(255), -- User ID or Cookie ID
    treatment INT, -- 0 or 1
    features JSONB, -- store f0..f11 as json
    outcome_visit INT,
    outcome_conversion INT,
    batch_date DATE
);

CREATE INDEX IF NOT EXISTS idx_obs_exp_id ON experimentation.experiment_observations(experiment_id);
CREATE INDEX IF NOT EXISTS idx_obs_unit_id ON experimentation.experiment_observations(unit_id);

-- 3) Experiment Results (Aggregated)
CREATE TABLE IF NOT EXISTS experimentation.experiment_results (
    result_id SERIAL PRIMARY KEY,
    experiment_id INT REFERENCES experimentation.experiment_registry(experiment_id),
    metric_name VARCHAR(50),
    effect_estimate FLOAT,
    ci_low FLOAT,
    ci_high FLOAT,
    p_value FLOAT,
    method VARCHAR(50), -- t-test, cuped, etc
    segment VARCHAR(100), -- 'all' or specific segment
    computed_at TIMESTAMP DEFAULT NOW()
);

-- 4) Health Checks
CREATE TABLE IF NOT EXISTS experimentation.experiment_health_checks (
    check_id SERIAL PRIMARY KEY,
    experiment_id INT REFERENCES experimentation.experiment_registry(experiment_id),
    check_name VARCHAR(50), -- SRM, Missingness
    status VARCHAR(20), -- PASS, WARN, FAIL
    details JSONB,
    computed_at TIMESTAMP DEFAULT NOW()
);

-- 5) Uplift Policy Results
CREATE TABLE IF NOT EXISTS experimentation.uplift_policy_results (
    policy_id SERIAL PRIMARY KEY,
    experiment_id INT REFERENCES experimentation.experiment_registry(experiment_id),
    model_name VARCHAR(50),
    qini_auc FLOAT,
    uplift_auc FLOAT,
    expected_value_lift FLOAT,
    targeting_fraction FLOAT,
    computed_at TIMESTAMP DEFAULT NOW()
);

-- 6) Decision Reports
CREATE TABLE IF NOT EXISTS experimentation.decision_reports (
    report_id SERIAL PRIMARY KEY,
    experiment_id INT REFERENCES experimentation.experiment_registry(experiment_id),
    decision VARCHAR(50), -- SHIP, HOLD, ITERATE
    rationale_markdown TEXT,
    risks_and_guardrails TEXT,
    next_steps TEXT,
    generated_at TIMESTAMP DEFAULT NOW()
);
