from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import joblib
import os
import numpy as np

# Load models
# Hardcoded for debugging
MODEL_DIR = r'c:/Users/anubh/Downloads/diabetes-heart-prediction-main/diabetes-heart-prediction-main/models'

try:
    heart_model = joblib.load(os.path.join(MODEL_DIR, 'heart_model.pkl'))
    diabetes_model = joblib.load(os.path.join(MODEL_DIR, 'diabetes_model.pkl'))
except FileNotFoundError as e:
    print(f"Warning: Models not found at {MODEL_DIR}. Error: {e}")
    heart_model = None
    diabetes_model = None

def get_preventive_measures(disease, probability):
    """
    Returns structured medical guidance based on disease and risk probability.
    """
    risk_level = "Low"
    if probability > 0.7:
        risk_level = "High"
    elif probability > 0.3:
        risk_level = "Moderate"

    guidance = {
        "risk_level": risk_level,
        "lifestyle": [],
        "diet": [],
        "exercise": [],
        "screening": [],
        "consult": ""
    }

    if disease == "Heart Disease":
        if risk_level == "High":
            guidance["lifestyle"] = ["Quit smoking immediately", "Manage stress with meditation/yoga"]
            guidance["diet"] = ["Strict low-sodium diet", "Avoid trans fats completely"]
            guidance["exercise"] = ["Consult doctor before starting", "Light walking 15 mins/day"]
            guidance["screening"] = ["ECG & Echo immediately", "Lipid profile"]
            guidance["consult"] = "Consult a Cardiologist IMMEDIATELY"
        elif risk_level == "Moderate":
            guidance["lifestyle"] = ["Limit alcohol intake", "Maintain healthy weight"]
            guidance["diet"] = ["Reduce salt intake", "Eat more fruits and vegetables"]
            guidance["exercise"] = ["Moderate cardio 30 mins/day", "Brisk walking"]
            guidance["screening"] = ["Monitor BP weekly", "Annual cholesterol check"]
            guidance["consult"] = "Schedule a checkup within 2 weeks"
        else:
            guidance["lifestyle"] = ["Maintain active lifestyle", "Avoid smoking"]
            guidance["diet"] = ["Balanced diet", "Limit processed foods"]
            guidance["exercise"] = ["Regular exercise 30 mins/day"]
            guidance["screening"] = ["Regular annual checkup"]
            guidance["consult"] = "Standard annual review"

    elif disease == "Diabetes":
        if risk_level == "High":
            guidance["lifestyle"] = ["Monitor blood sugar daily", "Inspect feet for injuries"]
            guidance["diet"] = ["Strict low-carb diet", "Avoid sugar completely"]
            guidance["exercise"] = ["Moderate activity after meals"]
            guidance["screening"] = ["HbA1c test immediately", "Fast blood sugar"]
            guidance["consult"] = "Consult an Endocrinologist IMMEDIATELY"
        elif risk_level == "Moderate":
            guidance["lifestyle"] = ["Weight management", "Regular sleep schedule"]
            guidance["diet"] = ["Complex carbohydrates", "Portion control"]
            guidance["exercise"] = ["Aerobic exercise 150 mins/week"]
            guidance["screening"] = ["HbA1c test every 3 months"]
            guidance["consult"] = "Consult doctor within 1 month"
        else:
            guidance["lifestyle"] = ["Healthy weight maintenance"]
            guidance["diet"] = ["Limit sugary drinks", "High fiber diet"]
            guidance["exercise"] = ["Stay active"]
            guidance["screening"] = ["Annual blood sugar check"]
            guidance["consult"] = "Standard annual review"

    return guidance

def generate_pdf_report(result_data):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "Smart Healthcare Early Risk System")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, f"Patient Report for: {result_data.get('username', 'N/A')}")
    p.drawString(50, height - 100, f"Date: {result_data.get('date', 'N/A')}")

    p.line(50, height - 110, width - 50, height - 110)

    # Result
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 140, "Prediction Result")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 160, f"Condition: {result_data.get('disease')}")
    p.drawString(50, height - 180, f"Prediction: {result_data.get('prediction')}")
    p.drawString(50, height - 200, f"Probability: {result_data.get('probability')}%")

    # Disclaimer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 50, "Disclaimer: This is an AI-generated report and not a substitute for professional medical advice.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def predict_heart_risk(input_data):
    if heart_model:
        # Prediction logic
        prediction = heart_model.predict([input_data])[0]
        probability = heart_model.predict_proba([input_data])[0][1] # Probability of class 1
        return prediction, probability
    return None, 0.0

def predict_diabetes_risk(input_data):
    if diabetes_model:
        prediction = diabetes_model.predict([input_data])[0]
        probability = diabetes_model.predict_proba([input_data])[0][1]
        return prediction, probability
    return None, 0.0
