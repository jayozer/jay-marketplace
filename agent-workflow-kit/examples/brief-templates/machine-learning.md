# Machine Learning Brief Template

## Template

```
Goal: Deliver [ML MODEL/PIPELINE].
Context: [ML FRAMEWORK/PROJECT], [DATA SOURCE], [FEATURES], and [CURRENT BASELINE].
Output: [MODEL ARTIFACTS/TRAINING CODE/INFERENCE API/MODEL CARD].
Boundaries: Preserve [DATA/PRIVACY/COST CONSTRAINTS]; require approval for training spend or deployment.
Verification: [REPRODUCIBLE EVAL], [TARGET METRICS], [ROBUSTNESS/FAIRNESS CHECKS], and artifact review.
```

## Example: Customer Churn Prediction Model

```
Goal: Deliver a reproducible customer-churn model in the existing scikit-learn project.
Context: Approved customer features, XGBoost, FastAPI inference, and Evidently AI monitoring.
Output: Training pipeline, model artifact, inference endpoint, evaluation report, and model card.
Boundaries: Use only approved de-identified data; do not start paid training or deploy without approval.
Verification: Reproduce AUC-ROC 0.85+, precision 0.80+, and recall 0.75+ on the held-out set, then review explainability and drift checks.
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
