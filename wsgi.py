"""WSGI entry point for Render and other production WSGI hosts."""

import os

from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app
from app.models import db

app = create_app(os.environ.get("APP_CONFIG", "production"))

# Render terminates HTTPS at its proxy. Trust the forwarded scheme so
# Flask-Talisman can enforce HTTPS without redirect loops.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# This demo currently uses SQLAlchemy create_all rather than migrations.
# Keep startup self-contained so a fresh deployment has its tables.
with app.app_context():
    db.create_all()
