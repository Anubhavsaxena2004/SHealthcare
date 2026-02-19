import os
try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None
from app.models import Result, User
from app import db
from datetime import datetime

class HealthcareChatbot:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if genai and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            if not genai:
                print("Warning: google-generativeai not installed; chatbot AI disabled.")
            else:
                print("Warning: GEMINI_API_KEY not found.")
            self.model = None

    def get_conversation_context(self, user_id):
        """Retrieve relevant medical context for the user."""
        try:
            last_result = Result.query.filter_by(user_id=user_id).order_by(Result.timestamp.desc()).first()
            if last_result:
                return {
                    "last_disease": last_result.disease,
                    "last_prediction": last_result.prediction,
                    "last_probability": last_result.probability,
                    "timestamp": last_result.timestamp.isoformat()
                }
            return {}
        except Exception:
            return {}

    def detect_intent(self, message):
        """Simple keyword-based intent detection."""
        keywords = ['diabetes', 'heart', 'blood', 'pressure', 'sugar', 'glucose', 'pain', 'symptom', 'doctor', 'risk', 'health', 'diet', 'exercise']
        if any(k in message.lower() for k in keywords):
            return "health"
        return "general"

    def check_hardcoded_response(self, message):
        """Check if message matches hardcoded queries."""
        msg = message.lower()
        
        responses = {
            # Existing responses
            "heart level": "To maintain a healthy heart: 1. Exercise 30 mins daily. 2. Eat a balanced diet low in saturated fats. 3. Manage stress. 4. Quit smoking. 5. Regular checkups.",
            "ideal values": "<b>Ideal Health Ranges:</b><br>Heart Rate: 60-100 bpm<br>Blood Pressure: 120/80 mmHg<br>Fasting Blood Sugar: 70-99 mg/dL<br>Post-meal Sugar: <140 mg/dL",
            "website about": "This is a <b>Smart Healthcare Early Risk Prediction System</b> designed to predict Diabetes and Heart Disease risk using advanced Machine Learning models.",
            "platform work": "<b>How it works:</b><br>1. Enter your health metrics in the Predict page.<br>2. Get an AI-driven risk analysis.<br>3. Receive personalized precautions and doctor recommendations.",
            "all the range": "<b>Standard Medical Ranges:</b><br><b>Blood Pressure:</b> 90/60 to 120/80 mmHg<br><b>Heart Rate:</b> 60-100 bpm<br><b>Cholesterol:</b> <200 mg/dL<br><b>Glucose (Fasting):</b> 70-99 mg/dL<br><b>BMI:</b> 18.5-24.9",
            
            # Diabetes related
            "diabetes symptoms": "<b>Common Diabetes Symptoms:</b><br>• Frequent urination<br>• Excessive thirst<br>• Unexplained weight loss<br>• Fatigue<br>• Blurred vision<br>• Slow-healing wounds",
            "diabetes precautions": "<b>Diabetes Precautions:</b><br>• Maintain healthy weight<br>• Exercise regularly (30 mins/day)<br>• Eat balanced diet, limit sugars<br>• Monitor blood sugar levels<br>• Take medications as prescribed<br>• Regular checkups",
            "diabetes cause": "<b>Common Causes of Diabetes:</b><br>• Genetic factors<br>• Poor diet and obesity<br>• Sedentary lifestyle<br>• Age (risk increases after 45)<br>• High blood pressure<br>• Family history",
            "diabetes diet": "<b>Diabetes-Friendly Diet:</b><br>• Whole grains (brown rice, oats)<br>• Lean proteins (fish, chicken)<br>• Fresh vegetables<br>• Fruits (in moderation)<br>• Avoid: Sugary drinks, processed foods, white bread",
            
            # Heart disease related
            "heart disease symptoms": "<b>Heart Disease Warning Signs:</b><br>• Chest pain or discomfort<br>• Shortness of breath<br>• Pain in neck, jaw, or back<br>• Fatigue during activity<br>• Swelling in legs/ankles<br>• Irregular heartbeat",
            "heart precautions": "<b>Heart Disease Precautions:</b><br>• Exercise regularly<br>• Eat heart-healthy foods<br>• Control cholesterol levels<br>• Manage blood pressure<br>• Quit smoking<br>• Reduce stress<br>• Limit alcohol",
            "heart attack": "<b>Heart Attack Warning Signs:</b><br>• Chest pain/pressure<br>• Pain in arm, jaw, or neck<br>• Shortness of breath<br>• Cold sweat<br>• Nausea<br><b>Action:</b> Call emergency services immediately!",
            "heart diet": "<b>Heart-Healthy Diet:</b><br>• Omega-3 fatty acids (fish, walnuts)<br>• Fiber-rich foods<br>• Fruits and vegetables<br>• Limit sodium and saturated fats<br>• Avoid processed foods",
            
            # Blood pressure related
            "blood pressure": "<b>Blood Pressure Guide:</b><br><b>Normal:</b> Less than 120/80 mmHg<br><b>Elevated:</b> 120-129/less than 80<br><b>High (Stage 1):</b> 130-139/80-89<br><b>High (Stage 2):</b> 140+/90+",
            "high blood pressure": "<b>Managing High Blood Pressure:</b><br>• Reduce sodium intake<br>• Exercise regularly<br>• Maintain healthy weight<br>• Limit alcohol<br>• Manage stress<br>• Take prescribed medications",
            
            # Sugar/Glucose related
            "blood sugar": "<b>Blood Sugar Levels:</b><br><b>Fasting:</b> 70-99 mg/dL (normal)<br><b>Pre-diabetes:</b> 100-125 mg/dL<br><b>Diabetes:</b> 126 mg/dL or higher<br><b>After meals:</b> Less than 140 mg/dL",
            "low blood sugar": "<b>Low Blood Sugar (Hypoglycemia):</b><br>Symptoms: Shaking, sweating, dizziness, confusion<br><b>Quick Fix:</b> Eat 15-20g glucose candy/drink juice",
            
            # General health
            "healthy lifestyle": "<b>Healthy Lifestyle Tips:</b><br>• Exercise 30 mins daily<br>• Eat balanced diet<br>• Get 7-8 hours sleep<br>• Stay hydrated<br>• Manage stress<br>• Regular health checkups<br>• Avoid smoking",
            "exercise": "<b>Recommended Exercise:</b><br>• Cardio: 150 mins/week<br>• Strength training: 2-3 times/week<br>• Walking, swimming, cycling<br>• Stretching daily<br>• Start slowly if beginner",
            "weight": "<b>Healthy Weight (BMI):</b><br><b>Underweight:</b> Below 18.5<br><b>Normal:</b> 18.5-24.9<br><b>Overweight:</b> 25-29.9<br><b>Obese:</b> 30 or higher",
            "cholesterol": "<b>Cholesterol Levels:</b><br><b>Total:</b> Less than 200 mg/dL<br><b>LDL (Bad):</b> Less than 100 mg/dL<br><b>HDL (Good):</b> 40 mg/dL or higher<br><b>Triglycerides:</b> Less than 150 mg/dL",
            
            # Symptoms
            "symptoms": "<b>Common Health Symptoms to Watch:</b><br>• Unexplained weight changes<br>• Persistent fatigue<br>• Fever lasting more than 3 days<br>• Chest pain<br>• Shortness of breath<br>• Severe headaches",
            "when to see doctor": "<b>When to See a Doctor:</b><br>• Persistent symptoms lasting more than 2 weeks<br>• Chest pain or difficulty breathing<br>• Sudden vision changes<br>• Severe headaches<br>• Unexplained weight loss<br>• High fever",
            
            # Prevention
            "prevent diabetes": "<b>Preventing Type 2 Diabetes:</b><br>• Maintain healthy weight<br>• Exercise regularly<br>• Eat whole grains and fiber<br>• Limit sugary foods<br>• Don't skip meals<br>• Regular screening after age 45",
            "prevent heart disease": "<b>Preventing Heart Disease:</b><br>• Don't smoke<br>• Exercise regularly<br>• Eat healthy diet<br>• Control blood pressure<br>• Manage cholesterol<br>• Reduce stress<br>• Limit alcohol",
            
            # Emergency
            "emergency": "<b>Medical Emergency Signs:</b><br>• Chest pain/discomfort<br>• Difficulty breathing<br>• Severe bleeding<br>• Loss of consciousness<br>• Severe allergic reaction<br><b>Action:</b> Call emergency services immediately!",
            "first aid": "<b>Basic First Aid:</b><br>• For cuts: Clean and apply pressure<br>• For burns: Cool water, cover loosely<br>• For choking: Heimlich maneuver<br>• For CPR: 30 chest compressions, 2 breaths"
        }

        for key, reply in responses.items():
            if key in msg:
                return {"reply": reply, "type": "info_response"}
        
        return None

    def process_health_chat(self, user_id, message):
        """Handle health-specific queries with context."""
        
        # Check hardcoded first
        hardcoded = self.check_hardcoded_response(message)
        if hardcoded:
            return hardcoded

        if not self.model:
            return {"reply": "AI service unavailable (Check API Key).", "type": "error"}

        context = self.get_conversation_context(user_id)
        
        system_prompt = f"""
        You are a Calm AI Wellness Assistant in a healthcare app.
        User Context: {context}
        
        Guidelines:
        - Be empathetic and supportive.
        - Use the user's recent health data if relevant.
        - If they have high risk, be gentle but firm about seeing a doctor.
        - Keep answers concise (under 100 words).
        - Disclaimer: You update educational info, not medical diagnosis.
        """
        
        try:
            full_prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"
            response = self.model.generate_content(full_prompt)
            return {
                "reply": response.text,
                "type": "health_response",
                "suggested_actions": ["View Dashboard", "Download Report"]
            }
        except Exception as e:
            return {"reply": "I'm having trouble connecting. Please try again.", "type": "error"}

    def process_general_chat(self, message):
        """Handle general queries."""
        
        # Check hardcoded first
        hardcoded = self.check_hardcoded_response(message)
        if hardcoded:
            return hardcoded

        # Fallback for unconnected general questions
        return {
            "reply": "I am working on learning that! Try asking about: 'Ideal heart values', 'How this platform works', or 'Diabetes precautions'.",
            "type": "general_response",
            "suggested_actions": ["Ideal values", "How it works"]
        }

healthcare_chatbot = HealthcareChatbot()
