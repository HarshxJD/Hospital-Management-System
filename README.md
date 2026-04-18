# 🏥 Hospital Management System

A web-based **Hospital Management System** built using **Flask (Python)** and **MySQL**, designed to manage hospital operations like patients, doctors, appointments, treatments, and more through a simple dashboard interface.

---

## 🚀 Features

* 📊 Dashboard overview
* 👨‍⚕️ Manage Doctors
* 🏥 Manage Departments
* 📅 Appointments tracking
* 🛏 Admissions & Transfers
* 📜 Medical History records
* 💊 Treatments & Surgeries
* ⚙️ Resource management
* 🔍 Search functionality
* ✏️ Edit & 🗑 Delete operations

---

## 🛠️ Tech Stack

* **Frontend:** HTML, CSS
* **Backend:** Flask (Python)
* **Database:** MySQL
* **Tools:** VS Code, Git

---

## 📁 Project Structure

```
Hospital Management/
│
├── app.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── doctors.html
│   ├── departments.html
│   ├── appointments.html
│   ├── admissions.html
│   ├── transfers.html
│   ├── medicalhistory.html
│   ├── treatments.html
│   ├── surgeries.html
│   └── resources.html
│
└── static/
    └── style.css
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```
git clone https://github.com/your-username/hospital-management-system.git
cd hospital-management-system
```

---

### 2. Install Dependencies

```
pip install flask mysql-connector-python
```

---

### 3. Setup MySQL Database

* Open MySQL
* Run your SQL script (tables + data)

Example:

```
CREATE DATABASE HospitalManagement;
USE HospitalManagement;
```

---

### 4. Update Database Connection

In `app.py`, update:

```
host="localhost"
user="root"
password="your_password"
database="HospitalManagement"
```

---

### 5. Run the Application

```
python app.py
```

---

### 6. Open in Browser

```
http://127.0.0.1:5000/
```

---

## 📸 Screenshots

* Dashboard
* Doctors Page
* Appointments Page
* Resource Management


---

## 🎯 Future Improvements

* Authentication (Login/Register)
* Role-based access (Admin/Doctor)
* Better UI (Bootstrap / React)
* Charts & analytics dashboard
* API integration

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork the repo and submit a pull request.

---

## 📄 License

This project is for educational purposes.

---

## 👨‍💻 Author

**Harsh**
**2401010096**

B.Tech CSE Student

---

⭐ If you like this project, give it a star on GitHub!
