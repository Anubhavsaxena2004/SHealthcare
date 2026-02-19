from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, jsonify, current_app, abort
from app import db
from app.models import User, Result, Doctor, DoctorProfile, PatientReport, DoctorReviewRequest, Notification
from app.services import get_preventive_measures, generate_pdf_report, predict_heart_risk, predict_diabetes_risk
from app.chatbot_service import healthcare_chatbot
from datetime import datetime
import os

main = Blueprint('main', __name__)

REVIEW_STATUS = {'pending', 'accepted', 'rejected', 'completed'}


def _current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


def _require_login():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return None


def _require_role(role: str):
    user = _current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if user.role != role:
        return jsonify({"error": "Forbidden"}), 403
    return None


def _notify(user_id: int, message: str):
    n = Notification(user_id=user_id, message=message, is_read=False)
    db.session.add(n)
    return n


def _result_inputs_for_report(result: Result):
    """
    Return a list of (label, value) pairs to embed in the PDF report,
    reflecting the exact fields the user entered for the prediction.
    """
    disease = (result.disease_selected or result.disease or "").lower()

    def yn(v):
        if v is None:
            return None
        try:
            return "Yes" if int(v) == 1 else "No"
        except Exception:
            return v

    def sex_label(v):
        if v is None:
            return None
        try:
            return "Male" if int(v) == 1 else "Female"
        except Exception:
            return v

    if "heart" in disease:
        return [
            ("Age", result.age),
            ("Sex", sex_label(result.sex)),
            ("Chest pain type (cp)", result.cp),
            ("Resting blood pressure (trestbps)", result.trestbps),
            ("Cholesterol (chol)", result.chol),
            ("Fasting blood sugar > 120 mg/dl (fbs)", yn(result.fbs)),
            ("Resting ECG (restecg)", result.restecg),
            ("Max heart rate achieved (thalach)", result.thalach),
            ("Exercise induced angina (exang)", yn(result.exang)),
            ("ST depression (oldpeak)", result.oldpeak),
            ("Slope (slope)", result.slope),
        ]

    # Default to diabetes fields when not heart
    return [
        ("Pregnancies", result.pregnancies),
        ("Glucose", result.glucose),
        ("Blood pressure (bp)", result.bp),
        ("Skin thickness", result.skin_thickness),
        ("Insulin", result.insulin),
        ("BMI", result.bmi),
        ("Diabetes pedigree function (dpf)", result.dpf),
        ("Age", result.age),
    ]


def _ensure_report_for_result(result: Result) -> PatientReport:
    report = PatientReport.query.filter_by(result_id=result.id).first()
    if report:
        return report

    report = PatientReport(
        patient_id=result.user_id,
        result_id=result.id,
        disease_type=result.disease_selected or result.disease,
        risk_score=float(result.probability or 0.0),
        report_file_path=None,
    )
    db.session.add(report)
    db.session.flush()

    # Persist a PDF copy for doctor access (optional). If it fails, pipeline still works.
    try:
        reports_dir = os.path.join(current_app.root_path, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        pdf_path = os.path.join(reports_dir, f"health_report_{result.id}.pdf")
        if not os.path.exists(pdf_path):
            data = {
                "username": User.query.get(result.user_id).username if User.query.get(result.user_id) else session.get('username', 'N/A'),
                "date": result.timestamp.strftime('%Y-%m-%d %H:%M:%S') if result.timestamp else '',
                "disease": result.disease,
                "prediction": result.prediction,
                "probability": result.probability,
                "inputs": _result_inputs_for_report(result),
            }
            buf = generate_pdf_report(data)
            with open(pdf_path, 'wb') as f:
                f.write(buf.getvalue())
        report.report_file_path = pdf_path
    except Exception:
        report.report_file_path = None

    return report


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

        new_user = User(username=username, email=email, password=password, role='patient')
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('signup.html')

@main.route('/doctor/register', methods=['GET', 'POST'])
def doctor_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        specialization = request.form['specialization']
        experience_years = int(request.form.get('experience_years') or 0)
        hospital = request.form.get('hospital', '')
        contact_number = request.form.get('contact_number', '')
        license_number = request.form['license_number']

        if User.query.filter_by(username=username).first():
            return "Username already taken. Try another."
        if User.query.filter_by(email=email).first():
            return "Email already taken. Try another."
        if DoctorProfile.query.filter_by(license_number=license_number).first():
            return "License number already registered."

        user = User(username=username, email=email, password=password, role='doctor')
        db.session.add(user)
        db.session.flush()

        profile = DoctorProfile(
            user_id=user.id,
            specialization=specialization,
            experience_years=experience_years,
            hospital=hospital,
            contact_number=contact_number,
            license_number=license_number,
            is_verified=True,
        )
        db.session.add(profile)
        db.session.commit()

        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return redirect(url_for('main.doctor_dashboard'))

    return render_template('doctor_register.html')

@main.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            if user.role == 'doctor':
                return redirect(url_for('main.doctor_dashboard'))
            return redirect(url_for('main.dashboard'))
        else:
            return "Invalid username or password."

    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    guard = _require_login()
    if guard:
        return guard
    user = _current_user()
    if user and user.role == 'doctor':
        return redirect(url_for('main.doctor_dashboard'))
    
    # Fetch user results for trends
    user_results = Result.query.filter_by(user_id=session['user_id']).order_by(Result.timestamp).all()
    
    trends_data = {
        "labels": [r.timestamp.strftime('%Y-%m-%d') for r in user_results],
        "probabilities": [r.probability if r.probability else 0 for r in user_results],
        "diseases": [r.disease_selected for r in user_results]
    }

    # Review requests + notifications
    my_requests = (
        DoctorReviewRequest.query
        .filter_by(patient_id=session['user_id'])
        .order_by(DoctorReviewRequest.updated_at.desc())
        .limit(25)
        .all()
    )
    my_requests_view = []
    for r in my_requests:
        doctor_user = User.query.get(r.doctor_id)
        my_requests_view.append({
            "id": r.id,
            "status": r.status,
            "doctor_id": r.doctor_id,
            "doctor_username": doctor_user.username if doctor_user else str(r.doctor_id),
            "doctor_notes": r.doctor_notes,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        })
    notifications = (
        Notification.query
        .filter_by(user_id=session['user_id'])
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        'dashboard.html',
        username=session['username'],
        trends_data=trends_data,
        my_requests=my_requests_view,
        notifications=notifications,
    )


@main.route('/doctor/dashboard')
def doctor_dashboard():
    guard = _require_login()
    if guard:
        return guard
    user = _current_user()
    if not user or user.role != 'doctor':
        return redirect(url_for('main.dashboard'))

    profile = DoctorProfile.query.filter_by(user_id=user.id).first()
    requests_q = (
        DoctorReviewRequest.query
        .filter_by(doctor_id=user.id)
        .order_by(DoctorReviewRequest.updated_at.desc())
        .limit(50)
        .all()
    )
    review_requests_view = []
    for r in requests_q:
        patient_user = User.query.get(r.patient_id)
        report = PatientReport.query.get(r.report_id) if r.report_id else None
        review_requests_view.append({
            "id": r.id,
            "status": r.status,
            "patient_id": r.patient_id,
            "patient_username": patient_user.username if patient_user else str(r.patient_id),
            "disease_type": report.disease_type if report else None,
            "risk_score": report.risk_score if report else None,
            "updated_at": r.updated_at,
            "doctor_notes": r.doctor_notes,
        })
    notifications = (
        Notification.query
        .filter_by(user_id=user.id)
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template('doctor_dashboard.html', doctor=user, profile=profile, review_requests=review_requests_view, notifications=notifications)

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
            result, probability = predict_heart_risk(data)
            if result is None:
                return "Heart model not loaded on server.", 500
            
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

            result, probability = predict_diabetes_risk(data)
            if result is None:
                return "Diabetes model not loaded on server.", 500

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
        "probability": result.probability,
        "inputs": _result_inputs_for_report(result),
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
    # Prefer verified doctor profiles when present; fallback to legacy Doctor table.
    q = db.session.query(DoctorProfile, User).join(User, DoctorProfile.user_id == User.id)
    q = q.filter(User.role == 'doctor')
    if search:
        q = q.filter((User.username.contains(search)) | (DoctorProfile.specialization.contains(search)) | (DoctorProfile.hospital.contains(search)))
    profiles = q.all()

    if profiles:
        doctors_view = [
            {
                "kind": "profile",
                "doctor_user_id": u.id,
                "name": u.username,
                "specialization": p.specialization,
                "experience": f"{p.experience_years} years",
                "hospital": p.hospital,
                "contact": p.contact_number,
                "is_verified": p.is_verified,
            }
            for (p, u) in profiles
        ]
    else:
        if search:
            legacy = Doctor.query.filter((Doctor.name.contains(search)) | (Doctor.specialization.contains(search))).all()
        else:
            legacy = Doctor.query.all()
        doctors_view = [
            {
                "kind": "legacy",
                "doctor_user_id": None,
                "name": d.name,
                "specialization": d.specialization,
                "experience": d.experience,
                "hospital": d.hospital,
                "contact": d.contact,
                "is_verified": True,
            }
            for d in legacy
        ]

    latest_result_id = None
    user = _current_user()
    if user and user.role == 'patient':
        latest = Result.query.filter_by(user_id=user.id).order_by(Result.timestamp.desc()).first()
        if latest:
            latest_result_id = latest.id

    return render_template('doctors.html', doctors=doctors_view, search=search, latest_result_id=latest_result_id)

@main.route('/government-support')
def government_schemes():
    return render_template('government_schemes.html')


# ==================== REVIEW PIPELINE (STATEFUL) ====================

@main.route('/api/doctors/', methods=['GET'])
def api_doctors():
    q = db.session.query(DoctorProfile, User).join(User, DoctorProfile.user_id == User.id)
    q = q.filter(User.role == 'doctor')
    verified_only = request.args.get('verified_only', '0').lower() in ('1', 'true', 'yes')
    if verified_only:
        q = q.filter(DoctorProfile.is_verified == True)  # noqa: E712
    doctors = q.all()
    return jsonify([
        {
            "doctor_user_id": u.id,
            "username": u.username,
            "specialization": p.specialization,
            "experience_years": p.experience_years,
            "hospital": p.hospital,
            "contact_number": p.contact_number,
            "is_verified": p.is_verified,
        }
        for (p, u) in doctors
    ])


@main.route('/api/request-review/', methods=['POST'])
def api_request_review():
    role_guard = _require_role('patient')
    if role_guard:
        return role_guard

    payload = request.get_json(silent=True) or {}
    doctor_user_id = payload.get('doctor_user_id')
    result_id = payload.get('result_id')
    if not doctor_user_id or not result_id:
        return jsonify({"error": "doctor_user_id and result_id are required"}), 400

    doctor = User.query.get(int(doctor_user_id))
    if not doctor or doctor.role != 'doctor':
        return jsonify({"error": "Invalid doctor"}), 400

    result = Result.query.get(int(result_id))
    if not result or result.user_id != session.get('user_id'):
        return jsonify({"error": "Invalid report"}), 400

    report = _ensure_report_for_result(result)
    # Prevent duplicate active requests for same report+doctor
    existing = DoctorReviewRequest.query.filter_by(
        patient_id=session['user_id'],
        doctor_id=doctor.id,
        report_id=report.id,
    ).order_by(DoctorReviewRequest.created_at.desc()).first()
    if existing and existing.status in ('pending', 'accepted', 'completed'):
        return jsonify({"error": "Request already exists", "request_id": existing.id, "status": existing.status}), 409

    req = DoctorReviewRequest(
        patient_id=session['user_id'],
        doctor_id=doctor.id,
        report_id=report.id,
        status='pending',
        doctor_notes=None,
    )
    db.session.add(req)
    _notify(doctor.id, f"New report review request from {session.get('username')}.")
    db.session.commit()

    return jsonify({"request_id": req.id, "status": req.status}), 201


@main.route('/api/my-requests/', methods=['GET'])
def api_my_requests():
    role_guard = _require_role('patient')
    if role_guard:
        return role_guard
    reqs = DoctorReviewRequest.query.filter_by(patient_id=session['user_id']).order_by(DoctorReviewRequest.updated_at.desc()).all()
    return jsonify([
        {
            "id": r.id,
            "status": r.status,
            "doctor_id": r.doctor_id,
            "report_id": r.report_id,
            "doctor_notes": r.doctor_notes,
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat(),
        }
        for r in reqs
    ])


@main.route('/api/doctor/requests/', methods=['GET'])
def api_doctor_requests():
    role_guard = _require_role('doctor')
    if role_guard:
        return role_guard
    reqs = DoctorReviewRequest.query.filter_by(doctor_id=session['user_id']).order_by(DoctorReviewRequest.updated_at.desc()).all()
    return jsonify([
        {
            "id": r.id,
            "status": r.status,
            "patient_id": r.patient_id,
            "report_id": r.report_id,
            "doctor_notes": r.doctor_notes,
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat(),
        }
        for r in reqs
    ])


def _get_doctor_request_or_404(request_id: int) -> DoctorReviewRequest:
    r = DoctorReviewRequest.query.get_or_404(request_id)
    if r.doctor_id != session.get('user_id'):
        abort(403)
    return r


@main.route('/api/doctor/accept/', methods=['POST'])
def api_doctor_accept():
    role_guard = _require_role('doctor')
    if role_guard:
        return role_guard
    payload = request.get_json(silent=True) or {}
    request_id = payload.get('request_id')
    if not request_id:
        return jsonify({"error": "request_id is required"}), 400
    r = _get_doctor_request_or_404(int(request_id))
    if r.status != 'pending':
        return jsonify({"error": "Only pending requests can be accepted"}), 409
    r.status = 'accepted'
    _notify(r.patient_id, "Your doctor has accepted your review request.")
    db.session.commit()
    return jsonify({"id": r.id, "status": r.status}), 200


@main.route('/api/doctor/reject/', methods=['POST'])
def api_doctor_reject():
    role_guard = _require_role('doctor')
    if role_guard:
        return role_guard
    payload = request.get_json(silent=True) or {}
    request_id = payload.get('request_id')
    reason = (payload.get('reason') or '').strip()
    if not request_id:
        return jsonify({"error": "request_id is required"}), 400
    r = _get_doctor_request_or_404(int(request_id))
    if r.status != 'pending':
        return jsonify({"error": "Only pending requests can be rejected"}), 409
    r.status = 'rejected'
    if reason:
        r.doctor_notes = reason
    _notify(r.patient_id, "Your doctor has rejected your review request.")
    db.session.commit()
    return jsonify({"id": r.id, "status": r.status}), 200


@main.route('/api/doctor/submit-review/', methods=['POST'])
def api_doctor_submit_review():
    role_guard = _require_role('doctor')
    if role_guard:
        return role_guard
    payload = request.get_json(silent=True) or {}
    request_id = payload.get('request_id')
    doctor_notes = (payload.get('doctor_notes') or '').strip()
    mark_completed = bool(payload.get('mark_completed', True))
    if not request_id:
        return jsonify({"error": "request_id is required"}), 400
    if not doctor_notes:
        return jsonify({"error": "doctor_notes is required"}), 400

    r = _get_doctor_request_or_404(int(request_id))
    if r.status not in ('accepted', 'completed'):
        return jsonify({"error": "Request must be accepted before submitting review"}), 409

    r.doctor_notes = doctor_notes
    if mark_completed:
        r.status = 'completed'
        _notify(r.patient_id, "Doctor completed your review. Check notes in your dashboard.")
    db.session.commit()
    return jsonify({"id": r.id, "status": r.status}), 200


@main.route('/api/review-request/<int:request_id>/report', methods=['GET'])
def api_get_report_for_request(request_id: int):
    """Doctor can access report only when accepted/completed. Patient can always access own report."""
    r = DoctorReviewRequest.query.get_or_404(request_id)
    user = _current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role == 'doctor':
        if r.doctor_id != user.id:
            return jsonify({"error": "Forbidden"}), 403
        if r.status not in ('accepted', 'completed'):
            return jsonify({"error": "Report not available until accepted"}), 403
    else:
        if r.patient_id != user.id:
            return jsonify({"error": "Forbidden"}), 403

    report = PatientReport.query.get_or_404(r.report_id)
    if report.report_file_path and os.path.exists(report.report_file_path):
        return send_file(report.report_file_path, as_attachment=False, mimetype='application/pdf')

    # Fallback: generate on the fly from Result
    result = Result.query.get_or_404(report.result_id)
    data = {
        "username": User.query.get(result.user_id).username if User.query.get(result.user_id) else 'N/A',
        "date": result.timestamp.strftime('%Y-%m-%d %H:%M:%S') if result.timestamp else '',
        "disease": result.disease,
        "prediction": result.prediction,
        "probability": result.probability,
        "inputs": _result_inputs_for_report(result),
    }
    pdf_buffer = generate_pdf_report(data)
    return send_file(pdf_buffer, as_attachment=False, download_name=f"health_report_{result.id}.pdf", mimetype='application/pdf')


@main.route('/api/notifications/', methods=['GET'])
def api_notifications():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    notes = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify([
        {
            "id": n.id,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in notes
    ])


@main.route('/api/notifications/mark-read/', methods=['POST'])
def api_notifications_mark_read():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    notification_id = payload.get('notification_id')
    if not notification_id:
        return jsonify({"error": "notification_id is required"}), 400
    n = Notification.query.get_or_404(int(notification_id))
    if n.user_id != session['user_id']:
        return jsonify({"error": "Forbidden"}), 403
    n.is_read = True
    db.session.commit()
    return jsonify({"id": n.id, "is_read": n.is_read}), 200


