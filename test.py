from cs50 import SQL
import os
from dotenv import load_dotenv

load_dotenv()
db = SQL(os.environ.get("DB_URL"))

try:
    print("⏳ Migrating 'appointments' table...")
    
    # Adding the missing 'bill' and 'expiry_date' columns
    db.execute("""
        ALTER TABLE appointments 
        ADD COLUMN IF NOT EXISTS bill REAL DEFAULT 0.0,
        ADD COLUMN IF NOT EXISTS expiry_date TIMESTAMP;
    """)
    
    print("✅ 'appointments' table updated with 'bill' and 'expiry_date' columns! 🚀")
except Exception as e:
    print(f"❌ Migration failed: {e}")