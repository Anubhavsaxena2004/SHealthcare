from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, jsonify
from app import db
from app.models import User, Result
from app.services import heart_model, diabetes_model, get_preventive_measures, generate_pdf_report
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
