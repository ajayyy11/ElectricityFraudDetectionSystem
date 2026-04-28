from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, Response
from flask_login import login_required, current_user
from flask_mail import Message
from app.models import db, User, EnergyRecord
from app import mail

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Administrator privileges required.', 'danger')
        return redirect(url_for('dashboard.main_dashboard'))
    
    users = User.query.all()
    total_users = User.query.count()
    total_readings = EnergyRecord.query.count()
    high_risk_count = EnergyRecord.query.filter(EnergyRecord.fraud_probability > 0.6).count()
    medium_risk_count = EnergyRecord.query.filter(EnergyRecord.fraud_probability > 0.3, EnergyRecord.fraud_probability <= 0.6).count()
    total_anomalies = EnergyRecord.query.filter(EnergyRecord.anomaly_status).count()
    latest_readings = EnergyRecord.query.order_by(EnergyRecord.timestamp.desc()).limit(10).all()

    return render_template('admin.html', 
                           users=users, 
                           total_users=total_users, 
                           total_readings=total_readings, 
                           high_risk_count=high_risk_count,
                           medium_risk_count=medium_risk_count,
                           total_anomalies=total_anomalies,
                           latest_readings=latest_readings)


@admin.route('/user/edit/<int:user_id>', methods=['POST'])
@login_required
def admin_edit_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get_or_404(user_id)
    user.username = request.form.get('username')
    user.email = request.form.get('email')
    user.role = request.form.get('role')
    
    db.session.commit()
    flash(f'User {user.username} updated successfully.', 'success')
    return redirect(url_for('admin.admin_dashboard'))


@admin.route('/user/notify/<int:user_id>', methods=['POST'])
@login_required
def send_usage_email(user_id):
    if current_user.role != 'admin':
        flash('Unauthorized.', 'danger')
        return redirect(url_for('dashboard.main_dashboard'))
    
    user = User.query.get_or_404(user_id)
    if not user.email:
        flash(f'User {user.username} has no email set.', 'warning')
        return redirect(url_for('admin.admin_dashboard'))
    
    latest_record = EnergyRecord.query.filter_by(user_id=user.id).order_by(EnergyRecord.timestamp.desc()).first()
    
    if not latest_record:
        flash('No usage data found for this user.', 'warning')
        return redirect(url_for('admin.admin_dashboard'))

    try:
        msg = Message("EFD System: Your Usage Report",
                      recipients=[user.email])
        msg.body = f"""
Hello {user.username},

This is an automated usage report from the Electricity Fraud Detection Platform.

Latest Reading Details:
- Consumption: {latest_record.usage} kWh
- Fraud Risk Probability: {round(latest_record.fraud_probability * 100, 2)}%
- EPI Score: {latest_record.epi_score}
- Status: {'Suspicious Activity Detected' if latest_record.fraud_probability > 0.5 else 'Normal Usage'}

Please log in to your dashboard for more details.

Security Team,
EFD Platform
"""
        mail.send(msg)
        flash(f'Notification sent to {user.email}', 'success')
    except Exception as e:
        flash(f'Error sending email: {str(e)}', 'danger')
        
    return redirect(url_for('admin.admin_dashboard'))


@admin.route('/reset-database', methods=['POST'])
@login_required
def reset_database():
    if current_user.role != 'admin':
        flash('Unauthorized.', 'danger')
        return redirect(url_for('dashboard.main_dashboard'))
    
    try:
        # Close all connections first (to avoid busy DB on Windows)
        db.session.remove()
        db.drop_all()
        db.create_all()
        
        # Ensure 'email' column is added back (since drop_all removes it)
        from sqlalchemy import text
        try:
            db.session.execute(text("ALTER TABLE user ADD COLUMN email VARCHAR(120)"))
            db.session.commit()
        except:
            pass # Already created by create_all if model was updated
            
        flash('Database has been completely reset. All data cleared.', 'success')
    except Exception as e:
        flash(f'Error resetting database: {str(e)}', 'danger')
        
    return redirect(url_for('admin.admin_dashboard'))


@admin.route("/export")
@login_required
def export_csv():
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard.main_dashboard"))

    records = EnergyRecord.query.all()

    def generate():
        yield "Username,Usage (kWh),Avg Usage,Fraud%,EPI Score,Anomaly,Timestamp\n"
        for r in records:
            yield (
                f"{r.user.username},"
                f"{r.usage},"
                f"{r.avg_usage},"
                f"{round(r.fraud_probability * 100, 2)},"
                f"{r.epi_score},"
                f"{r.anomaly_status or 'N/A'},"
                f"{r.timestamp.strftime('%Y-%m-%d %H:%M') if r.timestamp else 'N/A'}\n"
            )

    return Response(
        generate(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=fraud_report.csv"}
    )
