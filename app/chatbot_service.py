"""
Healthcare AI Chatbot Service
Integrates domain-specific healthcare logic with OpenAI fallback
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from app.models import Result, User
from app import db

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class HealthcareChatbot:
    """
    Domain-specific healthcare chatbot with intent detection,
    context awareness, and safety guardrails
    """

    def __init__(self):
        self.openai_client = None
        if OpenAI:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)

        # Healthcare intent keywords and patterns
        self.healthcare_intents = {
            "risk_explanation": [
                r"(explain|tell|clarify|show).*(diabetes|heart|disease).*(risk|score|result)",
                r"(what|why).*(my|the).*(risk|score|probability)",
                r"(how).*(high|low|my).*(score|risk)",
                r"(last|current|recent).*(result|prediction|score)",
            ],
            "preventive_measures": [
                r"(how|what).*(improve|reduce|lower).*(score|risk)",
                r"(prevention|prevent|improve|manage|control).*(diabetes|heart)",
                r"(what).*(should|can).*(do|take|eat).*(reduce|improve)",
                r"(diet|exercise|lifestyle).*(help|improve|prevent)",
            ],
            "navigation": [
                r"(open|go|show|navigate).*(dashboard|report|assessment)",
                r"(start|begin|new).*(assessment|prediction|test)",
                r"(download|get).*(report|pdf)",
            ],
            "health_education": [
                r"(what|define|explain).*(diabetes|heart|glucose|bmi|cholesterol)",
                r"(what|how).*(cause|lead|risk factor)",
                r"(symptom|sign|warning).*(diabetes|heart)",
                r"(normal|healthy).*(range|level).*(glucose|blood|pressure|cholesterol)",
            ],
            "medical_prescription": [
                r"(prescribe|medicine|drug|medication|pill|tablet).*(for|should|take)",
                r"(what|which).*(medicine|drug|medication).*(should|take|use)",
                r"(dosage|dose|how much)",
            ],
        }

        # Healthcare knowledge base
        self.health_knowledge = {
            "diabetes": {
                "definition": "Diabetes is a chronic condition affecting how the body processes blood glucose. High glucose levels can damage blood vessels and nerves.",
                "risk_factors": [
                    "High glucose levels",
                    "Elevated BMI (Body Mass Index)",
                    "Family history",
                    "Sedentary lifestyle",
                    "Unhealthy diet high in sugar",
                    "Age above 45"
                ],
                "normal_ranges": {
                    "fasting_glucose": "70-100 mg/dL",
                    "random_glucose": "< 140 mg/dL",
                    "HbA1c": "< 5.7%"
                },
                "prevention_tips": [
                    "Maintain healthy BMI (18.5-24.9)",
                    "Exercise 150 minutes per week",
                    "Eat balanced diet with whole grains",
                    "Reduce sugar intake",
                    "Monitor blood glucose regularly",
                    "Manage stress and sleep"
                ]
            },
            "heart_disease": {
                "definition": "Heart disease includes conditions affecting the heart and blood vessels. It can lead to heart attacks and strokes.",
                "risk_factors": [
                    "High blood pressure",
                    "High cholesterol",
                    "Smoking",
                    "Diabetes",
                    "Obesity",
                    "Sedentary lifestyle",
                    "Family history",
                    "Stress",
                    "Age and gender"
                ],
                "normal_ranges": {
                    "blood_pressure": "< 120/80 mmHg",
                    "total_cholesterol": "< 200 mg/dL",
                    "resting_heart_rate": "60-100 bpm"
                },
                "prevention_tips": [
                    "Maintain healthy blood pressure",
                    "Keep cholesterol in check",
                    "Stop smoking",
                    "Exercise regularly",
                    "Eat heart-healthy diet (Mediterranean style)",
                    "Manage weight",
                    "Control stress",
                    "Limit alcohol"
                ]
            }
        }

    def detect_intent(self, message: str) -> str:
        """
        Detect user intent from message.
        Returns: intent type or 'general'
        """
        message_lower = message.lower()

        # Check for medical prescription (DANGEROUS - must block)
        for pattern in self.healthcare_intents["medical_prescription"]:
            if re.search(pattern, message_lower):
                return "medical_prescription"

        # Check other healthcare intents
        for intent_type, patterns in self.healthcare_intents.items():
            if intent_type == "medical_prescription":
                continue
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent_type

        return "general"

    def handle_risk_explanation(self, user_id: int, message: str) -> Dict:
        """
        Explain user's latest risk result
        """
        try:
            # Get latest result for user
            latest_result = Result.query.filter_by(user_id=user_id).order_by(
                Result.timestamp.desc()
            ).first()

            if not latest_result:
                return {
                    "type": "health_response",
                    "reply": "I don't see any previous assessments. Please complete a health assessment first.",
                    "suggested_actions": ["Start New Assessment"]
                }

            disease_type = latest_result.disease_selected
            probability = latest_result.probability
            risk_level = self._calculate_risk_level(probability)

            # Extract contributing factors based on disease type
            contributing_factors = self._extract_contributing_factors(
                latest_result, disease_type
            )

            # Generate explanation
            explanation = self._generate_risk_explanation(
                disease_type, probability, risk_level, contributing_factors
            )

            # Get preventive suggestions
            preventive_suggestions = self._get_preventive_suggestions(
                disease_type, risk_level
            )

            return {
                "type": "health_response",
                "reply": explanation,
                "risk_level": risk_level,
                "probability": probability,
                "risk_percentage": f"{probability}%",
                "contributing_factors": contributing_factors,
                "preventive_actions": preventive_suggestions,
                "suggested_actions": ["Download Report", "Schedule Consultation"],
                "disclaimer": "This is educational guidance, not medical advice. Consult a healthcare professional."
            }

        except Exception as e:
            return {
                "type": "error",
                "reply": f"Unable to fetch your results: {str(e)}",
                "suggested_actions": ["Try Again", "Contact Support"]
            }

    def handle_preventive_measures(self, user_id: int, disease_type: Optional[str] = None) -> Dict:
        """
        Provide preventive measures clarification
        """
        try:
            # Get user's latest result if not specified
            if not disease_type:
                latest_result = Result.query.filter_by(user_id=user_id).order_by(
                    Result.timestamp.desc()
                ).first()
                if latest_result:
                    disease_type = latest_result.disease_selected
                else:
                    return {
                        "type": "health_response",
                        "reply": "Please specify which disease you'd like preventive measures for: Diabetes or Heart Disease.",
                        "suggested_actions": ["Ask about Diabetes", "Ask about Heart Disease"]
                    }

            # Normalize disease type
            if isinstance(disease_type, str):
                if "diabetes" in disease_type.lower():
                    disease_type = "diabetes"
                elif "heart" in disease_type.lower():
                    disease_type = "heart_disease"

            if disease_type not in self.health_knowledge:
                return {
                    "type": "health_response",
                    "reply": "I can provide guidance on Diabetes and Heart Disease prevention.",
                    "suggested_actions": ["Diabetes Prevention", "Heart Disease Prevention"]
                }

            # Ensure disease_type is a string for subsequent operations
            assert isinstance(disease_type, str), "disease_type must be a string"
            
            knowledge = self.health_knowledge[disease_type]
            risk_level = "Moderate"  # Default

            # Get user's actual risk level if available
            latest_result = Result.query.filter_by(user_id=user_id).order_by(
                Result.timestamp.desc()
            ).first()
            if latest_result and latest_result.disease_selected.lower() in disease_type.lower():
                risk_level = self._calculate_risk_level(latest_result.probability)

            preventive_message = f"""
            ## Prevention for {disease_type.replace('_', ' ').title()}
            
            **Definition:** {knowledge['definition']}
            
            **Key Risk Factors:**
            {chr(10).join(f"• {factor}" for factor in knowledge['risk_factors'][:5])}
            
            **Normal Healthy Ranges:**
            {chr(10).join(f"• {key.replace('_', ' ').title()}: {value}" for key, value in knowledge['normal_ranges'].items())}
            
            **Prevention Tips:**
            {chr(10).join(f"• {tip}" for tip in knowledge['prevention_tips'])}
            
            **Your Current Risk Level:** {risk_level}
            """

            return {
                "type": "health_response",
                "reply": preventive_message.strip(),
                "suggested_actions": ["Download Prevention Guide", "Schedule Consultation"],
                "disclaimer": "This is educational guidance. Consult your healthcare provider for personalized advice."
            }

        except Exception as e:
            return {
                "type": "error",
                "reply": f"Error retrieving prevention information: {str(e)}"
            }

    def handle_navigation(self, command: str) -> Dict:
        """
        Handle navigation commands
        """
        routes = {
            "dashboard": "/dashboard",
            "report": "/dashboard",
            "assessment": "/select-disease",
            "test": "/select-disease"
        }

        command_lower = command.lower()
        for keyword, route in routes.items():
            if keyword in command_lower:
                return {
                    "type": "navigation",
                    "action": "redirect",
                    "route": route,
                    "message": f"Redirecting to {keyword}..."
                }

        return {
            "type": "error",
            "reply": "I didn't understand that navigation command. Try: dashboard, start assessment, or download report.",
            "suggested_actions": ["Go to Dashboard", "Start Assessment"]
        }

    def handle_health_education(self, topic: str) -> Dict:
        """
        Provide health education on specific topics
        """
        topic_lower = topic.lower()

        # Determine which disease the question is about
        disease = None
        if "diabetes" in topic_lower or "glucose" in topic_lower or "bmi" in topic_lower:
            disease = "diabetes"
        elif "heart" in topic_lower or "cholesterol" in topic_lower or "blood pressure" in topic_lower:
            disease = "heart_disease"

        if disease and disease in self.health_knowledge:
            knowledge = self.health_knowledge[disease]
            education = f"""
            ## {disease.replace('_', ' ').title()} Education
            
            **What is it?**
            {knowledge['definition']}
            
            **Risk Factors:**
            {chr(10).join(f"• {factor}" for factor in knowledge['risk_factors'][:6])}
            
            **Healthy Ranges:**
            {chr(10).join(f"• {key.replace('_', ' ').title()}: {value}" for key, value in knowledge['normal_ranges'].items())}
            """

            return {
                "type": "health_response",
                "reply": education.strip(),
                "suggested_actions": ["Learn Prevention", "Get Assessed"],
                "disclaimer": "For medical diagnosis, consult a healthcare professional."
            }

        # Fallback to OpenAI for general medical education
        return None  # type: ignore

    def handle_medical_prescription_block(self) -> Dict:
        """
        Safety: Block medication/prescription requests
        """
        return {
            "type": "safety_block",
            "reply": "⚠️ **Safety Notice**: I cannot provide medication prescriptions, dosages, or drug recommendations.\n\n"
                     "Please consult a licensed healthcare professional or pharmacist for medication guidance.\n\n"
                     "I can help with:\n"
                     "• Explaining your risk scores\n"
                     "• Prevention strategies\n"
                     "• Health education\n"
                     "• Navigation assistance",
            "suggested_actions": ["Explain my risk", "Prevention tips", "Health information"]
        }

    def process_health_chat(self, user_id: int, message: str) -> Dict:
        """
        Main entry point for healthcare-specific chat
        """
        intent = self.detect_intent(message)

        if intent == "medical_prescription":
            return self.handle_medical_prescription_block()

        elif intent == "risk_explanation":
            return self.handle_risk_explanation(user_id, message)

        elif intent == "preventive_measures":
            return self.handle_preventive_measures(user_id)

        elif intent == "navigation":
            return self.handle_navigation(message)

        elif intent == "health_education":
            result = self.handle_health_education(message)
            if result:
                return result
            # Falls back to OpenAI if no direct match

        # Default to general AI
        return None  # type: ignore

    def process_general_chat(self, message: str) -> Dict:
        """
        Fallback to OpenAI for general knowledge questions
        """
        if not self.openai_client:
            return {
                "type": "error",
                "reply": "OpenAI API is not configured. Please set OPENAI_API_KEY environment variable.",
                "suggested_actions": ["Try healthcare question", "Contact Support"]
            }

        try:
            system_prompt = """You are an AI healthcare assistant integrated into a preventive health risk prediction platform.

Your Guidelines:
1. Focus on disease awareness, prevention, and explanation of risk scores
2. Do NOT provide diagnosis or medication advice
3. Do NOT prescribe medications or suggest dosages
4. Always add disclaimers: "This is educational guidance, not medical advice"
5. Be calm, clinical, structured, and trustworthy
6. Direct users to healthcare professionals for medical decisions
7. If asked about prescriptions, firmly decline and suggest consulting a doctor

Your Tone: Professional, educational, health-focused, never casual or meme-like"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )

            reply = response.choices[0].message.content

            return {
                "type": "ai_response",
                "reply": reply,
                "source": "OpenAI GPT-4o-mini",
                "disclaimer": "This is educational guidance, not medical advice."
            }

        except Exception as e:
            return {
                "type": "error",
                "reply": f"AI service temporarily unavailable: {str(e)}",
                "suggested_actions": ["Try healthcare question", "Contact Support"]
            }

    def _calculate_risk_level(self, probability: float) -> str:
        """Calculate risk level from probability"""
        if probability >= 70:
            return "High"
        elif probability >= 40:
            return "Moderate"
        else:
            return "Low"

    def _extract_contributing_factors(self, result: Result, disease_type: str) -> List[str]:
        """Extract key contributing factors from prediction result"""
        factors = []

        if "Diabetes" in disease_type:
            if result.glucose and result.glucose > 125:
                factors.append(f"Elevated glucose level ({result.glucose} mg/dL)")
            if result.bmi and result.bmi > 25:
                factors.append(f"High BMI ({result.bmi})")
            if result.age and result.age > 45:
                factors.append("Age above 45")
            if result.pregnancies and result.pregnancies > 3:
                factors.append("Multiple pregnancies")

        elif "Heart" in disease_type:
            if result.trestbps and result.trestbps > 140:
                factors.append(f"High blood pressure ({result.trestbps} mmHg)")
            if result.chol and result.chol > 240:
                factors.append(f"High cholesterol ({result.chol} mg/dL)")
            if result.age and result.age > 55:
                factors.append("Age above 55")
            if result.exang == 1:
                factors.append("Exercise-induced angina")

        return factors if factors else ["See detailed assessment for factors"]

    def _generate_risk_explanation(
        self,
        disease_type: str,
        probability: float,
        risk_level: str,
        factors: List[str]
    ) -> str:
        """Generate detailed risk explanation"""

        explanation = f"""
        ## Your {disease_type} Risk Assessment
        
        **Risk Probability:** {probability}%
        **Risk Category:** {risk_level}
        
        **Key Contributing Factors:**
        {chr(10).join(f"• {factor}" for factor in factors)}
        
        **What This Means:**
        """

        if risk_level == "High":
            explanation += f"\nYour {disease_type} risk is significantly elevated. Immediate medical consultation is strongly recommended."
        elif risk_level == "Moderate":
            explanation += f"\nYour {disease_type} risk is moderate. Lifestyle changes and regular monitoring are important."
        else:
            explanation += f"\nYour {disease_type} risk is low. Continue preventive measures and regular check-ups."

        explanation += f"\n\n⚠️ **Disclaimer:** This is an AI-generated assessment, not a medical diagnosis. Consult a healthcare professional for proper evaluation."

        return explanation.strip()

    def _get_preventive_suggestions(self, disease_type: str, risk_level: str) -> List[str]:
        """Get actionable preventive suggestions"""
        suggestions = []

        if "Diabetes" in disease_type:
            if risk_level == "High":
                suggestions = [
                    "Monitor blood glucose daily",
                    "Follow strict low-carb diet",
                    "Get HbA1c test immediately",
                    "Consult an Endocrinologist"
                ]
            elif risk_level == "Moderate":
                suggestions = [
                    "Exercise 150 mins per week",
                    "Monitor weight and BMI",
                    "Reduce sugar intake",
                    "Schedule doctor visit"
                ]
            else:
                suggestions = [
                    "Maintain healthy BMI",
                    "Continue balanced diet",
                    "Annual glucose screening",
                    "Stay active"
                ]

        elif "Heart" in disease_type:
            if risk_level == "High":
                suggestions = [
                    "Get ECG and cardiac test immediately",
                    "Start cardiac rehabilitation",
                    "Consult a heart specialist",
                    "Monitor blood pressure daily"
                ]
            elif risk_level == "Moderate":
                suggestions = [
                    "Reduce sodium intake",
                    "Exercise regularly",
                    "Manage stress",
                    "Monitor cholesterol"
                ]
            else:
                suggestions = [
                    "Maintain healthy lifestyle",
                    "Regular cardio exercise",
                    "Healthy diet (Mediterranean style)",
                    "Annual heart check-up"
                ]

        return suggestions

    def get_conversation_context(self, user_id: int) -> Dict:
        """Get user context for conversation"""
        try:
            user = User.query.get(user_id)
            latest_result = Result.query.filter_by(user_id=user_id).order_by(
                Result.timestamp.desc()
            ).first()

            context = {
                "username": user.username if user else "User",
                "last_assessment": None,
                "last_disease": None,
                "last_probability": None
            }

            if latest_result:
                context["last_assessment"] = latest_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                context["last_disease"] = latest_result.disease_selected
                context["last_probability"] = latest_result.probability

            return context

        except Exception as e:
            return {"username": "User", "error": str(e)}


# Initialize global chatbot instance
healthcare_chatbot = HealthcareChatbot()
