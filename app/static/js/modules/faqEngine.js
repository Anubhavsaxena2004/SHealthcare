export const FAQ_RESPONSES = {
    "what is this website for": {
        type: "text",
        content: "This platform is an AI-powered Smart Healthcare Early Risk Assessment System designed to help individuals evaluate potential risks for conditions such as diabetes and heart disease. It provides early insights, preventive guidance, and access to healthcare support resources."
    },
    "how does this website work": {
        type: "text",
        content: "The system collects health-related inputs from you and analyzes them using machine learning models trained on medical datasets. Based on your responses, it estimates your risk probability and provides preventive recommendations."
    },
    "is my personal information secure": {
        type: "text",
        content: "Yes. Your data is handled with strict confidentiality. We do not sell or share personal health information with third parties. All records are stored securely and used only for assessment and support purposes."
    },
    "what precautions should i take": {
        type: "text",
        content: "Preventive measures depend on your assessed risk level. Generally, maintaining a balanced diet, exercising regularly, managing stress, and scheduling routine health check-ups significantly reduce health risks."
    },
    "what is diabetes": {
        type: "text",
        content: "Diabetes is a chronic condition where the body either does not produce enough insulin or cannot effectively use it, leading to elevated blood sugar levels over time."
    },
    "what is heart disease": {
        type: "text",
        content: "Heart disease refers to various conditions affecting the heart, including coronary artery disease, arrhythmias, and heart failure. It is often linked to lifestyle factors and genetics."
    },
    "how accurate is the prediction": {
        type: "text",
        content: "The prediction is based on trained machine learning models and statistical analysis. While it provides strong indications, it is not a medical diagnosis and should not replace professional consultation."
    },
    "is this a replacement for a doctor": {
        type: "text",
        content: "No. This system is an early risk assessment tool. It does not replace medical professionals. Always consult a qualified doctor for diagnosis and treatment."
    },
    "how is my data stored": {
        type: "text",
        content: "Your data is securely stored in protected databases with controlled access. Security protocols are implemented to prevent unauthorized access."
    },
    "can i delete my data": {
        type: "text",
        content: "Yes. You may request deletion of your data through your account settings or by contacting support."
    },
    "how often should i take the assessment": {
        type: "text",
        content: "It is recommended to reassess every 3–6 months, or sooner if there are significant lifestyle or health changes."
    },
    "what does high risk mean": {
        type: "text",
        content: "A high-risk result indicates a strong probability of developing or already having risk indicators for a condition. You should consult a healthcare professional promptly."
    },
    "what does moderate risk mean": {
        type: "text",
        content: "Moderate risk suggests potential concern areas. Lifestyle modifications and preventive monitoring are advised."
    },
    "what does low risk mean": {
        type: "text",
        content: "Low risk indicates minimal current indicators. Maintaining healthy habits is recommended to stay in this range."
    },
    "who built this system": {
        type: "text",
        content: "This system was developed as a Smart Healthcare initiative combining machine learning, preventive healthcare analytics, and structured medical guidelines."
    },
    "is this service free": {
        type: "text",
        content: "Basic risk assessments are available for free. Additional advanced features may vary depending on system configuration."
    },
    "can i download my report": {
        type: "text",
        content: "Yes. After completing an assessment, you can download a detailed health risk report for your records."
    },
    "where can i consult a doctor": {
        type: "text",
        content: "You can visit the Doctors section to view available specialists and consultation options."
    },
    "are government schemes available": {
        type: "text",
        content: "Yes. We provide information about public healthcare schemes that may support eligible individuals."
    },
    "is this ai based": {
        type: "text",
        content: "Yes. The system uses machine learning algorithms to analyze patterns in medical data and generate risk predictions."
    },
    "how is ai used here": {
        type: "text",
        content: "AI analyzes health parameters and compares them with patterns learned from large datasets to estimate risk probabilities."
    },
    "can i use this on mobile": {
        type: "text",
        content: "Yes. The platform is fully responsive and optimized for mobile devices."
    },
    "is my chat saved": {
        type: "text",
        content: "Chat conversations may be stored to improve user experience and system performance, but sensitive information is protected."
    },
    "what if i get high risk": {
        type: "text",
        content: "If you receive a high-risk result, consult a doctor immediately. Early intervention significantly improves outcomes."
    },
    "take me to assessment": {
        type: "navigation",
        content: "You can start your health risk assessment below.",
        action: "/predict"
    },
    "take me to precautions": {
        type: "navigation",
        content: "You can explore preventive healthcare guidance below.",
        action: "/precautions"
    },
    "take me to doctors": {
        type: "navigation",
        content: "You can view available doctors below.",
        action: "/doctors"
    },
    "take me to dashboard": {
        type: "navigation",
        content: "Redirecting you to your dashboard.",
        action: "/dashboard"
    }
};

export function getFAQResponse(message) {
    const cleaned = message.toLowerCase().trim();

    for (let key in FAQ_RESPONSES) {
        if (cleaned.includes(key)) {
            return FAQ_RESPONSES[key];
        }
    }

    return null;
}
