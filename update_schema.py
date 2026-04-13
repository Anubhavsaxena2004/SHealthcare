from app import create_app, db
from sqlalchemy import text

app = create_app()

def update_schema():
    with app.app_context():
        # Get the database engine
        engine = db.engine
        
        # Determine if we are using Postgres or SQLite
        dialect_name = engine.dialect.name
        
        try:
            if dialect_name == 'postgresql':
                print("Detected PostgreSQL. Running ALTER TABLE...")
                with engine.connect() as conn:
                    # Increase prediction column length to 50
                    conn.execute(text("ALTER TABLE result ALTER COLUMN prediction TYPE VARCHAR(50);"))
                    conn.commit()
                print("Schema updated successfully for PostgreSQL.")
            elif dialect_name == 'sqlite':
                print("Detected SQLite. Schema updates via ALTER TABLE are limited.")
                print("If this is a local dev DB, you might need to recreate the table if it fails.")
                # SQLite doesn't strictly enforce VARCHAR lengths, so it might not even need an ALTER
            else:
                print(f"Detected dialect: {dialect_name}. No specific migration logic needed.")
        except Exception as e:
            print(f"Notification: Schema update might have already been applied or failed: {e}")

if __name__ == "__main__":
    update_schema()
