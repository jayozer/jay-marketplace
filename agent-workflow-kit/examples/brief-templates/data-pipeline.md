# Data Pipeline Brief Template

## Template

```
Goal: Deliver [DATA PIPELINE/ETL JOB].
Context: [DATA FRAMEWORK/PROJECT], [DATA SOURCES], [DESTINATION], and [SCHEDULING SYSTEM].
Output: [PIPELINE CODE/CONFIGURATION/DOCUMENTATION] implementing [TRANSFORMATIONS], [VALIDATION], and [MONITORING].
Boundaries: Preserve [SOURCE/DESTINATION CONTRACTS]; require approval for [PRODUCTION DATA OR DEPLOYMENT].
Verification: [FIXTURE RUN], [DATA QUALITY CHECKS], [IDEMPOTENCY CHECK], and lineage review.
```

## Example: E-commerce Sales Analytics Pipeline

```
Goal: Deliver a daily sales analytics pipeline in the existing Airflow project.
Context: PostgreSQL transactions, Python/Pandas transforms, Snowflake, dbt, and Datadog.
Output: Airflow DAGs, transformations, dbt models, validation, monitoring, and lineage documentation for daily sales, customer segments, and product performance.
Boundaries: Use test fixtures rather than production data and do not deploy.
Verification: Run the DAG against fixtures, validate completeness and accuracy, prove idempotency, and review the destination schema.
```

## Field Explanations

- **OUTCOME:** The data pipeline or ETL job being built
- **CONTEXT:** Data framework (Airflow, dbt, Spark, etc.) and project context
- **CORE DELIVERABLES:** Extraction logic, transformations, loading operations, validation
- **BEHAVIOR:** Scheduling, error handling, retry logic, data quality checks
- **QUALITY BAR:** Data accuracy, completeness, timeliness, reliability
- **ENVIRONMENT:** Data sources, destinations, processing infrastructure, monitoring
- **ARTIFACT:** Pipeline code, configuration files SQL/models, documentation

## Common Data Pipeline Constraints

- Handle data incrementally when possible
- Implement idempotent operations
- Validate data at each stage
- Handle schema evolution gracefully
- Monitor for data quality issues
- Log pipeline execution metrics
- Implement proper error handling and retries
- Document data lineage and transformations
