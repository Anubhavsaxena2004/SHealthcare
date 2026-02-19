from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')  # 'patient' | 'doctor'

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disease = db.Column(db.String(50), nullable=False)
    prediction = db.Column(db.String(10), nullable=False)
    probability = db.Column(db.Float, nullable=True)
    disease_selected = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Heart disease fields
    age = db.Column(db.Integer)
    sex = db.Column(db.Integer)
    cp = db.Column(db.Integer)
    trestbps = db.Column(db.Integer)
    chol = db.Column(db.Integer)
    fbs = db.Column(db.Integer)
    restecg = db.Column(db.Integer)
    thalach = db.Column(db.Integer)
    exang = db.Column(db.Integer)
    oldpeak = db.Column(db.Float)
    slope = db.Column(db.Integer)

    # Diabetes fields
    pregnancies = db.Column(db.Integer)
    glucose = db.Column(db.Float)
    bp = db.Column(db.Float)
    skin_thickness = db.Column(db.Float)
    insulin = db.Column(db.Float)
    bmi = db.Column(db.Float)
    dpf = db.Column(db.Float)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    hospital = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(200), nullable=True) # URL or path


class DoctorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False, index=True)
    specialization = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, nullable=False, default=0)
    hospital = db.Column(db.String(200), nullable=False, default='')
    contact_number = db.Column(db.String(20), nullable=False, default='')
    license_number = db.Column(db.String(50), nullable=False, unique=True, index=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('doctor_profile', uselist=False))


class PatientReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False, unique=True, index=True)
    disease_type = db.Column(db.String(50), nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    report_file_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    patient = db.relationship('User', foreign_keys=[patient_id])
    result = db.relationship('Result')


class DoctorReviewRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.String(20), nullable=False, default='pending')  # pending|accepted|rejected|completed

    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    report_id = db.Column(db.Integer, db.ForeignKey('patient_report.id'), nullable=False, index=True)

    doctor_notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    patient = db.relationship('User', foreign_keys=[patient_id], backref=db.backref('sent_review_requests', lazy='dynamic'))
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref=db.backref('received_review_requests', lazy='dynamic'))
    report = db.relationship('PatientReport')


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

