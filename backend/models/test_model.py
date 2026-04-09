import joblib
import pandas as pd
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "risk_model.pkl")
model = joblib.load(model_path)

# model = joblib.load("risk_model.pkl")

sample = pd.DataFrame([{
    "income": 50000,
    "loan_amount": 200000,
    "Credit_Score": 720,
    "dtir1": 35
}])

prediction = model.predict(sample)

print("Prediction:", prediction)