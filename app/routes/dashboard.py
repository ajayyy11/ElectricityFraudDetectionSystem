from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, Response
from flask_login import login_required, current_user
import csv
import io
import joblib
import os
import random
from app.models import db, EnergyRecord
from datetime import datetime
from app.services.ml_engine import ml_engine

dashboard = Blueprint('dashboard', __name__)

# Using ml_engine service instead of local implementation


def build_dashboard_context(page=1):
    from app.services.scoring import monthly_change
    from app.services.prediction import predict_next_usage
    from app.services.insights import generate_insight

    history_all = EnergyRecord.query.filter_by(user_id=current_user.id)\
        .order_by(EnergyRecord.id.desc()).all()

    if len(history_all) >= 3:
        avg_usage = round(sum(r.usage for r in history_all[-10:]) / min(len(history_all), 10), 2)
    else:
        avg_usage = 410

    latest = history_all[0] if history_all else None

    current_usage = latest.usage if latest else 420
    fraud_probability = latest.fraud_probability if latest else 0.1
    epi = latest.epi_score if latest else 80.0
    anomaly_status = latest.anomaly_status if latest else "Usage within normal range"

    previous_usage = history_all[1].usage if len(history_all) >= 2 else current_usage
    change = monthly_change(current_usage, previous_usage)

    predicted = predict_next_usage(current_usage, avg_usage)
    insight_text = generate_insight(current_usage, avg_usage, fraud_probability, predicted)

    # Month comparison
    if len(history_all) >= 2:
        previous_month_fraud = 1 if history_all[1].fraud_probability > 0.2 else 0
        current_month_fraud = 1 if history_all[0].fraud_probability > 0.2 else 0
        last_month_usage = history_all[1].usage
        month_change = round(((current_usage - last_month_usage) / last_month_usage) * 100, 2) if last_month_usage else 0
    else:
        previous_month_fraud = 0
        current_month_fraud = 0
        month_change = 0

    # Risk distribution
    fraud_count = len([r for r in history_all if r.fraud_probability > 0.3])
    normal_count = len(history_all) - fraud_count
    low_risk = len([r for r in history_all if r.fraud_probability <= 0.3])
    medium_risk = len([r for r in history_all if 0.3 < r.fraud_probability <= 0.6])
    high_risk = len([r for r in history_all if r.fraud_probability > 0.6])

    # Active alert count
    active_alerts = len([r for r in history_all[:5] if r.fraud_probability > 0.2])

    # EPI trend
    avg_epi = round(sum(r.epi_score for r in history_all) / len(history_all), 2) if history_all else 80.0
    epi_change = round(epi - avg_epi, 2) if history_all else 0

    # Pagination
    per_page = 10
    total = len(history_all)
    start = (page - 1) * per_page
    end = start + per_page
    history_page = history_all[start:end]
    total_pages = max(1, (total + per_page - 1) // per_page)

    return dict(
        epi=epi,
        fraud=round(fraud_probability * 100, 2),
        usage=current_usage,
        avg_usage=avg_usage,
        change=change,
        month_change=month_change,
        predicted=predicted,
        anomaly=anomaly_status,
        insight=insight_text,
        history=history_page,
        total_pages=total_pages,
        current_page=page,
        fraud_count=fraud_count,
        normal_count=normal_count,
        previous_month_fraud=previous_month_fraud,
        current_month_fraud=current_month_fraud,
        low_risk=low_risk,
        medium_risk=medium_risk,
        high_risk=high_risk,
        active_alerts=active_alerts,
        epi_change=epi_change,
        total_records=total,
        avg_epi=avg_epi
    )


@dashboard.route("/")
@login_required
def main_dashboard():
    page = request.args.get('page', 1, type=int)
    ctx = build_dashboard_context(page)
    return render_template("dashboard.html", **ctx)


@dashboard.route("/refresh", methods=["POST"])
@login_required
def refresh_reading():
    history_all = EnergyRecord.query.filter_by(user_id=current_user.id)\
        .order_by(EnergyRecord.id.desc()).all()

    if len(history_all) >= 3:
        avg_usage = round(sum(r.usage for r in history_all[-10:]) / min(len(history_all), 10), 2)
    else:
        avg_usage = 410

    current_usage = random.randint(360, 500)
    ml_engine.predict_and_save(current_user.id, current_usage, avg_usage)
    flash("New energy reading captured successfully!", "success")
    return redirect(url_for("dashboard.main_dashboard"))


@dashboard.route("/risk")
@login_required
def risk():
    page = request.args.get('page', 1, type=int)
    ctx = build_dashboard_context(page)
    return render_template("risk.html", **ctx)


@dashboard.route("/insights")
@login_required
def insights():
    page = request.args.get('page', 1, type=int)
    ctx = build_dashboard_context(page)
    return render_template("insights.html", **ctx)


@dashboard.route("/reports")
@login_required
def reports():
    page = request.args.get('page', 1, type=int)
    ctx = build_dashboard_context(page)
    return render_template("reports.html", **ctx)


def _csv_safe(value):
    """Prevent spreadsheet formula execution when opening exported text in Excel."""
    if not isinstance(value, str):
        return value
    trimmed = value.lstrip()
    if trimmed.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


@dashboard.route("/reports/export.csv")
@login_required
def export_user_csv():
    """Export only the signed-in user's own energy and fraud records."""
    records = EnergyRecord.query.filter_by(user_id=current_user.id)\
        .order_by(EnergyRecord.timestamp.desc(), EnergyRecord.id.desc()).all()

    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow([
        "Record ID", "Usage (kWh)", "Average Usage (kWh)",
        "Fraud Risk (%)", "EPI Score", "Anomaly Status", "Explanation", "Timestamp"
    ])

    for record in records:
        writer.writerow([
            record.id,
            record.usage,
            record.avg_usage,
            round(record.fraud_probability * 100, 2),
            record.epi_score,
            _csv_safe(record.anomaly_status or ""),
            _csv_safe(record.reason or ""),
            record.timestamp.strftime("%Y-%m-%d %H:%M:%S") if record.timestamp else "",
        ])

    response = Response("\ufeff" + output.getvalue(), mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = 'attachment; filename="my_energy_fraud_report.csv"'
    response.headers["Cache-Control"] = "no-store"
    return response


@dashboard.route("/profile")
@login_required
def profile():
    history = EnergyRecord.query.filter_by(user_id=current_user.id)\
        .order_by(EnergyRecord.id.desc()).all()

    total_records = len(history)
    avg_epi = round(sum(r.epi_score for r in history) / total_records, 2) if history else 0
    avg_fraud = round(sum(r.fraud_probability for r in history) / total_records * 100, 2) if history else 0
    high_risk_count = len([r for r in history if r.fraud_probability > 0.6])

    return render_template("profile.html",
        total_records=total_records,
        avg_epi=avg_epi,
        avg_fraud=avg_fraud,
        high_risk_count=high_risk_count,
        member_since=current_user.created_at.strftime("%B %d, %Y") if current_user.created_at else "N/A"
    )


@dashboard.route('/profile/edit', methods=['POST'])
@login_required
def self_edit_user():
    current_user.email = request.form.get('email')
    db.session.commit()
    flash('Profile updated successfully.', 'success')
    return redirect(url_for('dashboard.profile'))


@dashboard.route('/api/dashboard-data')
@login_required
def dashboard_data():
    history = EnergyRecord.query.filter_by(user_id=current_user.id)\
        .order_by(EnergyRecord.id.desc()).limit(10).all()

    fraud_count = len([r for r in history if r.fraud_probability > 0.2])
    normal_count = len(history) - fraud_count

    return jsonify({
        "usage": [r.usage for r in history][::-1],
        "fraud_probs": [round(r.fraud_probability * 100, 2) for r in history][::-1],
        "epi_scores": [r.epi_score for r in history][::-1],
        "fraud_count": fraud_count,
        "normal_count": normal_count
    })
