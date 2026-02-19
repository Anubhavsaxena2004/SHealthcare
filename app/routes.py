from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, jsonify
from app import db
from app.models import User, Result, Doctor
from app.services import heart_model, diabetes_model, get_preventive_measures, generate_pdf_report
from app.chatbot_service import healthcare_chatbot
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already taken. Try another."

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('signup.html')

@main.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.dashboard'))
        else:
            return "Invalid username or password."

    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    # Fetch user results for trends
    user_results = Result.query.filter_by(user_id=session['user_id']).order_by(Result.timestamp).all()
    
    trends_data = {
        "labels": [r.timestamp.strftime('%Y-%m-%d') for r in user_results],
        "probabilities": [r.probability if r.probability else 0 for r in user_results],
        "diseases": [r.disease_selected for r in user_results]
    }

    return render_template('dashboard.html', username=session['username'], trends_data=trends_data)

@main.route('/select-disease', methods=['GET', 'POST'])
def select_disease():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        selected_disease = request.form.get('disease')
        session['selected_disease'] = selected_disease
        if selected_disease == "Heart Disease":
            return redirect(url_for('main.predict_heart'))
        else:
            return redirect(url_for('main.predict_diabetes'))

    return render_template('select-disease.html')

@main.route('/predict-heart', methods=['POST', 'GET'])
def predict_heart():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        try:
            # Form data extraction (simulated for brevity, assume similar to original)
            data = [
                int(request.form['age']), int(request.form['sex']), int(request.form['cp']),
                int(request.form['trestbps']), int(request.form['chol']), int(request.form['fbs']),
                int(request.form['restecg']), int(request.form['thalach']), int(request.form['exang']),
                float(request.form['oldpeak']), int(request.form['slope'])
            ]
            
            # Predict
            result = heart_model.predict([data])[0]
            probability = heart_model.predict_proba([data])[0][1] # Probability of heart disease
            
            prediction_text = "Heart Disease" if result == 1 else "No Heart Disease"
            
            new_result = Result(
                user_id=session['user_id'],
                disease="Heart Disease",
                prediction=prediction_text,
                probability=round(probability * 100, 2),
                disease_selected="Heart Disease",
                # Log other fields...
                age=data[0], sex=data[1], cp=data[2], trestbps=data[3], chol=data[4],
                fbs=data[5], restecg=data[6], thalach=data[7], exang=data[8],
                oldpeak=data[9], slope=data[10]
            )
            db.session.add(new_result)
            db.session.commit()
            
            guidance = get_preventive_measures("Heart Disease", probability)

            return render_template('results-heart.html', result=result, probability=round(probability*100, 2), guidance=guidance, result_id=new_result.id)

        except Exception as e:
            return f"Error: {e}"

    return render_template('predict-heart.html')

@main.route('/predict-diabetes', methods=['POST', 'GET'])
def predict_diabetes():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        try:
            data = [
                int(request.form['pregnancies']), float(request.form['glucose']), float(request.form['bp']),
                float(request.form['skin_thickness']), float(request.form['insulin']), float(request.form['bmi']),
                float(request.form['dpf']), int(request.form['age'])
            ]

            result = diabetes_model.predict([data])[0]
            probability = diabetes_model.predict_proba([data])[0][1]

            prediction_text = "Diabetes" if result == 1 else "No Diabetes"

            new_result = Result(
                user_id=session['user_id'],
                disease="Diabetes",
                prediction=prediction_text,
                probability=round(probability * 100, 2),
                disease_selected="Diabetes",
                pregnancies=data[0], glucose=data[1], bp=data[2], skin_thickness=data[3],
                insulin=data[4], bmi=data[5], dpf=data[6], age=data[7]
            )
            db.session.add(new_result)
            db.session.commit()

            guidance = get_preventive_measures("Diabetes", probability)

            return render_template('results-diabetes.html', result=result, probability=round(probability*100, 2), guidance=guidance, result_id=new_result.id)

        except Exception as e:
             return f"Error: {e}"

    return render_template('predict-diabetes.html')

@main.route('/download_report/<int:result_id>')
def download_report(result_id):
    result = Result.query.get_or_404(result_id)
    if result.user_id != session.get('user_id'):
        return "Unauthorized", 403
    
    data = {
        "username": session['username'],
        "date": result.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        "disease": result.disease,
        "prediction": result.prediction,
        "probability": result.probability
    }
    
    pdf_buffer = generate_pdf_report(data)
    
    return send_file(pdf_buffer, as_attachment=True, download_name=f"health_report_{result_id}.pdf", mimetype='application/pdf')

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


# ==================== HEALTHCARE CHATBOT ENDPOINTS ====================

@main.route('/api/health-chat', methods=['POST'])
def health_chat():
    """
    Healthcare-specific chatbot endpoint
    Handles medical questions, risk explanations, preventive guidance
    
    Request:
    {
        "message": "Explain my diabetes risk",
        "user_id": 1
    }
    
    Response:
    {
        "type": "health_response",
        "reply": "Your diabetes risk is...",
        "suggested_actions": ["Download Report", "Schedule Consultation"],
        "disclaimer": "This is educational guidance..."
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id') or session.get('user_id')
        message = data.get('message', '').strip()

        if not user_id:
            return jsonify({
                "type": "error",
                "reply": "User not authenticated. Please log in first.",
                "suggested_actions": ["Login", "Signup"]
            }), 401

        if not message:
            return jsonify({
                "type": "error",
                "reply": "Please provide a message.",
                "suggested_actions": ["Try asking about your risk", "Ask prevention tips"]
            }), 400

        # Get user context
        context = healthcare_chatbot.get_conversation_context(user_id)

        # Process healthcare chat
        response = healthcare_chatbot.process_health_chat(user_id, message)

        # If no specialized response, try general chat
        if response is None:
            response = healthcare_chatbot.process_general_chat(message)

        # Add context
        response['user_context'] = context
        response['timestamp'] = datetime.utcnow().isoformat()

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "type": "error",
            "reply": f"An error occurred: {str(e)}",
            "suggested_actions": ["Try again", "Contact support"]
        }), 500


@main.route('/api/general-chat', methods=['POST'])
def general_chat():
    """
    General knowledge chatbot endpoint (OpenAI fallback)
    Handles non-medical questions with healthcare awareness
    
    Request:
    {
        "message": "What is machine learning?",
        "user_id": 1  (optional)
    }
    
    Response:
    {
        "type": "ai_response",
        "reply": "Machine learning is...",
        "source": "OpenAI GPT-4o-mini",
        "disclaimer": "This is educational guidance..."
    }
    """
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_id = data.get('user_id') or session.get('user_id')

        if not message:
            return jsonify({
                "type": "error",
                "reply": "Please provide a message.",
                "suggested_actions": ["Ask a question", "Try a healthcare question"]
            }), 400

        # Check if it's actually a healthcare-related question
        intent = healthcare_chatbot.detect_intent(message)
        if intent != "general":
            # Route to healthcare endpoint instead
            if user_id:
                response = healthcare_chatbot.process_health_chat(user_id, message)
                if response is None:
                    response = healthcare_chatbot.process_general_chat(message)
            else:
                response = healthcare_chatbot.process_general_chat(message)
        else:
            # Process purely general query
            response = healthcare_chatbot.process_general_chat(message)

        response['timestamp'] = datetime.utcnow().isoformat()
        if user_id:
            response['user_context'] = healthcare_chatbot.get_conversation_context(user_id)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "type": "error",
            "reply": f"An error occurred: {str(e)}",
            "suggested_actions": ["Try again", "Contact support"]
        }), 500


@main.route('/api/chat-suggestions/<int:user_id>', methods=['GET'])
def chat_suggestions(user_id):
    """
    Get suggested chat prompts based on user's latest assessment
    Helps users know what they can ask the chatbot
    """
    try:
        if session.get('user_id') != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        context = healthcare_chatbot.get_conversation_context(user_id)
        suggestions = [
            "Explain my last result",
            "How can I improve my score?",
            "What causes high diabetes risk?",
            "Prevention tips for heart disease",
            "Go to dashboard"
        ]

        if context.get('last_disease'):
            suggestions.insert(0, f"Tell me about my {context['last_disease']} risk")
            suggestions.insert(1, f"How to prevent {context['last_disease']}?")

        return jsonify({
            "suggestions": suggestions,
            "context": context
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route('/precautions')
def precautions():
    return render_template('precautions.html')

@main.route('/doctors')
def doctors():
    search = request.args.get('search', '')
    if search:
        doctors = Doctor.query.filter((Doctor.name.contains(search)) | (Doctor.specialization.contains(search))).all()
    else:
        doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors, search=search)

@main.route('/government-support')
def government_schemes():
    return render_template('government_schemes.html')


