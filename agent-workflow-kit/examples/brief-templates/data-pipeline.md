# Data Pipeline Brief Template

## Template

```
Build or deliver [DATA PIPELINE/ETL JOB] in [DATA FRAMEWORK/PROJECT].
It should include [DATA SOURCES], with [TRANSFORMATION LOGIC], [VALIDATION RULES], and [DESTINATION SCHEMA].
Make it meet [DATA QUALITY STANDARDS], using [PROCESSING FRAMEWORK], [SCHEDULING SYSTEM], and [MONITORING/ALERTING].
Output as [PIPELINE CODE/CONFIGURATION FILES/DOCUMENTATION].
```

## Example: E-commerce Sales Analytics Pipeline

```
Build or deliver daily sales analytics pipeline in Apache Airflow project.
It should include data extraction from PostgreSQL transaction database, transformation to aggregate metrics (daily sales, customer segments, product performance), validation for data completeness and accuracy, and loading to analytics warehouse (Snowflake).
Make it meet enterprise data quality standards with 99.9% uptime, using Python with Pandas for transformations, Airflow for scheduling, and Datadog for monitoring/alerting.
Output as Airflow DAGs, transformation scripts, dbt models, and pipeline documentation.
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
