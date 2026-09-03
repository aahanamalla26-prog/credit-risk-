-- Credit Risk Assessment Platform -- MySQL schema
-- Note: the local/demo backend (app.py) runs on SQLite for zero-setup local
-- development. This schema is the production-equivalent MySQL DDL with the
-- same structure. To run against real MySQL, swap app.py's sqlite3 calls for
-- a MySQL connector (e.g. PyMySQL or mysql-connector-python) -- the table
-- shape and queries are unchanged.

CREATE DATABASE IF NOT EXISTS credit_risk_platform;
USE credit_risk_platform;

CREATE TABLE IF NOT EXISTS applicants (
    id                  BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    age                 INT NOT NULL,
    annual_income       DECIMAL(14,2) NOT NULL,
    employment_years    DECIMAL(5,1) NOT NULL,
    loan_amount         DECIMAL(14,2) NOT NULL,
    credit_score        SMALLINT NOT NULL,
    existing_debt       DECIMAL(14,2) NOT NULL,
    num_open_accounts   SMALLINT NOT NULL,
    previous_defaults   TINYINT(1) NOT NULL DEFAULT 0,
    loan_purpose        VARCHAR(50) NOT NULL,
    predicted_risk      ENUM('Low', 'Medium', 'High') NOT NULL,
    risk_probabilities  JSON NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'submitted',
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_predicted_risk (predicted_risk),
    INDEX idx_created_at (created_at),
    CONSTRAINT chk_credit_score CHECK (credit_score BETWEEN 300 AND 850)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
