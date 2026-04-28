from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    energy_records = db.relationship('EnergyRecord', backref='user', lazy=True)


class EnergyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usage = db.Column(db.Float, nullable=False)
    avg_usage = db.Column(db.Float, nullable=False)
    fraud_probability = db.Column(db.Float, nullable=False)
    epi_score = db.Column(db.Float, nullable=False)
    anomaly_status = db.Column(db.String(100))
    reason = db.Column(db.String(500))  # New: AI-driven explanation
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
