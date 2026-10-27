import os

from app import create_app
from app.models import db

app = create_app(os.environ.get("FLASK_ENV", "development"))


def _validate_secret_key():
    secret = app.config.get("SECRET_KEY")
    placeholders = {
        "",
        "replace-with-a-unique-random-secret",
        "dev-fallback-key-change-in-production",
        "your_secret_key",
        "change-me",
    }
    if not isinstance(secret, str) or len(secret) < 32 or secret.strip().lower() in placeholders:
        raise RuntimeError(
            "Set SECRET_KEY to a unique random value of at least 32 characters in .env. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )


if __name__ == "__main__":
    _validate_secret_key()
    with app.app_context():
        db.create_all()
        print("Database structure verified.")

    app.run(debug=app.config.get("DEBUG", False), host="127.0.0.1")
