from urllib.parse import urlsplit

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User
from app import limiter

auth = Blueprint('auth', __name__)


def _safe_next_url(target):
    """Allow only local absolute paths; reject external and scheme-relative URLs."""
    if not isinstance(target, str) or not target.startswith("/") or target.startswith("//"):
        return None
    if "\\" in target:
        return None
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None
    return target


@auth.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.main_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.", "danger")
        elif User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
        elif email and User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
        else:
            # The first account bootstraps the administrator; public registrations
            # after that always receive the least-privileged role.
            is_first_user = User.query.count() == 0
            assigned_role = "admin" if is_first_user else "user"

            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email or None,
                password=hashed_password,
                role=assigned_role,
            )
            db.session.add(new_user)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.main_dashboard"))

    if request.method == "POST":
        identity = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not identity or not password:
            flash("Please enter your credentials.", "danger")
            return render_template("login.html")

        # Check for user by username OR email
        user = User.query.filter((User.username == identity) | (User.email == identity)).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = _safe_next_url(request.args.get("next"))
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page or url_for("dashboard.main_dashboard"))

        flash("Invalid username or password.", "danger")
        return render_template("login.html")

    return render_template("login.html")


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
