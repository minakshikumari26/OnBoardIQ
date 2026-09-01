-- OnBoardIQ database schema
-- Run once:  psql -U postgres -d loan_db -f backend/db/schema.sql
-- WARNING: this drops old loan tables (users, loans) from previous version.

DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS onboarding_applications CASCADE;
DROP TABLE IF EXISTS loans CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

CREATE TABLE customers (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(120) NOT NULL,
    pan             VARCHAR(10) UNIQUE NOT NULL,
    aadhaar_masked  VARCHAR(14),
    dob             DATE,
    mobile          VARCHAR(10),
    email           VARCHAR(120),
    monthly_income  INT,
    employment_type VARCHAR(30),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE onboarding_applications (
    id                 SERIAL PRIMARY KEY,
    customer_id        INT REFERENCES customers(id),
    decision           VARCHAR(20),
    reason             TEXT,
    kyc_status         VARCHAR(20),
    document_status    VARCHAR(20),
    compliance_status  VARCHAR(20),
    risk_level         VARCHAR(10),
    risk_score         INT,
    created_at         TIMESTAMP DEFAULT NOW()
);

CREATE TABLE documents (
    id              SERIAL PRIMARY KEY,
    application_id  INT REFERENCES onboarding_applications(id),
    document_type   VARCHAR(20),
    extracted_text  TEXT,
    is_valid        BOOLEAN,
    uploaded_at     TIMESTAMP DEFAULT NOW()
);
