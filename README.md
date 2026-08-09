# OnBoardIQ

OnBoardIQ is an AI-powered loan approval platform that combines a Streamlit frontend, a FastAPI backend, and multiple decision-making agents to evaluate loan applications.

## Overview

The system allows users to:
- register and verify their identity using PAN information
- enter loan and financial details
- receive an AI-driven credit decision with risk scoring
- save approved or rejected loan outcomes in a PostgreSQL database

It is designed as a practical demo of an agentic AI workflow for financial decision support.

## Features

- PAN-based applicant verification
- Credit and risk assessment flow
- DTI-based live risk estimation
- AI decision output with reasons and supporting factors
- Admin endpoints for viewing users and loan records

## Tech Stack

- Python
- FastAPI
- Streamlit
- scikit-learn
- pandas
- joblib
- PostgreSQL

## Project Structure

- backend/agents/ - compliance, credit, fraud, decision, and orchestrator agents
- backend/api/ - FastAPI routes and application entrypoint
- backend/db/ - database connection and query helpers
- backend/services/ - loan service logic
- ui/ - Streamlit web app
- data/ - loan dataset used for modeling
- notebooks/ - training scripts and experiments

## Getting Started

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows, use:

```powershell
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up PostgreSQL

Create a PostgreSQL database named `loan_db` and ensure the connection settings in `backend/db/connection.py` match your local environment.

### 4. Run the backend

```bash
uvicorn backend.api.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 5. Run the frontend

In a separate terminal:

```bash
streamlit run ui/app.py
```

Open `http://localhost:8501` in your browser.

## Testing

You can run the available tests with:

```bash
pytest -q
```

## Notes

- The app expects a local PostgreSQL instance with a database named `loan_db`.
- If your PostgreSQL credentials differ, update them in `backend/db/connection.py`.
- The Streamlit UI communicates with the FastAPI backend on port `8000`.
