import os
from dotenv import load_dotenv
from cs50 import SQL

load_dotenv()
db = SQL(os.getenv("DB_URL"))

def fix_schema():
    # List of required columns and their types
    required_columns = {
        "patient_id": "INTEGER",
        "booked_date": "DATE",
        "booked_time": "TIME",
        "status": "TEXT",
        "notes": "TEXT",
        "expiry_date": "DATE",
        "appointment_code": "TEXT",
        "bill": "REAL"
    }

    # Fetch existing columns
    existing = db.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'appointments'")
    existing_names = [col['column_name'] for col in existing]

    # Add missing ones
    for col, dtype in required_columns.items():
        if col not in existing_names:
            print(f"Adding column: {col}...")
            db.execute(f"ALTER TABLE appointments ADD COLUMN {col} {dtype}")
        else:
            print(f"Column {col} already exists.")

if __name__ == "__main__":
    fix_schema()