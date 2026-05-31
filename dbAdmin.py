'''import os
from cs50 import SQL
from dotenv import load_dotenv

# Load database URI from your .env file
load_dotenv()
db_url = os.environ.get("DB_URL")

if not db_url:
    print("❌ Error: DB_URL not found in .env file!")
    exit(1)

print("⏳ Connecting to Aiven Cloud Database...")
db = SQL(db_url)

try:
    print("🏗️ Creating production tables...")

    # 1. Clinic Info
    db.execute("""
    CREATE TABLE IF NOT EXISTS clinic_info (
        id SERIAL PRIMARY KEY,
        clinic_name VARCHAR(100) NOT NULL,
        address TEXT NOT NULL,
        phone_number VARCHAR(20) NOT NULL,
        email VARCHAR(100) NOT NULL,
        operating_hours VARCHAR(100),
        tagline VARCHAR(150),
        facebook_url TEXT,
        instagram_url TEXT,
        twitter_url TEXT,
        maps_embed_url TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("✅ Table 'clinic_info' ready.")

    # 2. Services
    db.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        price REAL,
        fa_icon_class VARCHAR(50),
        is_active INT DEFAULT 1,
        display_order INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("✅ Table 'services' ready.")

    # 3. Testimonials
    db.execute("""
    CREATE TABLE IF NOT EXISTS testimonials (
        id SERIAL PRIMARY KEY,
        quote TEXT NOT NULL,
        author_name VARCHAR(100) NOT NULL,
        author_description VARCHAR(150),
        is_approved INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("✅ Table 'testimonials' ready.")

    # 4. Team Members
    db.execute("""
    CREATE TABLE IF NOT EXISTS team_members (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        position VARCHAR(100) NOT NULL,
        specialization VARCHAR(100),
        bio TEXT,
        image_url TEXT,
        is_active INT DEFAULT 1,
        display_order INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("✅ Table 'team_members' ready.")

    # 5. Blog Posts
    db.execute("""
    CREATE TABLE IF NOT EXISTS blog_posts (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        slug VARCHAR(200) UNIQUE NOT NULL,
        content TEXT NOT NULL,
        author_id INT,
        published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        featured_image_url TEXT,
        is_published INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("✅ Table 'blog_posts' ready.")

    # 6. Patients
    db.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(150) NOT NULL,
        email VARCHAR(100),
        phone VARCHAR(20),
        gender VARCHAR(15),
        date_of_birth DATE,
        address TEXT,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("✅ Table 'patients' ready.")

    # 7. Appointments
    db.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id SERIAL PRIMARY KEY,
        patient_id INT NOT NULL,
        appointment_date DATE NOT NULL,
        appointment_time TIME NOT NULL,
        appointment_code VARCHAR(50) UNIQUE NOT NULL,
        message TEXT,
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
    );
    """)
    print("✅ Table 'appointments' ready.")

    # 8. Users
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role VARCHAR(20) DEFAULT 'admin',
        is_active INT DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("✅ Table 'users' ready.")

    print("\n🚀 Database built successfully on Aiven! All tables are active.")

except Exception as e:
    print(f"\n❌ Error building schema: {e}")


import os
import time
from cs50 import SQL
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()
db_url = os.environ.get("DB_URL")

if not db_url:
    print("❌ Error: DB_URL not found in your .env file!")
    exit(1)

db = SQL(db_url)

print("⏳ [1/3] Nuking all existing tables and sequences completely...")
try:
    db.execute("""
        DROP TABLE IF EXISTS 
            appointments, 
            bills, 
            blog_posts, 
            clinic_info, 
            patients, 
            services, 
            team_members, 
            testimonials, 
            visits,
            users
        CASCADE;
    """)
    print("✅ Database wiped completely clean!")
except Exception as e:
    print(f"❌ Wipe failed: {e}")
    exit(1)

print("\n⏳ [2/3] Reconstructing production schemas...")
try:
    # 1. Clinic Info
    db.execute("""
    CREATE TABLE clinic_info (
        id SERIAL PRIMARY KEY,
        clinic_name VARCHAR(100) NOT NULL,
        address TEXT NOT NULL,
        phone_number VARCHAR(20) NOT NULL,
        email VARCHAR(100) NOT NULL,
        operating_hours VARCHAR(100),
        tagline VARCHAR(150),
        facebook_url TEXT,
        instagram_url TEXT,
        twitter_url TEXT,
        maps_embed_url TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Services
    db.execute("""
    CREATE TABLE services (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        price REAL,
        fa_icon_class VARCHAR(50),
        is_active INT DEFAULT 1,
        display_order INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Testimonials
    db.execute("""
    CREATE TABLE testimonials (
        id SERIAL PRIMARY KEY,
        quote TEXT NOT NULL,
        author_name VARCHAR(100) NOT NULL,
        author_description VARCHAR(150),
        is_approved INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Team Members
    db.execute("""
    CREATE TABLE team_members (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        position VARCHAR(100) NOT NULL,
        specialization VARCHAR(100),
        bio TEXT,
        image_url TEXT,
        is_active INT DEFAULT 1,
        display_order INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Blog Posts
    db.execute("""
    CREATE TABLE blog_posts (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        slug VARCHAR(200) UNIQUE NOT NULL,
        content TEXT NOT NULL,
        author_id INT,
        published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        featured_image_url TEXT,
        is_published INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Patients
    db.execute("""
    CREATE TABLE patients (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(150) NOT NULL,
        email VARCHAR(100),
        phone VARCHAR(20),
        gender VARCHAR(15),
        date_of_birth DATE,
        address TEXT,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Appointments
    db.execute("""
    CREATE TABLE appointments (
        id SERIAL PRIMARY KEY,
        patient_id INT NOT NULL,
        appointment_date DATE NOT NULL,
        appointment_time TIME NOT NULL,
        appointment_code VARCHAR(50) UNIQUE NOT NULL,
        message TEXT,
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
    );
    """)

    # 8. Users
    db.execute("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role VARCHAR(20) DEFAULT 'admin',
        is_active INT DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("✅ All tables built successfully on Aiven!")
except Exception as e:
    print(f"❌ Schema creation failed: {e}")
    exit(1)

print("\n⏳ [3/3] Seeding fresh records into tables...")
try:
    # Clinic details
    db.execute("""
        INSERT INTO clinic_info (clinic_name, address, phone_number, email, operating_hours, tagline) VALUES 
        ('Modern Tech Clinic', 'Lagos, Nigeria', '+2348000000000', 'info@moderntech.com', 'Mon - Fri: 8AM - 5PM', 'Your Smile, Our Priority');
    """)

    # Services
    db.execute("""
        INSERT INTO services (name, description, price, fa_icon_class, display_order) VALUES 
        ('General Dental Checkup', 'Comprehensive oral examination and professional scaling/cleaning.', 15000.00, 'fa-tooth', 1),
        ('Laser Teeth Whitening', 'Advanced laser treatment to brighten your smile instantly.', 45000.00, 'fa-lightbulb', 2);
    """)

    # Testimonials
    db.execute("""
        INSERT INTO testimonials (quote, author_name, author_description, is_approved) VALUES 
        ('Incredible technological integration. The appointment pipeline was flawless!', 'Alice Johnson', 'Verified Patient', 1);
    """)

    # Team Members
    db.execute("""
        INSERT INTO team_members (name, position, specialization, bio, display_order) VALUES 
        ('Admin Principal', 'Chief Medical Director', 'Health Informatics', 'System Administration Account.', 1),
        ('Dr. Christianah Ade', 'Lead Dental Surgeon', 'Cosmetic Dentistry', 'Expert in maxillofacial restorative care.', 2);
    """)

    # Patients
    db.execute("""
        INSERT INTO patients (full_name, email, phone, gender, date_of_birth, address) VALUES 
        ('Victor Adebayo', 'victor@example.com', '+2348011223344', 'Male', '2007-01-01', 'Ibadan, Nigeria');
    """)

    # Appointments
    db.execute("""
        INSERT INTO appointments (patient_id, appointment_date, appointment_time, appointment_code, message, status) VALUES 
        (1, '2026-06-01', '10:00:00', 'APT-2026-VIC01', 'Routine checkup request.', 'approved');
    """)

    # Admin User
    admin_hash = generate_password_hash("YW5ORG67B")
    db.execute("""
        INSERT INTO users (username, email, password_hash, role, is_active) VALUES 
        ('admin', 'admin@moderntech.com', ?, 'admin', 1);
    """, admin_hash)

    print("✅ All production data successfully seeded!")
    print("\n🏁 Rebuild complete! Your environment is completely fresh. 🚀🎮🦾")

except Exception as e:
    print(f"❌ Seeding failed: {e}") '''


from cs50 import SQL
import os
from dotenv import load_dotenv

load_dotenv()
db = SQL(os.environ.get("DB_URL"))

db.execute("""
CREATE TABLE IF NOT EXISTS visits (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45),
    user_agent TEXT,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
print("✅ 'visits' table deployed successfully!")


from cs50 import SQL
import os
from dotenv import load_dotenv

load_dotenv()
db = SQL(os.environ.get("DB_URL"))

try:
    print("⏳ Migrating 'visits' table...")
    # Add patient_id column linking it directly to your patients table
    db.execute("""
        ALTER TABLE visits 
        ADD COLUMN IF NOT EXISTS patient_id INT REFERENCES patients(id) ON DELETE CASCADE;
    """)
    print("✅ 'visits' table successfully linked to patients! 🚀")
except Exception as e:
    print(f"❌ Migration failed: {e}")


from cs50 import SQL
import os
from dotenv import load_dotenv

load_dotenv()
db = SQL(os.environ.get("DB_URL"))

try:
    print("⏳ Adding expiry columns to 'appointments'...")
    # Adds the expiry column to track when the appointment validation runs out
    db.execute("""
        ALTER TABLE appointments 
        ADD COLUMN IF NOT EXISTS expiry_date TIMESTAMP;
    """)
    print("✅ Schema updated successfully!")
except Exception as e:
    print(f"❌ Migration failed: {e}")



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