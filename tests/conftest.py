import os
import sys

import pytest

# Ensure the repository root is importable when pytest is launched from any directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.models import db


@pytest.fixture
def app(tmp_path):
    app = create_app("development")
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-only-secret-key-not-for-production",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'test.db'}",
        WTF_CSRF_ENABLED=False,
        RATELIMIT_ENABLED=False,
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
