from cs50 import SQL
import os
from dotenv import load_dotenv

#loading stuff from dotenv
load_dotenv()
# Connect to your database
# Ensure your DATABASE_URL is set in your Render environment variables
db = SQL(os.environ.get("DB_URL"))

def add_password_column():
    try:
        # Adding the column to store hashes
        db.execute("ALTER TABLE team_members ADD COLUMN password TEXT;")
        print("Successfully added password_hash column! ✅")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_password_column()