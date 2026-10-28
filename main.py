"""Compatibility entry point for Render's existing gunicorn main:app command.

The actual Flask application factory and production setup live in wsgi.py.
"""
from wsgi import app

__all__ = ["app"]
