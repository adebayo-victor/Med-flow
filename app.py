import random
import csv
import requests
from datetime import datetime, timedelta, date, time
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, send_file
import pandas as pd
from flask_cors import CORS
from cs50 import SQL
import secrets
import os
from werkzeug.utils import secure_filename
import string
import io
import xlsxwriter
from dotenv import load_dotenv

#loading stuff from dotenv
load_dotenv()
#get stuff from .env
POSTMAIL_URL = "https://postmail.invotes.com/send"
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
#mail function
def send_email(to_email, subject, message_body, reply_to="adebayovictorvicade@gmail.com"):
    payload = {
        "access_token": ACCESS_TOKEN,
        "subject": subject,
        "text": message_body,
        "reply_to": reply_to,
        "recipient": to_email
    }

    try:
        response = requests.post(POSTMAIL_URL, data=payload)
        print("✅ Status Code:", response.status_code)
        print("📨 Response:", response.text)
        return response.status_code == 200
    except Exception as e:
        print("❌ Error:", str(e))
        return False


#adding files
UPLOAD_FOLDER = 'static/images/gallery'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'txt', 'jfif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_file_upload(file_key='file'):
    if file_key not in request.files:
        return {'error': 'No file part in the request'}

    file = request.files[file_key]

    if file.filename == '':
        return {'error': 'No selected file'}

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(save_path)
    
        return {'path': save_path}

    return {'error': 'Invalid file type'}
#functions that are part of otp system
def validate_code(patient_id, input_otp):
    row = db.execute("""
    SELECT * FROM otps WHERE patient_id = ? AND otp = ?
    """, patient_id, input_otp)

    if row:
        otp_data = row[0]
        if datetime.strptime(otp_data["expires_at"], "%Y-%m-%d %H:%M:%S") > datetime.now():
            # OTP is valid – delete it
            db.execute("DELETE FROM otps WHERE id = ?", otp_data["id"])
            return True
        else:
            # Expired – delete it
            db.execute("DELETE FROM otps WHERE id = ?", otp_data["id"])
            return False
    return False

def generate_and_store_otp(patient_id):
    otp = str(random.randint(100000, 999999))
    expires_at = datetime.now() + timedelta(minutes=5)

    db.execute("""
    INSERT INTO otps (patient_id, otp, expires_at)
    VALUES (?, ?, ?)
    """, patient_id, otp, expires_at)

    return otp

def cleanup_expired_otps():
    db.execute("DELETE FROM otps WHERE expires_at < ?", datetime.now())
#/////////////////////////////////////////////////////////////////////////////////////////////////////////
def save_log(id):
    try:
        return db.execute('INSERT INTO  visits(patient_id, ip_address, path, user_agent) VALUES(?,?,?,?)', id, request.remote_addr, request.path, request.headers.get('User-Agent'))
    except Exception as e:
        return e
def view_log():
    try:
        return db.execute('SELECT * FROM visits')
    except Exception as e:
        print(f"⚠️ view_log error caught: {e}")
        return []  # Safe fallback so len() handles it perfectly
def view_a_log(id):
    try:
        return db.execute('SELECT * FROM visits WHERE id = ?', id)
    except Exception as e:
        return e

def get_expiry_info():
    with open('expiry_limit.csv','r', newline='') as file:
        reader = csv.reader(file)
        first_row = next(reader)  # 👈 grab the first row
    return first_row
def add_visit():
    with open('visits.csv', mode='r', encoding='utf-8', newline='') as file:
        reader = list(csv.reader(file))

    
    with open('visits.csv', mode='w', encoding='utf-8', newline='') as file:
        if reader:
            reader[0].append(str(datetime.now()))

        writer = csv.writer(file)
        writer.writerows(reader)
        print('time_log', reader)

def get_visit():
    with open('visits.csv', mode='r', encoding='utf-8', newline='') as file:
        reader = list(csv.reader(file))

    if reader:
        return reader
    else:
        return []  # Return an empty list if file is empty
def generate_code(length=6):
    characters = string.ascii_uppercase + string.digits
    random_part = ''.join(secrets.choice(characters) for _ in range(length))
    return f"{random_part}"    
def generate_password(length=9):
    characters = string.ascii_uppercase + string.digits
    random_part = ''.join(secrets.choice(characters) for _ in range(length))
    return f"{random_part}"
password = generate_password()
print(password)
# Usage
code = generate_code()
print(code)  # e.g., APPT-X4F7Z2
#checks if today is greater than input date, returns true if it is greater and returns false if it is not



def find_greater_date(expiry_val):
    if not expiry_val:
        return False
    # If already a native datetime/date instance, check directly
    if isinstance(expiry_val, datetime):
        return datetime.now() > expiry_val
    if isinstance(expiry_val, date):
        return date.today() > expiry_val
        
    # String fallback parser
    try:
        parsed_expiry = datetime.strptime(str(expiry_val).split(".")[0], "%Y-%m-%d %H:%M:%S")
        return datetime.now() > parsed_expiry
    except Exception:
        return False

def add_expired_status(expiry_col, status_col, table, status_name='expired'):
    rows = db.execute(f'SELECT * FROM {table}')
    for row in rows:
        expiry_date = row[expiry_col]
        if find_greater_date(expiry_date):
            row_id = row['id']
            db.execute(
                f'UPDATE {table} SET {status_col}=? WHERE id=?',
                status_name, row_id
            )
            print(f"Updated ID {row_id} as expired")
app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("app_secret_key")
db = SQL(os.environ.get("DB_URL"))
@app.route("/", methods=["GET", "POST"])
def index():
    testimonials = db.execute('SELECT * FROM testimonials')
    clinic_info = db.execute('SELECT * FROM clinic_info')[0]
    services = db.execute('SELECT * FROM services')
    add_visit()
    return render_template('dental.html', info=clinic_info, services=services, testimonials=testimonials)

PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_INITIALIZE_URL = 'https://api.paystack.co/transaction/initialize'
# 🔥 Step 1: Post session and initialize Paystack payment
@app.route('/post_session', methods=['POST'])
def post_session():
    try:
        data = request.form # This is correct for ImmutableMultiDict

        # Required form fields
        name = data.get('name')
        print(name)
        email = data.get('email')
        print(email)
        phone_number = data.get('phone')
        symptoms = data.get('symptoms')
        services = data.get('services')
        bill = int(data.get('bill')) * 100  # 💰 Convert to Kobo
        print(data.get("bill"))
        existing_patient = db.execute('SELECT * FROM patients WHERE email = ?', email)
        if not existing_patient:
            return {"error": "Patient not in database"}

        metadata = {
            "name": name,
            "email": email,
            "phone_number": phone_number,
            "symptoms": symptoms,
            "services": services,
            "bill": bill
        }

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "email": email,
            "amount": bill,
            "metadata": metadata,
            "callback_url": " http://127.0.0.1:8000/callback"  # 🔁 Paystack will redirect here
        }

        response = requests.post(PAYSTACK_INITIALIZE_URL, json=payload, headers=headers)
        print(response)
        res_data = response.json()
        if res_data.get("status"):
            print(res_data) # This print is already there, you can keep it or remove it
            return redirect(res_data['data']['authorization_url'])

        else:
            
            return {"error": res_data}
    except Exception as e:
        return {"error": str(e)}


# 🔁 Step 2: Payment verification callback
@app.route('/callback')
def callback():
    reference = request.args.get('reference')

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    res = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    response_data = res.json()

    if not response_data.get('status'):
        return {"error": "Payment verification failed"}

    payment_data = response_data['data']
    metadata = payment_data['metadata']

    try:
        # Get expiry limit
        with open('expiry_limit.csv', mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            limit = int(next(reader)[0])

        # Patient check
        print(metadata['email'])
        existing_patient = db.execute('SELECT * FROM patients WHERE email = ?', metadata['email'])
        if not existing_patient:
            return {"error": "Patient not in database"}

        # Expiry, date & time stuff
        expiry_date = (datetime.now() + timedelta(days=limit)).strftime('%Y-%m-%d')
        booked_date = datetime.now().strftime('%Y-%m-%d')
        booked_time = datetime.now().strftime('%H:%M')
        note = f'''
            Services: {metadata['services']}
            Message: {metadata['symptoms']}
            Bill: {int(metadata['bill']) / 100:.2f}
        '''

        db.execute(
            '''INSERT INTO appointments (patient_id, booked_date, booked_time, status, notes, expiry_date, appointment_code, bill) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            existing_patient[0]['id'], booked_date, booked_time, 'valid', note, expiry_date, generate_code(), int(metadata['bill']) / 100
        )

        return render_template('success.html')  # or return a JSON response

    except IndexError as e:
        return {"error": str(e)}

        
@app.route("/update_clinic_info", methods=['POST'])
def update_clinic_info():
    if request.method == "POST":
        try:
            data = request.get_json()
            name = data['name']
            email = data['email']
            phone_number = data['phone_number']
            address = data['address']
            hours = data['hours']
            print(data)
            db.execute("UPDATE clinic_info  SET clinic_name=?, email=?, address=?,phone_number=?,operating_hours=? WHERE id = ?", name, email, address, phone_number, hours, 1)
            clinic_info = db.execute('SELECT * FROM clinic_info')[0]
            clinic_info['response'] = 'clinic info updated successfully'
            return jsonify(clinic_info)
        except Exception as e:
            print(e)
            return {"response":f"Uh oh, somethig happened in the backend  => {e}"}
icon_classes = [
    # Core Medical /   / Clinic
    "fas fa-tooth",
    "fas fa-brush",
    "fas fa-medkit",
    "fas fa-stethoscope",
    "fas fa-pills",
    "fas fa-syringe",
    "fas fa-user-doctor",        # Formerly fa-user-md in FA5
    "fas fa-hospital",
    "fas fa-clinic-medical",
    "fas fa-x-ray",
    "fas fa-heart-pulse",        # Replaces fa-heartbeat in FA6
    "fas fa-brain",
    "fas fa-lungs",
    "fas fa-eye",
    "fas fa-ear",
    "fas fa-flask",
    "fas fa-microscope",
    "fas fa-dna",
    "fas fa-band-aid",
    "fas fa-thermometer-half",
    "fas fa-prescription",
    "fas fa-capsules",
    "fas fa-first-aid",
    "fas fa-allergies",
    "fas fa-virus",
    "fas fa-disease",
    "fas fa-hand-holding-medical",
    "fas fa-house-medical",
    "fas fa-kit-medical",
    "fas fa-hospital-user",
    "fas fa-user-nurse",
    "fas fa-ambulance",
    "fas fa-clipboard-user",
    "fas fa-file-waveform",
    "fas fa-head-side-cough",
    "fas fa-lungs-virus",
    "fas fa-pump-medical",
    "fas fa-sensor-on",
    "fas fa-sensor-off",
    "fas fa-vial-virus",
    "fas fa-bacteria",
    "fas fa-bone",
    "fas fa-crutches",
    "fas fa-wheelchair",
    "fas fa-notes-medical",
    "fas fa-file-medical",
    "fas fa-file-prescription",
    "fas fa-clipboard-medical",   # Potentially available or similar
    "fas fa-person-dots-from-line", # Patient movement/progress
    "fas fa-shield-virus",

    # Health & Wellness (related)
    "fas fa-weight-scale",       # Formerly fa-weight in FA5
    "fas fa-child",
    "fas fa-baby",
    "fas fa-male",
    "fas fa-female",
    "fas fa-bed",
    "fas fa-star-of-life",
    "fas fa-hand-sparkles",      # For hygiene
    "fas fa-hands-wash",         # For hygiene
    "fas fa-soap",               # For hygiene
    "fas fa-face-mask",          # For safety/PPE
    "fas fa-mask-face",          # Alternative for safety/PPE
    "fas fa-person-walking",
    "fas fa-running",
    "fas fa-dumbbell",
    "fas fa-bowl-food",
    "fas fa-utensils",
    "fas fa-apple-whole",
    "fas fa-carrot",
    "fas fa-seedling",
    "fas fa-sun",                # For wellness/day
    "fas fa-moon",               # For wellness/night
    "fas fa-droplet",            # For water/fluids
    "fas fa-poop",               # For bodily functions (if needed)
    "fas fa-toilet",             # For facilities
    "fas fa-bath",               # For facilities
    "fas fa-shower",             # For facilities

    # Admin / UI / Related Concepts
    "fas fa-calendar-check",    # Appointments/scheduling
    "fas fa-clock",             # Time/duration
    "fas fa-map-marker-alt",    # Location
    "fas fa-phone",             # Contact
    "fas fa-envelope",          # Contact
    "fas fa-bell",              # Notifications
    "fas fa-comment-dots",      # Messaging
    "fas fa-question-circle",   # Help/FAQ
    "fas fa-info-circle",       # Information
    "fas fa-lock",              # Security/privacy
    "fas fa-unlock",            # Security/privacy
    "fas fa-cog",               # Settings
    "fas fa-user-plus",         # Add user/patient
    "fas fa-user-minus",        # Remove user/patient
    "fas fa-user-pen",          # Formerly fa-user-edit in FA5
    "fas fa-search",            # Search
    "fas fa-print",             # Print
    "fas fa-download",          # Download
    "fas fa-upload",            # Upload
    "fas fa-sign-in-alt",       # Login
    "fas fa-sign-out-alt",      # Logout
    "fas fa-trash",             # Delete
    "fas fa-pen-to-square",     # Formerly fa-edit in FA5
    "fas fa-plus",              # Add
    "fas fa-minus",             # Remove
    "fas fa-check",             # Confirm/complete
    "fas fa-xmark",             # Formerly fa-times in FA5
    "fas fa-triangle-exclamation", # Formerly fa-exclamation-triangle in FA5
    "fas fa-lightbulb",         # Idea/suggestion
    "fas fa-clipboard-list",    # Lists/tasks
    "fas fa-file-alt",          # Generic document
    "fas fa-folder",            # Folder
    "fas fa-user",              # Single user
    "fas fa-users",             # Multiple users/staff
    "fas fa-building",          # Building/office
    "fas fa-calendar",          # Calendar
    "fas fa-home",              # Dashboard/home
    "fas fa-chart-pie",         # Data visualization
    "fas fa-book",              # Reference/guide
    "fas fa-comments",          # Feedback/discussions
    "fas fa-shield-alt",        # Protection
    "fas fa-map",               # Map
    "fas fa-globe",             # Global/website
    "fas fa-tags",              # Categories
    "fas fa-barcode",           # Barcode/identification
    "fas fa-file-invoice",      # Billing/invoice
    "fas fa-hand-wave",         # Greeting/welcome (if applicable)
]
@app.route('/admin')
def admin():
    clinic_info = db.execute('SELECT * FROM clinic_info')[0]
    print (clinic_info)
    #web visit log
    visits = len(view_log())
    services = db.execute('SELECT * FROM services')
    #services handling
    if not services:
        services = []
    testimonials = db.execute('SELECT * FROM testimonials')
    team_members = db.execute('SELECT * FROM team_members')
    print(team_members)
    appointments = db.execute('SELECT * FROM patients JOIN appointments ON patients.id = appointments.patient_id')
    #total revenue calculation
    revenue = 0
    for appointment in appointments:
        revenue += appointment.get('price') or 0
    patients = db.execute('SELECT * FROM patients')
    blogs = db.execute('SELECT * FROM blog_posts')
    # Pass the correct column name 'appointment_date' instead of 'expiry_date'
    # Change this line inside your admin route block:
    add_expired_status('expiry_date', 'status', 'appointments')
    print('visit logs', get_visit())
    return render_template("admin1.html",clinic_info=clinic_info, services=services, icons=icon_classes, appointments=appointments, testimonials=testimonials, team_members=team_members, appointment_count=len(appointments), patient_count=len(patients), visit=visits, revenue=revenue, expiry_info=get_expiry_info(), blogs=blogs)
@app.route('/delete_service',methods=['POST'])
def delete_service():
    if request.method == 'POST':
        data = request.get_json()
        print('delete request:', data['id'])
        #db.execute('DELETE FROM appointments WHERE service_id=?', data['id'])
        db.execute('DELETE FROM services WHERE id=?', data['id'])
        services = db.execute('SELECT * FROM services')
        services[0]['response'] = 'service deleted successfully'
        return jsonify(services)
@app.route('/add_service',methods=['POST'])
def add_service():
    if request.method == 'POST':
        data = request.get_json()
        print('add request:', data)
        db.execute('INSERT INTO services(name, price, fa_icon_class, description) VALUES(?,?,?,?)', data['name'], data['price'], data['icon_class'], data['description'])
        services = db.execute('SELECT * FROM services')
        print(services)
        services[0]['response'] = 'service added successfully'
        return jsonify(services)
@app.route('/fetch_appointments', methods=['POST'])
def fetch_appointments():
    if request.method == "POST":
         data = request.get_json()
         appointments = db.execute('SELECT * FROM patients  JOIN appointments ON  appointments.patient_id = patients.id  WHERE appointmentS.id=?', data['id'])
         print(appointments)
         appointments[0]['response'] = "appointment fetched"
         return jsonify(appointments)
@app.route('/validate_appointment', methods=['POST'])
def validate_appointments():
    try:
        if request.method  == "POST":
            data = request.get_json()
            print(data)
            validity = db.execute('SELECT * FROM patients  JOIN appointments ON  appointments.patient_id = patients.id  WHERE appointment_code = ? AND email = ?', data['code'],data['email'])[0]
            if validity:
                db.execute("UPDATE appointments SET status=? WHERE appointment_code=?", 'used', data['code'])
                return jsonify({'response':"appointment used"})
            else:
                return jsonify({'response':"Invalid code or email"})
    except IndexError:
        return jsonify({'response':"Invalid code or email"})
    except Exception as e:
        return jsonify({'response':f"{e}"})
@app.route('/set_appointment_expiry', methods=['POST'])
def set_appointment_expiry():
    try:
        data = request.get_json()
        appointment_id = data.get("appointment_id")
        
        days = int(data.get("days", 0))
        hours = int(data.get("hours", 0))
        minutes = int(data.get("minutes", 0))
        seconds = int(data.get("seconds", 0))
        
        # Calculate future timestamp based on dashboard sliders/inputs
        expiry_timestamp = datetime.now() + timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        )
        
        db.execute("""
            UPDATE appointments 
            SET expiry_date = ?, status = 'approved' 
            WHERE id = ?
        """, expiry_timestamp, appointment_id)
        
        return jsonify({
            "response": "successful", 
            "expiry_date": str(expiry_timestamp)
        })
    except Exception as e:
        if hasattr(db, "_disconnect"):
            db._disconnect()
        return jsonify({"response": f"Error: {e}"}), 500
@app.route('/set_expiry', methods=['POST'])
def set_expiry():
    if request.method == 'POST':
        data = request.get_json()
        expiry_list = [[data['days'], data['hours'], data['minutes'], data['seconds']]]
        with open('expiry_limit.csv', 'w') as file:
            csv.writer(file).writerows(expiry_list)
        return jsonify({"response":f"expiry set to days:{data['days']}, hours:{data['hours']}, minutes:{data['minutes']}, seconds:{data['seconds']}"})
@app.route('/post_testimonial', methods=['POST'])
def post_testimonial():
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        email = data['email']
        quote = data['quote']
        author_description = data['author_description']
        existing_patient = db.execute('SELECT * FROM patients WHERE email = ? ', email)[0]
        if existing_patient:
            db.execute('INSERT INTO testimonials(patient_id, quote, author_name, author_description) VALUES(?,?,?,?)', existing_patient['id'], quote, name, author_description)
            return [{'response': "testimonial added to backend"}]
        else:
            return [{'response': "not an existing patient"}]
@app.route('/delete_testimonial', methods=['POST'])
def delete_testimonial():
    if request.method == 'POST':
        try:
            db.execute('DELETE FROM testimonials WHERE id = ?', request.get_json()['id'])
            return [{'response': f"removed"}]
        except Exception as e:
            return [{'response': f"e"}]
@app.route('/delete_member', methods=['POST'])
def delete_member():
    if request.method == 'POST':
        try:
            db.execute('DELETE FROM team_members WHERE id = ?', request.get_json()['id'])
            return [{'response': f"removed member"}]
        except Exception as e:
            return [{'response': f"e"}]
@app.route('/add_member', methods=['POST'])
def add_member():
    try:
        if request.method == 'POST':
            data=request.form
            print(data)
            name = data.get('name')
            position = data.get('position')
            specialization = data.get('specialization')
            bio = data.get('bio')
            email = data.get('email')
            phone = data.get('phone')
            password = generate_password()
            image_url = handle_file_upload(file_key='image_url').get('path')
            image_url = image_url.replace('\\', '/')
            print(image_url)
            db.execute('INSERT INTO team_members(name, position,specialization, bio, image_url, email, phone_number, password) VALUES(?,?,?,?,?,?,?,?)', name, position,specialization,bio,image_url,email,phone,password)
            send_email(
                to_email=email,
                subject="TECHLITE INNOVATIONS",
                message_body=f"Hello there, This is your  password => {password},🔐 try not to forget it"
            )
            print('password:', password)
            reply = db.execute('SELECT  * FROM team_members WHERE name = ? AND specialization = ? AND bio = ?', name, specialization,bio)
            reply[0]['response'] = 'successful'
            return jsonify(reply)
    except Exception as e:
        print(e)
        return jsonify([{'response':f'{e}'}])
@app.route('/update_member', methods=['POST'])
def update_member():
    try:
        if request.method == 'POST':
            data = request.get_json()
            print(data)
            db.execute('UPDATE team_members SET name=?, position=?, specialization=?, bio=?, image_url=?, email=?, phone_number=? WHERE id=?', data['name'], data['position'], data['specialization'], data['bio'], data['image_url'], data['email'], data['phone_number'], data['id'])
            return jsonify(data)
    except Exception as e:
        return {'response': f'{e}'}
@app.route('/update_service', methods=['POST'])
def update_service():
    try:
        if request.method == 'POST':
            data = request.get_json()
            print(data)
            db.execute('UPDATE services SET name=?, price=?, description=? WHERE id = ?', data['name'], data['price'], data['description'], data['id'])
            return jsonify(db.execute('SELECT * FROM services WHERE id = ?', data['id']))
    except Exception as e:
        return {'response': f'{e}'}
@app.route('/search_appointment', methods=['POST'])
def search_service():
    try:
        if request.method == 'POST':
            data = request.get_json()
            stuff = db.execute('SELECT * FROM patients  JOIN appointments ON  appointments.patient_id = patients.id')
            response = []
            for row in stuff:
                if data['input'].lower() in row['full_name'].lower():
                    response.append(row)
            return jsonify(response)
    except Exception as e:
        return {'response': f'{e}'}
@app.route('/login', methods=['POST'])
def login():
    try:
        if request.method == 'POST':
            data = request.get_json()
            email = data['email']
            password = data['password']
            print(data)
            user = db.execute('SELECT * FROM patients WHERE email=? AND password =?', email,password)
            if user:
                user[0]['response'] = 'successful'
                print('is a patient')
                print(user)
                print(save_log(user[0]['id']))
                return jsonify(user)
            else:
                return [{'response':'not a patient'}]
    except Exception as e:
        return [{'response':f'{e}'}]
@app.route('/signup', methods=['POST'])
def signup():
    try:
        if request.method == 'POST':
            data = request.get_json()
            print(data)
            name = data['full_name']
            email = data['email']
            phone = data['phone']
            password = data['password']
            if name and email and phone and password:
                db.execute('INSERT INTO patients(full_name, email, phone, password) VALUES(?,?,?,?)', name,email,phone,password)
                reply = db.execute('SELECT * FROM patients WHERE full_name=? AND email=? AND phone=? AND password=?', name, email, phone, password)
                reply[0]['response'] = 'successful'
                return jsonify(reply)
            else:
                return [{'response':'Fill the form completely'}]
    except Exception as e:
        print(e)
        return [{'response':f'{e}'}]
@app.route('/my_appointments/<int:user_id>')
def my_appointments(user_id):
    new_appointments = []
    valid = 0
    used = 0
    expired = 0
    user= db.execute('SELECT * FROM patients WHERE id =?', user_id)[0]
    appointments = db.execute('SELECT * FROM appointments WHERE patient_id =?', user_id)
    for appointment in appointments:
        if appointment['status'] == 'valid':
            new_appointments.append(appointment)
    #Using LIFO the used and expired go in first
    for appointment in appointments:
        if appointment['status'] == 'expired' or appointment['status'] == 'used':
            new_appointments.append(appointment)
    for appointment in appointments:
        if appointment['status'] == 'used':
            used += 1
    for appointment in appointments:
        if appointment['status'] == 'valid':
            valid += 1
    for appointment in appointments:
        if appointment['status'] == 'expired':
            expired += 1
    return render_template('user.html', user=user, appointments=new_appointments, valid_count=valid, expired_count=expired, used_count=used)
@app.route('/fetch_all_patients')
def fetch_all_patients():
    patients = db.execute('SELECT * FROM patients')
    print(patients)
    return jsonify(patients)
@app.route('/fetch_patient_details/<patient_id>')
def fetch_patient_details(patient_id):
    patient = db.execute('SELECT * FROM patients WHERE id = ?', patient_id)
    print(patient)
    return (patient)
@app.route('/update_patient', methods=['POST'])
def update_patient():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        id = data['id']
        name=data['full_name']
        email = data['email']
        phone_number = data['phone']
        password = data['password']
        db.execute('UPDATE patients SET full_name =?, email = ?, phone = ?, password=? WHERE id = ? ', name, email,phone_number,password, id )
        return [{'response':'Patient updated successfully'}]
from datetime import date, time, datetime

@app.route('/fetch_all_bills')
def fetch_all_bills():
    # This query uses the column names confirmed by your database schema
    query = """
        SELECT 
            appointments.id AS bill_id,
            patients.id AS patient_id,
            appointments.appointment_date,
            appointments.appointment_time,
            appointments.expiry_date,
            appointments.appointment_code,
            appointments.message,
            appointments.bill,
            appointments.status
        FROM appointments 
        JOIN patients ON appointments.patient_id = patients.id
        ORDER BY appointments.id DESC
    """
    try:
        bills = db.execute(query)
    except Exception as e:
        # If any column is missing, the transaction will fail.
        # Closing the connection is mandatory to reset the 'poisoned' transaction block.
        if hasattr(db, "_disconnect"):
            db._disconnect()
        return jsonify({"error": str(e)}), 500
        
    if not bills:
        return jsonify([])
        
    cleaned_bills = []
    for row in bills:
        # Convert row object to dictionary and serialize dates
        bill_dict = dict(row) if hasattr(row, 'keys') else row
        for key, value in bill_dict.items():
            if isinstance(value, (time, date, datetime)):
                bill_dict[key] = str(value)
        cleaned_bills.append(bill_dict)
        
    return jsonify(cleaned_bills)




@app.route('/fetch_all_visits')
def fetch_all_visits():
    # This now runs seamlessly since patient_id exists!
    query = """
        SELECT 
            visits.id, visits.ip_address, visits.user_agent, visits.viewed_at,
            patients.full_name, patients.email, patients.phone
        FROM visits 
        LEFT JOIN patients ON visits.patient_id = patients.id 
        ORDER BY visits.viewed_at DESC
    """
    
    try:
        visits = db.execute(query)
    except Exception as e:
        if hasattr(db, "_disconnect"):
            db._disconnect()
        return jsonify({"error": str(e)}), 500

    if not visits:
        return jsonify([])
        
    cleaned_visits = []
    for row in visits:
        visit_dict = dict(row) if hasattr(row, 'keys') else row
        for key, value in visit_dict.items():
            if isinstance(value, (time, date, datetime)):
                visit_dict[key] = str(value)
        cleaned_visits.append(visit_dict)
        
    return jsonify(cleaned_visits)
@app.route('/fetch_a_visit', methods=['POST'])
def fetch_a_visit():
    if request.method == "POST":
        visit = view_a_log(request.get_json().get['id'])
        print(visit)
        if not visit:
            return []
        return jsonify(visit)
    else:
        return []
@app.route('/admin_login', methods = ['POST'])
def admin_login():
    try:
        if request.method == "POST":
            print(request.get_json())
            valid = db.execute('SELECT * FROM team_members WHERE password = ?', request.get_json()['password'])
            print(valid)
            valid[0]['response'] = 'successful'
            if valid:
                print(valid)
                return jsonify(valid)
            else:
                return [{"response": "not an admin"}]
    except IndexError as e:
        return {'response':f'{e}'}
@app.route('/change_admin_password', methods=["POST"])
def change_admin_password():
    try:
        if request.method == "POST":
            data = request.get_json()
            print(data)
            email = data['email']
            position = data['position']
            member = db.execute('SELECT * FROM team_members WHERE email = ? AND position = ?', email,position)
            if member:
                new_password = generate_password()
                db.execute('UPDATE team_members SET password = ? WHERE email = ?',new_password, email)
                print('new password', new_password)
                send_email(
                    to_email=email,
                    subject="TECHLITE INNOVATIONS",
                    message_body=f"Hello there, This is your new password => {new_password},🔐 try not to forget it"
                )
                return {'response':'successful'}
            else:
                return {'response':'The email is not of a member, if there is an issue,contact the superior admin'}
    except IndexError as e:
        return {'response':f'{e}'}
@app.route("/get_otp", methods=['POST'])
def get_otp():
    try:
        if request.method == "POST":
            #delete expired otps
            print(request.get_json())
            cleanup_expired_otps()
            email = request.get_json()['id']#email key has been replaced with id, soooooo it contains key amd not "id"
            id = db.execute('SELECT * FROM patients WHERE email = ?', email)[0]['id']
            #check if user has valid otp
            existing = db.execute('SELECT * FROM otps WHERE id = ?', id)
            if existing:
                return {'response':"Your requested otp is still valid, check your email"}
            else:
                otp = generate_and_store_otp(id)
                print(otp)
                #email will be sent here
                send_email(
                    to_email=email,
                    subject="TECHLITE INNOVATIONS",
                    message_body=f"OTP => {otp}. Share your otp with no one."
                )
                return {"response":"successful"}
    except Exception as e:
        return {"response":f"{e}"}
@app.route('/validate_otp', methods=["POST"])
def validate_otp():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        email = request.get_json()['id']#email key has been replaced with id, soooooo it contains email not "id"
        id = db.execute('SELECT * FROM patients WHERE email = ?', email)[0]['id']
        print('id', id)
        otp = data['otp']
        valid = validate_code(id, otp)
        if valid:
            return {"response":"successful"}
        else:
            return {"response":"invalid otp"}
@app.route('/change_password', methods=["POST"])
def change_password():
    try:
        data = request.get_json()
        print(data)
        password = data['password']
        email = request.get_json()['id']#email key has been replaced with id, soooooo it contains email not "id"
        id = db.execute('SELECT * FROM patients WHERE email = ?', email)[0]['id']
        db.execute('UPDATE patients SET password = ? WHERE id = ?',password, id)
        
        return {"response":"successful"}
    except Exception as e:
        return {"response":f"{e}"}


@app.route('/download_excel')
def download_excel():
    # Fixed columns to perfectly match your database schema
    query_str = """
        SELECT 
            patients.id AS patient_id,
            patients.full_name,
            patients.email,
            patients.phone,
            patients.gender,
            patients.date_of_birth,
            patients.address,
            appointments.appointment_date,
            appointments.appointment_time,
            appointments.appointment_code,
            appointments.message,
            appointments.status
        FROM patients
        LEFT JOIN appointments ON appointments.patient_id = patients.id
    """
    
    try:
        query = db.execute(query_str)

        if not query:
            return jsonify({"error": "No data found"}), 404

        # Clean raw database row objects (stringify date/time fields) so pandas handles it perfectly
        cleaned_data = []
        for row in query:
            row_dict = dict(row) if hasattr(row, 'keys') else row
            for key, value in row_dict.items():
                if type(value).__name__ in ['date', 'time', 'datetime']:
                    row_dict[key] = str(value)
            cleaned_data.append(row_dict)

        # Convert to DataFrame
        df = pd.DataFrame(cleaned_data)

        # Write to an in-memory buffer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Patient Data Summary')

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name='patient_data_summary.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        # Crucial fallback: automatically break the aborted transaction block loop if it jams up
        if hasattr(db, "_disconnect"):
            db._disconnect()
        return jsonify({"error": str(e)}), 500
@app.route('/blog')
def blog():
    blogs = db.execute('SELECT * FROM blog_posts')
    return render_template('Blog.html', blogs=blogs)
@app.route('/post_blog', methods=["POST"])
def post_blog():
    if request.method == "POST":
        data = request.form
        title = data.get('title')
        image_url = handle_file_upload('image_url').get('path')
        image_url = image_url.replace('\\', '/')
        slug = data.get('slug')
        content = data.get('content')
        db.execute('INSERT INTO blog_posts(title,content, slug, featured_image_url) VALUES(?,?,?,?)', title, content, slug, image_url)
        reply = db.execute("SELECT * FROM blog_posts")
        reply[0]['response'] = 'successful'
        return jsonify(reply)
@app.route('/delete_blog', methods=["POST"])
def delete_blog():
    id = request.get_json()['id']
    db.execute('DELETE FROM blog_posts WHERE id = ?', id)
    return [{'response':"successful"}]
@app.route('/appointment_trend', methods=["POST"])
def appointment_trend():
    if request.method == "POST":
        x_values = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        y_values = [0] * 12  
        appointments = db.execute('SELECT * FROM appointments')
        present_year = datetime.now().year

        for appointment in appointments:
            # Safely fetch the date column whether it's a dict or a tuple index
            try:
                raw_date = appointment['appointment_date']
            except (TypeError, KeyError):
                # Fallback to standard index mapping if it's returning raw tuples
                # Change the index number below if appointment_date is not the 4th column (0-indexed)
                raw_date = appointment[3] 

            # Handle type handling if Postgres returns native datetime objects or strings
            if isinstance(raw_date, (date, datetime)):
                booked_date = raw_date
            else:
                booked_date = datetime.strptime(str(raw_date).split()[0], "%Y-%m-%d")

            if booked_date.year == present_year:
                month_index = booked_date.month - 1
                y_values[month_index] += 1

        appointment_data = {
            'x_values': x_values,
            'y_values': y_values
        }
        print(appointment_data)
        return appointment_data
@app.route("/service_popularity")
def service_popularity():
    # Step 1: Get list of all services from database
    db_services = db.execute('SELECT * FROM services')
    services = [service['name'] for service in db_services]
    count = [0] * len(services)

    # Step 2: Get all appointments
    appointments = db.execute('SELECT * FROM appointments')

    # Step 3: Count appearances of each service name in appointment notes
    for i, service in enumerate(services):
        for appointment in appointments:
            if service.lower() in appointment['message'].lower():
                count[i] += 1

    # Step 4: Package and return data
    service_data = {
        'x_values': services,
        'y_values': count
    }
    return service_data
@app.route('/search_patients', methods=['POST'])
def search_patients():
    try:
        if request.method == 'POST':
            data = request.get_json()
            stuff = db.execute('SELECT * FROM patients')
            response = []
            for row in stuff:
                if data['input'].lower() in row['full_name'].lower():
                    response.append(row)
            return jsonify(response)
    except Exception as e:
        return {'response': f'{e}'}
#updates start from here, first update, AI consultancy
#this function generates the csv,dont mind the variable name in it, it is from FLING
def generate_csv(prompt):
    headers = {"Content-Type": "application/json"}
    params = {"key": os.environ.get('gemini_key')}

    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    print(os.environ.get('GEMINI_URL'))
    try:
        res = requests.post(
            os.environ.get('GEMINI_URL'),
            headers=headers,
            params=params,
            json=data
        )


        if res.status_code != 200:
            print("Gemini error:", res.status_code, res.text)
            return None

        r = res.json()

        candidates = r.get("candidates")
        if not candidates:
            print("No candidates:", r)
            return None

        parts = candidates[0].get("content", {}).get("parts")
        if not parts or "text" not in parts[0]:
            print("Malformed response:", r)
            return None

        return parts[0]["text"]

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return None

        
@app.route("/suggestion", methods=["POST"])
def suggestion():
    if request.method == "POST":
        total = 0
        services_info = {'services':[]}
        data = request.json
        #create suitable prompt with list of services available in database
        ailment = data['prompt']
        services = db.execute("SELECT name,price  FROM services")
        #convert all prices from float to int
        for service in services:
            service['price']=str(service['price']).replace(".0", "")
        prompt = f"Act as an AI Consultant. Analyze my ailment: [{ailment}]. Cross-reference this with our service catalog: [{services}]. Based on your consultation, identify the necessary and suggested services. Output the result strictly as a raw CSV string with no headers, no markdown blocks, and no conversational text. Use this format: service_name,price,is_suggested"
        print(prompt)
        #send prompt to API
        raw_csv = generate_csv(prompt)
        #receive response as raw csv format , convert into workable form
        raw_csv=raw_csv.replace('```', '')
        split_data = raw_csv.split("\n")
        for data in split_data:
            entry = data.split(',')
            services_info['services'].append({'name':entry[0], 'price':entry[1]})
        #calculate total amount
            total+=int(entry[1])
        #return services, prices and total
        return jsonify({'services':services_info,'total':total})

@app.route('/toggle_testimonial_status', methods=['POST'])
def toggle_testimonial_status():
    data = request.get_json()
    testimonial_id = data.get("id")
    
    if not testimonial_id:
        return jsonify({"error": "Missing 'id' in payload"}), 400

    try:
        # Get current status
        row = db.execute("SELECT is_approved FROM testimonials WHERE id = ?", testimonial_id)
        if not row:
            return jsonify({"error": "Testimonial not found"}), 404
        
        current_status = row[0]["is_approved"]
        # Flip: 1 to 0, or 0 to 1
        new_status = 1 if current_status == 0 else 0
        
        # Update
        db.execute("UPDATE testimonials SET is_approved = ? WHERE id = ?", new_status, testimonial_id)
        
        return jsonify({"status": "success", "new_status": new_status})
    except Exception as e:
        if hasattr(db, "_disconnect"):
            db._disconnect()
        return jsonify({"error": str(e)}), 500

if __name__=="__main__":
    app.run(debug=True, port=8000 )