from flask import Flask, render_template
from services.scoring import calculate_epi, monthly_change
from services.prediction import predict_next_usage, detect_anomaly
from services.insights import generate_insight
import random
from flask import jsonify
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import csv
from flask import Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import joblib
model = joblib.load("fraud_model.pkl")
scaler = joblib.load("scaler.pkl")

# -------------------------
# App Setup
# -------------------------
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eip.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'superpasskey99970'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------------
# Database Models
# -------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")  # NEW

    energy_records = db.relationship('EnergyRecord', backref='user', lazy=True)



class EnergyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usage = db.Column(db.Float, nullable=False)
    avg_usage = db.Column(db.Float, nullable=False)
    fraud_probability = db.Column(db.Float, nullable=False)
    epi_score = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# -------------------------
# Data Generator (Temporary)
# -------------------------
def generate_data():
    current_usage = random.randint(380, 460)
    avg_usage = 410
    previous_usage = 400
    fraud_probability = round(random.uniform(0.05, 0.30), 2)

    epi = calculate_epi(current_usage, avg_usage, fraud_probability)
    change = monthly_change(current_usage, previous_usage)
    predicted = predict_next_usage(current_usage, avg_usage)
    anomaly_status = detect_anomaly(current_usage, avg_usage)
    insight_text = generate_insight(current_usage, avg_usage, fraud_probability, predicted)

    return {
        "epi": epi,
        "fraud": fraud_probability * 100,
        "usage": current_usage,
        "change": change,
        "predicted": predicted,
        "anomaly": anomaly_status,
        "insight": insight_text
    }

# -------------------------
# Routes
# -------------------------

@app.route("/risk")
def risk():
    data = generate_data()
    return render_template("risk.html", **data)


@app.route("/insights")
def insights():
    data = generate_data()
    return render_template("insights.html", **data)


@app.route("/reports")
def reports():
    data = generate_data()
    return render_template("reports.html", **data)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Prevent duplicate usernames
        if User.query.filter_by(username=username).first():
            return "Username already exists"

        # If first user → make admin
        if User.query.count() == 0:
            role = "admin"
        else:
            role = "user"

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        return "Invalid username or password"

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ===============================
# USER DASHBOARD
# ===============================
@app.route("/")
@login_required
def dashboard():

    # Simulate current usage
    current_usage = random.randint(380, 460)
    avg_usage = 410
    previous_usage = 400

    # ===============================
    # ML FRAUD PREDICTION
    # ===============================
    scaled_input = scaler.transform([[current_usage, avg_usage]])
    fraud_probability = model.predict_proba(scaled_input)[0][1]

    # Your existing logic
    epi = calculate_epi(current_usage, avg_usage, fraud_probability)
    change = monthly_change(current_usage, previous_usage)
    predicted = predict_next_usage(current_usage, avg_usage)
    anomaly_status = detect_anomaly(current_usage, avg_usage)
    insight_text = generate_insight(
        current_usage, avg_usage, fraud_probability, predicted
    )

    # ===============================
    # SAVE TO DATABASE
    # ===============================
    new_record = EnergyRecord(
        usage=current_usage,
        avg_usage=avg_usage,
        fraud_probability=fraud_probability,
        epi_score=epi,
        user_id=current_user.id
    )

    db.session.add(new_record)
    db.session.commit()

    # ===============================
    # FETCH USER HISTORY
    # ===============================
    history = EnergyRecord.query.filter_by(user_id=current_user.id)\
        .order_by(EnergyRecord.id.desc()).all()

    # ===============================
    # FRAUD VS NORMAL
    # ===============================
    fraud_count = len([r for r in history if r.fraud_probability > 0.3])
    normal_count = len(history) - fraud_count

    # ===============================
    # MONTH FRAUD COMPARISON
    # ===============================
    if len(history) >= 2:
        previous_month_fraud = 1 if history[1].fraud_probability > 0.2 else 0
        current_month_fraud = 1 if history[0].fraud_probability > 0.2 else 0

        last_month_usage = history[1].usage
        month_change = round(
            ((current_usage - last_month_usage) / last_month_usage) * 100, 2
        )
    else:
        previous_month_fraud = 0
        current_month_fraud = 0
        month_change = 0

    # ===============================
    # RISK DISTRIBUTION
    # ===============================
    low_risk = len([r for r in history if r.fraud_probability <= 0.3])
    medium_risk = len([r for r in history if 0.3 < r.fraud_probability <= 0.6])
    high_risk = len([r for r in history if r.fraud_probability > 0.6])
    return render_template(
        "dashboard.html",
        epi=epi,
        fraud=round(fraud_probability * 100, 2),
        usage=current_usage,
        change=change,
        month_change=month_change,
        predicted=predicted,
        anomaly=anomaly_status,
        insight=insight_text,
        history=history,

        fraud_count=fraud_count,
        normal_count=normal_count,
        previous_month_fraud=previous_month_fraud,
        current_month_fraud=current_month_fraud,
        low_risk=low_risk,
        medium_risk=medium_risk,
        high_risk=high_risk
    )


# ===============================
# REAL-TIME API
# ===============================
@app.route('/api/dashboard-data')
@login_required
def dashboard_data():

    history = EnergyRecord.query.filter_by(user_id=current_user.id)\
        .order_by(EnergyRecord.id.desc()).limit(10).all()

    fraud_count = len([r for r in history if r.fraud_probability > 0.2])
    normal_count = len(history) - fraud_count

    return jsonify({
        "usage": [r.usage for r in history][::-1],
        "fraud_count": fraud_count,
        "normal_count": normal_count
    })


# ===============================
# ADMIN DASHBOARD
# ===============================
@app.route("/admin")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        return "Access Denied", 403

    users = User.query.all()
    user_ranking = []

    for user in users:
        records = EnergyRecord.query.filter_by(user_id=user.id).all()

        if records:
            avg_fraud = sum(r.fraud_probability for r in records) / len(records)
        else:
            avg_fraud = 0

        user_ranking.append({
            "username": user.username,
            "role": user.role,
            "avg_fraud": round(avg_fraud * 100, 2)
        })

    user_ranking.sort(key=lambda x: x["avg_fraud"], reverse=True)

    return render_template("admin.html", ranking=user_ranking)


# ===============================
# EXPORT CSV
# ===============================
@app.route("/admin/export")
@login_required
def export_csv():

    if current_user.role != "admin":
        return "Access Denied", 403

    records = EnergyRecord.query.all()

    def generate():
        yield "Username,Usage,Fraud%,EPI\n"
        for r in records:
            yield f"{r.user.username},{r.usage},{round(r.fraud_probability*100,2)},{r.epi_score}\n"

    return Response(
        generate(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=fraud_report.csv"}
    )





# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
