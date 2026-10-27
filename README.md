# Electricity Fraud Detection System

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

Create a local `.env` file for configuration values required by the app. Set a unique, random `SECRET_KEY` before running the application. Do not commit secrets or production credentials.

### 5. Start the application

Use the entry point documented by the current project files. If your local checkout uses `app.py` as the entry point:

```bash
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Machine-Learning Workflow

1. Collect and validate usage inputs.
2. Derive features from current and historical usage.
3. Apply the preprocessing/scaling expected by the saved model.
4. Generate a prediction and risk-oriented explanation.
5. Review the result alongside the underlying usage data.

For a meaningful model evaluation, report metrics on a held-out dataset—such as precision, recall, F1 score, confusion matrix, and ROC-AUC where appropriate. Do not describe the model as production-validated unless those results have been measured.

## Security and Reliability Notes

- Use a strong environment-provided secret key; never rely on a development fallback in production.
- Run with debug mode disabled outside local development.
- Validate non-finite and out-of-range inputs and handle missing model files gracefully.
- Keep model artifacts and training/evaluation instructions versioned or clearly documented.

## Future Improvements

- Add reproducible model training and evaluation scripts.
- Expand tests for validation, prediction, and authentication flows.
- Add deployment instructions and screenshots stored as normal image files.
- Document the dataset source, limitations, and model metrics.

## Author

Ajay Shanmuga Sundaram
