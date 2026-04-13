from app import create_app, db
import os

app = create_app()

with app.app_context():
    # Use create_all to ensure all tables defined in models are created
    db.create_all()
    print("Database tables created successfully.")
