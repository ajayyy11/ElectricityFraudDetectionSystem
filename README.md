# Electricity Fraud Detection System

![Python CI](https://github.com/ajayyy11/ElectricityFraudDetectionSystem/actions/workflows/ci.yml/badge.svg)

A Flask web application that analyzes electricity-consumption patterns and flags potentially suspicious usage using a machine-learning workflow. It includes user-facing pages, usage comparisons, and a risk-oriented result view.

> **Important:** A flagged result is an indicator for review, not proof of electricity theft. Model performance depends on the quality and representativeness of the training data.

## Features

- User authentication and role-oriented pages
- Electricity usage input and historical tracking
- Feature engineering for usage-pattern analysis
- Model-backed fraud-risk prediction
- Dashboard and usage-comparison visualizations

## Tech Stack

- **Backend:** Python, Flask
- **ML/data:** scikit-learn, NumPy, Pandas, Joblib
- **Database:** SQLite configuration (review your local configuration for any alternate database setup)
- **UI:** HTML, CSS, Bootstrap, JavaScript

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/ajayyy11/ElectricityFraudDetectionSystem.git
cd ElectricityFraudDetectionSystem
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`. Replace the placeholder `SECRET_KEY` with a unique random secret of at least 32 characters. Generate one with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Do not commit `.env`, API credentials, or production secrets.

### 5. Start the application

```bash
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Tests

Run the automated unit and route tests with:

```bash
pytest -q
```

The tests cover input validation, scoring calculations, selected routes, evaluation-feature validation, registration-role protection, and safe post-login redirects. They do not replace manual integration testing with the saved model artifacts and database configuration.

## Machine-Learning Evaluation

The repository includes `scripts/evaluate_model.py` to evaluate the saved model on a labeled CSV. The CSV must contain these columns:

- `current_usage`
- `avg_usage`
- `fraud_label` — ground-truth binary label: `0` for non-fraud, `1` for fraud

Example:

```bash
python scripts/evaluate_model.py path/to/held_out_data.csv
```

Optionally choose a probability threshold:

```bash
python scripts/evaluate_model.py path/to/held_out_data.csv --threshold 0.4
```

The script reports accuracy, precision, recall, F1, ROC-AUC (when both classes are present), a confusion matrix, and a classification report. Use a held-out dataset that was not used to train or tune the model. Do not publish performance claims until you have run the evaluation and reviewed the results.

## Security and Reliability Notes

- Use a strong environment-provided secret key.
- Run with debug mode disabled outside local development.
- Validate non-finite and out-of-range inputs and handle missing model files gracefully.
- Keep model artifacts and training/evaluation instructions versioned or clearly documented.

## Future Improvements

- Add reproducible model training and dataset documentation.
- Expand tests for prediction persistence and authentication flows.
- Add deployment instructions and screenshots stored as normal image files.
- Document measured model metrics and limitations.

## Author

Ajay Shanmuga Sundaram
