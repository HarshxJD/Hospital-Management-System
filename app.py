import os
print("RUNNING FROM:", os.getcwd())

from flask import Flask, render_template, request, redirect, session
import functools

import mysql.connector

app = Flask(__name__)

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345HARSH",
    database="HospitalManagement"
)

cursor = db.cursor()

app.secret_key = 'super_secret_hospital_key'

@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            session['role'] = user[0]
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/analytics')
def analytics():
    # Top 3 Departments
    cursor.execute('''SELECT d.department_name, COUNT(a.admission_id) as count 
                      FROM Admission a JOIN Department d ON a.department_id = d.department_id 
                      GROUP BY d.department_id ORDER BY count DESC LIMIT 3''')
    top_depts = cursor.fetchall()
    
    # Top 3 Doctors (Surgeries)
    cursor.execute('''SELECT d.doctor_name, COUNT(s.surgery_id) as count 
                      FROM Surgery s JOIN Doctor d ON s.doctor_id = d.doctor_id 
                      GROUP BY d.doctor_id ORDER BY count DESC LIMIT 3''')
    top_docs = cursor.fetchall()

    # Most Common Diseases
    cursor.execute('''SELECT disease, COUNT(history_id) as count 
                      FROM MedicalHistory GROUP BY disease ORDER BY count DESC LIMIT 3''')
    top_diseases = cursor.fetchall()
    
    return render_template("analytics.html", top_depts=top_depts, top_docs=top_docs, top_diseases=top_diseases)




# ---------------- PATIENTS ----------------

@app.route('/')
def index():

    cursor.execute("SELECT COUNT(*) FROM patient")
    total_patients = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Doctor")
    total_doctors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Appointment")
    total_appointments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Admission")
    total_admissions = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM patient")
    patients = cursor.fetchall()

    return render_template(
        "index.html",
        patients=patients,
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        total_admissions=total_admissions
    )

@app.route('/add_patient', methods=['POST'])
def add_patient():

    patient_id = request.form['patient_id']
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    phone = request.form['phone']
    address = request.form['address']

    query = """
    INSERT INTO patient
    VALUES (%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query,(patient_id,name,age,gender,phone,address))
    db.commit()

    return redirect('/')


# ---------------- DOCTORS ----------------

@app.route('/doctors')
def doctors():
    search = request.args.get('search')
    if search:
        query = "SELECT * FROM Doctor WHERE doctor_name LIKE %s"
        cursor.execute(query, ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM Doctor")
    
    doctors = cursor.fetchall()
    return render_template("doctors.html", doctors=doctors)

# ---------------- DEPARTMENTS ----------------

@app.route('/departments')
def departments():

    cursor.execute("SELECT * FROM Department")
    departments = cursor.fetchall()

    return render_template("departments.html", departments=departments)


# ---------------- APPOINTMENTS ----------------

@app.route('/appointments')
def appointments():

    cursor.execute("""
    SELECT a.appointment_id, p.name,d.doctor_name,a.appointment_date,a.status
    FROM Appointment a
    JOIN patient p ON a.patient_id=p.patient_id
    JOIN Doctor d ON a.doctor_id=d.doctor_id
    """)

    appointments = cursor.fetchall()

    return render_template("appointments.html", appointments=appointments)


# ---------------- ADMISSIONS ----------------

@app.route('/admissions')
def admissions():

    cursor.execute("""
    SELECT a.admission_id, p.name,d.department_name,a.admission_date,a.discharge_date
    FROM Admission a
    JOIN patient p ON a.patient_id=p.patient_id
    JOIN Department d ON a.department_id=d.department_id
    """)

    admissions = cursor.fetchall()

    return render_template("admissions.html", admissions=admissions)


# ---------------- TRANSFERS ----------------

@app.route('/transfers')
def transfers():

    cursor.execute("""
    SELECT t.transfer_id, p.name,t.from_department,t.to_department,t.transfer_date
    FROM Transfer t
    JOIN patient p ON t.patient_id=p.patient_id
    """)

    transfers = cursor.fetchall()

    return render_template("transfers.html", transfers=transfers)


# ---------------- MEDICAL HISTORY ----------------

@app.route('/medicalhistory')
def medicalhistory():

    cursor.execute("""
    SELECT m.history_id, p.name,m.disease,m.diagnosis_date,m.notes
    FROM MedicalHistory m
    JOIN patient p ON m.patient_id=p.patient_id
    """)

    history = cursor.fetchall()

    return render_template("medicalhistory.html", history=history)


# ---------------- TREATMENTS ----------------

@app.route('/treatments')
def treatments():

    cursor.execute("""
    SELECT t.treatment_id, p.name,d.doctor_name,t.treatment_description,t.treatment_date
    FROM Treatment t
    JOIN patient p ON t.patient_id=p.patient_id
    JOIN Doctor d ON t.doctor_id=d.doctor_id
    """)

    treatments = cursor.fetchall()

    return render_template("treatments.html", treatments=treatments)


# ---------------- SURGERIES ----------------

@app.route('/surgeries')
def surgeries():

    cursor.execute("""
    SELECT s.surgery_id, p.name,d.doctor_name,s.surgery_type,s.surgery_date
    FROM Surgery s
    JOIN patient p ON s.patient_id=p.patient_id
    JOIN Doctor d ON s.doctor_id=d.doctor_id
    """)

    surgeries = cursor.fetchall()

    return render_template("surgeries.html", surgeries=surgeries)


# ---------------- RESOURCES ----------------

@app.route('/resources')
def resources():

    cursor.execute("SELECT * FROM Resource")
    resources = cursor.fetchall()

    return render_template("resources.html", resources=resources)

# Run Server

# ==========================================
# CRUD ROUTES (EDIT / DELETE)
# ==========================================

# --- PATIENT ---
@app.route('/delete_patient/<id>')
def delete_patient(id):
    cursor.execute("DELETE FROM patient WHERE patient_id=%s", (id,))
    db.commit()
    return redirect('/')

@app.route('/edit_patient/<id>', methods=['GET', 'POST'])
def edit_patient(id):
    if request.method == 'POST':
        cursor.execute("UPDATE patient SET name=%s, age=%s, gender=%s, phone=%s, address=%s WHERE patient_id=%s", 
                       (request.form['name'], request.form['age'], request.form['gender'], request.form['phone'], request.form['address'], id))
        db.commit()
        return redirect('/')
    cursor.execute("SELECT * FROM patient WHERE patient_id=%s", (id,))
    r = cursor.fetchone()
    fields = [
        {"label": "ID", "type": "number", "name": "patient_id", "value": r[0], "readonly": True},
        {"label": "Name", "type": "text", "name": "name", "value": r[1]},
        {"label": "Age", "type": "number", "name": "age", "value": r[2]},
        {"label": "Gender", "type": "text", "name": "gender", "value": r[3]},
        {"label": "Phone", "type": "text", "name": "phone", "value": r[4]},
        {"label": "Address", "type": "text", "name": "address", "value": r[5]}
    ]
    return render_template("edit_form.html", title="Patient", post_url=f"/edit_patient/{id}", fields=fields)

# --- DOCTOR ---
@app.route('/delete_doctor/<id>')
def delete_doctor(id):
    cursor.execute("DELETE FROM Doctor WHERE doctor_id=%s", (id,))
    db.commit()
    return redirect('/doctors')

@app.route('/edit_doctor/<id>', methods=['GET', 'POST'])
def edit_doctor(id):
    if request.method == 'POST':
        cursor.execute("UPDATE Doctor SET doctor_name=%s, specialization=%s, department_id=%s WHERE doctor_id=%s", 
                       (request.form['name'], request.form['spec'], request.form['dept'], id))
        db.commit()
        return redirect('/doctors')
    cursor.execute("SELECT * FROM Doctor WHERE doctor_id=%s", (id,))
    r = cursor.fetchone()
    fields = [
        {"label": "ID", "type": "number", "name": "doctor_id", "value": r[0], "readonly": True},
        {"label": "Name", "type": "text", "name": "name", "value": r[1]},
        {"label": "Specialization", "type": "text", "name": "spec", "value": r[2]},
        {"label": "Department ID", "type": "number", "name": "dept", "value": r[3]}
    ]
    return render_template("edit_form.html", title="Doctor", post_url=f"/edit_doctor/{id}", fields=fields)

# --- DEPARTMENT ---
@app.route('/delete_department/<id>')
def delete_department(id):
    cursor.execute("DELETE FROM Department WHERE department_id=%s", (id,))
    db.commit()
    return redirect('/departments')

@app.route('/edit_department/<id>', methods=['GET', 'POST'])
def edit_department(id):
    if request.method == 'POST':
        cursor.execute("UPDATE Department SET department_name=%s WHERE department_id=%s", 
                       (request.form['name'], id))
        db.commit()
        return redirect('/departments')
    cursor.execute("SELECT * FROM Department WHERE department_id=%s", (id,))
    r = cursor.fetchone()
    fields = [
        {"label": "ID", "type": "number", "name": "department_id", "value": r[0], "readonly": True},
        {"label": "Name", "type": "text", "name": "name", "value": r[1]}
    ]
    return render_template("edit_form.html", title="Department", post_url=f"/edit_department/{id}", fields=fields)

# --- APPOINTMENT ---
@app.route('/delete_appointment/<id>')
def delete_appointment(id):
    cursor.execute("DELETE FROM Appointment WHERE appointment_id=%s", (id,))
    db.commit()
    return redirect('/appointments')

@app.route('/edit_appointment/<id>', methods=['GET', 'POST'])
def edit_appointment(id):
    if request.method == 'POST':
        cursor.execute("UPDATE Appointment SET appointment_date=%s, status=%s WHERE appointment_id=%s", 
                       (request.form['date'], request.form['status'], id))
        db.commit()
        return redirect('/appointments')
    cursor.execute("SELECT * FROM Appointment WHERE appointment_id=%s", (id,))
    r = cursor.fetchone()
    fields = [
        {"label": "ID", "type": "number", "name": "appointment_id", "value": r[0], "readonly": True},
        {"label": "Patient ID", "type": "number", "name": "patient_id", "value": r[1], "readonly": True},
        {"label": "Doctor ID", "type": "number", "name": "doctor_id", "value": r[2], "readonly": True},
        {"label": "Date", "type": "date", "name": "date", "value": r[3]},
        {"label": "Status", "type": "text", "name": "status", "value": r[4]}
    ]
    return render_template("edit_form.html", title="Appointment", post_url=f"/edit_appointment/{id}", fields=fields)

# --- ADMISSION ---
@app.route('/delete_admission/<id>')
def delete_admission(id):
    cursor.execute("DELETE FROM Admission WHERE admission_id=%s", (id,))
    db.commit()
    return redirect('/admissions')

@app.route('/edit_admission/<id>', methods=['GET', 'POST'])
def edit_admission(id):
    if request.method == 'POST':
        cursor.execute("UPDATE Admission SET admission_date=%s, discharge_date=%s WHERE admission_id=%s", 
                       (request.form['admission_date'], request.form['discharge_date'] or None, id))
        db.commit()
        return redirect('/admissions')
    cursor.execute("SELECT * FROM Admission WHERE admission_id=%s", (id,))
    r = cursor.fetchone()
    fields = [
        {"label": "ID", "type": "number", "name": "admission_id", "value": r[0], "readonly": True},
        {"label": "Patient ID", "type": "number", "name": "patient_id", "value": r[1], "readonly": True},
        {"label": "Department ID", "type": "number", "name": "department_id", "value": r[2], "readonly": True},
        {"label": "Admission Date", "type": "date", "name": "admission_date", "value": r[3]},
        {"label": "Discharge Date", "type": "date", "name": "discharge_date", "value": r[4]}
    ]
    return render_template("edit_form.html", title="Admission", post_url=f"/edit_admission/{id}", fields=fields)

# --- TRANSFER ---
@app.route('/delete_transfer/<id>')
def delete_transfer(id):
    cursor.execute("DELETE FROM Transfer WHERE transfer_id=%s", (id,))
    db.commit()
    return redirect('/transfers')

@app.route('/edit_transfer/<id>', methods=['GET', 'POST'])
def edit_transfer(id):
    if request.method == 'POST':
        cursor.execute("UPDATE Transfer SET transfer_date=%s WHERE transfer_id=%s", 
                       (request.form['date'], id))
        db.commit()
        return redirect('/transfers')
    cursor.execute("SELECT * FROM Transfer WHERE transfer_id=%s", (id,))
    r = cursor.fetchone()
    fields = [
        {"label": "ID", "type": "number", "name": "transfer_id", "value": r[0], "readonly": True},
        {"label": "Patient ID", "type": "number", "name": "patient_id", "value": r[1], "readonly": True},
        {"label": "From Dept", "type": "number", "name": "from", "value": r[2], "readonly": True},
        {"label": "To Dept", "type": "number", "name": "to", "value": r[3], "readonly": True},
        {"label": "Date", "type": "date", "name": "date", "value": r[4]}
    ]
    return render_template("edit_form.html", title="Transfer", post_url=f"/edit_transfer/{id}", fields=fields)

# --- MEDICAL HISTORY ---
@app.route('/delete_medicalhistory/<id>')
def delete_medicalhistory(id):
    cursor.execute("DELETE FROM MedicalHistory WHERE history_id=%s", (id,))
    db.commit()
    return redirect('/medicalhistory')

@app.route('/edit_medicalhistory/<id>', methods=['GET', 'POST'])
def edit_medicalhistory(id):
    if request.method == 'POST':
        cursor.execute("UPDATE MedicalHistory SET disease=%s, diagnosis_date=%s, notes=%s WHERE history_id=%s", 
                       (request.form['disease'], request.form['date'], request.form['notes'], id))
        db.commit()
        return redirect('/medicalhistory')
    cursor.execute("SELECT * FROM MedicalHistory WHERE history_id=%s", (id,))
    r = cursor.fetchone()
    fields = [
        {"label": "ID", "type": "number", "name": "history_id", "value": r[0], "readonly": True},
        {"label": "Patient ID", "type": "number", "name": "patient_id", "value": r[1], "readonly": True},
        {"label": "Disease", "type": "text", "name": "disease", "value": r[2]},
        {"label": "Diagnosis Date", "type": "date", "name": "date", "value": r[3]},
        {"label": "Notes", "type": "text", "name": "notes", "value": r[4]}
    ]
    return render_template("edit_form.html", title="Medical History", post_url=f"/edit_medicalhistory/{id}", fields=fields)

# --- TREATMENT ---
@app.route('/delete_treatment/<id>')
def delete_treatment(id):
    cursor.execute("DELETE FROM Treatment WHERE treatment_id=%s", (id,))
    db.commit()
    return redirect('/treatments')

@app.route('/edit_treatment/<id>', methods=['GET', 'POST'])
def edit_treatment(id):
    if request.method == 'POST':
        cursor.execute("UPDATE Treatment SET treatment_description=%s, treatment_date=%s WHERE treatment_id=%s", 
                       (request.form['desc'], request.form['date'], id))
        db.commit()
        return redirect('/treatments')
    cursor.execute("SELECT * FROM Treatment WHERE treatment_id=%s", (id,))
    r = cursor.fetchone()
    fields = [
        {"label": "ID", "type": "number", "name": "treatment_id", "value": r[0], "readonly": True},
        {"label": "Patient ID", "type": "number", "name": "patient_id", "value": r[1], "readonly": True},
        {"label": "Doctor ID", "type": "number", "name": "doctor_id", "value": r[2], "readonly": True},
        {"label": "Description", "type": "text", "name": "desc", "value": r[3]},
        {"label": "Date", "type": "date", "name": "date", "value": r[4]}
    ]
    return render_template("edit_form.html", title="Treatment", post_url=f"/edit_treatment/{id}", fields=fields)

# --- SURGERY ---
@app.route('/delete_surgery/<id>')
def delete_surgery(id):
    cursor.execute("DELETE FROM Surgery WHERE surgery_id=%s", (id,))
    db.commit()
    return redirect('/surgeries')

@app.route('/edit_surgery/<id>', methods=['GET', 'POST'])
def edit_surgery(id):
    if request.method == 'POST':
        cursor.execute("UPDATE Surgery SET surgery_type=%s, surgery_date=%s, operation_room=%s WHERE surgery_id=%s", 
                       (request.form['type'], request.form['date'], request.form['room'], id))
        db.commit()
        return redirect('/surgeries')
    cursor.execute("SELECT * FROM Surgery WHERE surgery_id=%s", (id,))
    r = cursor.fetchone()
    fields = [
        {"label": "ID", "type": "number", "name": "surgery_id", "value": r[0], "readonly": True},
        {"label": "Patient ID", "type": "number", "name": "patient_id", "value": r[1], "readonly": True},
        {"label": "Doctor ID", "type": "number", "name": "doctor_id", "value": r[2], "readonly": True},
        {"label": "Type", "type": "text", "name": "type", "value": r[3]},
        {"label": "Date", "type": "date", "name": "date", "value": r[4]},
        {"label": "Room", "type": "number", "name": "room", "value": r[5]}
    ]
    return render_template("edit_form.html", title="Surgery", post_url=f"/edit_surgery/{id}", fields=fields)

# --- RESOURCE ---
@app.route('/delete_resource/<id>')
def delete_resource(id):
    cursor.execute("DELETE FROM Resource WHERE resource_id=%s", (id,))
    db.commit()
    return redirect('/resources')

@app.route('/edit_resource/<id>', methods=['GET', 'POST'])
def edit_resource(id):
    if request.method == 'POST':
        cursor.execute("UPDATE Resource SET resource_name=%s, status=%s WHERE resource_id=%s", 
                       (request.form['name'], request.form['status'], id))
        db.commit()
        return redirect('/resources')
    cursor.execute("SELECT * FROM Resource WHERE resource_id=%s", (id,))
    r = cursor.fetchone()
    fields = [
        {"label": "ID", "type": "number", "name": "resource_id", "value": r[0], "readonly": True},
        {"label": "Name", "type": "text", "name": "name", "value": r[1]},
        {"label": "Status", "type": "text", "name": "status", "value": r[2]}
    ]
    return render_template("edit_form.html", title="Resource", post_url=f"/edit_resource/{id}", fields=fields)


app.run(debug=True)