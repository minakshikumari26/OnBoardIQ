from openai import models
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
print("Current location:", os.getcwd())
print("Files in data folder:", os.listdir("data"))

data = pd.read_csv("data/loan_dataset.csv")

print("Columns in dataset:")
print(data.columns)

X = data[['income','loan_amount','Credit_Score','dtir1']]
y = data['Status']


X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train,y_train)

os.makedirs("backend/models", exist_ok=True)
joblib.dump(model,"backend/models/risk_model.pkl")

print("Model trained and saved")