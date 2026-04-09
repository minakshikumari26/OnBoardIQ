import joblib
import pandas as pd
import shap

# Load model
model = joblib.load("backend/models/risk_model.pkl")

explainer = shap.TreeExplainer(model)

def predict_risk(income, loan_amount, credit_score, dti):
    
    print("DEBUG INPUT:", income, loan_amount, credit_score, dti)
    
    # Input dataframe
    data = pd.DataFrame([{
        "income": income,
        "loan_amount": loan_amount,
        "Credit_Score": credit_score,
        "dtir1": dti
    }])
    
    
    
    # Prediction
    proba = model.predict_proba(data)[0]
    pd_score = float(proba[1])
    
    print("PROBA:", proba)

    # Risk Level Mapping
    if pd_score > 0.7:
        level = "High Risk"
    elif pd_score > 0.4:
        level = "Medium Risk"
    else:
        level = "Low Risk"

    # SHAP Calculation
    shap_values = explainer(data)
    
    if len(shap_values.values.shape) == 3:
        shap_vals = shap_values.values[0,:,1]
    else:
        shap_vals = shap_values.values[0]
        
        
    feature_names = data.columns

    factors = []
    for i in range(len(feature_names)):
        factors.append({
            "factor": feature_names[i],
            "impact": round(float(shap_vals[i]), 3)
        })

    factors = sorted(factors, key=lambda x: abs(x["impact"]), reverse=True)[:3]

    return {
        "risk_level": level,
        "pd_score": round(pd_score, 2),
        "top_factors": factors
    }