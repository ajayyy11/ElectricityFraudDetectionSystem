import os

from app import create_app
from app.models import db

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY is required. Add a strong random SECRET_KEY to your local .env file."
        )

    with app.app_context():
        db.create_all()
        print("Database structure verified.")

    app.run(debug=app.config.get("DEBUG", False), host="127.0.0.1")
