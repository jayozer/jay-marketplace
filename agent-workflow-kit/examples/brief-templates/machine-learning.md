# Machine Learning Brief Template

## Template

```
Build or deliver [ML MODEL/PIPELINE] in [ML FRAMEWORK/PROJECT].
It should include [MODEL ARCHITECTURE], with [TRAINING DATA], [FEATURE ENGINEERING], and [EVALUATION METRICS].
Make it meet [MODEL PERFORMANCE TARGETS], using [TRAINING FRAMEWORK], [DEPLOYMENT STRATEGY], and [MONITORING/DRIFT DETECTION].
Output as [MODEL ARTIFACTS/TRAINING CODE/INFERENCE API].
```

## Example: Customer Churn Prediction Model

```
Build or deliver customer churn prediction model in scikit-learn project.
It should include gradient boosting classifier architecture, with training data from customer database (features: usage patterns, support tickets, engagement metrics), feature engineering for temporal patterns, and evaluation metrics (AUC-ROC 0.85+, precision 0.80+, recall 0.75+).
Make it meet production model standards with explainability requirements, using scikit-learn with XGBoost, FastAPI for inference, and Evidently AI for monitoring/drift detection.
Output as trained model artifacts, training pipeline code, FastAPI inference endpoint, and model card documentation.
```

## Field Explanations

- **OUTCOME:** The ML model or pipeline being built
- **CONTEXT:** ML framework (scikit-learn, TensorFlow, PyTorch, etc.) and project context
- **CORE DELIVERABLES:** Model architecture, training code, preprocessing, evaluation
- **BEHAVIOR:** Training process, hyperparameter tuning, inference latency, batch vs real-time
- **QUALITY BAR:** Performance metrics, explainability, fairness, robustness
- **ENVIRONMENT:** Training infrastructure, deployment target, monitoring system
- **ARTIFACT:** Model files, training scripts, inference code, documentation

## Common ML Development Constraints

- Use reproducible training procedures
- Implement proper train/validation/test splits
- Monitor for data drift and model drift
- Ensure model explainability where required
- Handle class imbalance appropriately
- Implement proper feature versioning
- Document model cards and lineage
- Consider inference latency and cost
- Implement safety guardrails for production
