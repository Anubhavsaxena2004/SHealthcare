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
            "heart level": "To maintain a healthy heart: 1. Exercise 30 mins daily. 2. Eat a balanced diet low in saturated fats. 3. Manage stress. 4. Quit smoking. 5. Regular checkups.",
            "ideal values": "<b>Ideal Health Ranges:</b><br>Heart Rate: 60-100 bpm<br>Blood Pressure: 120/80 mmHg<br>Fasting Blood Sugar: 70-99 mg/dL<br>Post-meal Sugar: <140 mg/dL",
            "website about": "This is a <b>Smart Healthcare Early Risk Prediction System</b> designed to predict Diabetes and Heart Disease risk using advanced Machine Learning models.",
            "platform work": "<b>How it works:</b><br>1. Enter your health metrics in the Predict page.<br>2. Get an AI-driven risk analysis.<br>3. Receive personalized precautions and doctor recommendations.",
            "all the range": "<b>Standard Medical Ranges:</b><br><b>Blood Pressure:</b> 90/60 to 120/80 mmHg<br><b>Heart Rate:</b> 60-100 bpm<br><b>Cholesterol:</b> <200 mg/dL<br><b>Glucose (Fasting):</b> 70-99 mg/dL<br><b>BMI:</b> 18.5-24.9"
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
