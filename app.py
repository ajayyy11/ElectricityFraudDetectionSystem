from app import create_app
from app.models import db

app = create_app('development')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database structure verified.")

    app.run(debug=True)
