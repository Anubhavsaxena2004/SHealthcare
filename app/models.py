from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disease = db.Column(db.String(50), nullable=False)
    prediction = db.Column(db.String(10), nullable=False)
    probability = db.Column(db.Float, nullable=True)  # New field for charts
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
