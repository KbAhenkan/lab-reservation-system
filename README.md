# Lab Reservation System - Backend

A Django REST Framework backend for a lab reservation system.

## Tech Stack
- Django 6.0.6
- Django REST Framework
- MySQL
- JWT Authentication

## Setup Instructions

### 1. Clone the repository
git clone <repository-url>
cd lab

### 2. Install dependencies
pip install -r requirements.txt

### 3. Create a .env file in the root directory
SECRET_KEY=your_secret_key
DB_PASSWORD=your_mysql_password
EMAIL_PASSWORD=your_gmail_app_password

### 4. Setup MySQL database
Create a database called labreserve in MySQL

### 5. Run migrations
python manage.py migrate

### 6. Run the server
python manage.py runserver

## API Endpoints
- POST /api/auth/signup/
- POST /api/auth/login/
- POST /api/auth/password-reset/
- POST /api/auth/password-reset/confirm/
- GET/POST /api/labs/
- GET/POST /api/users/
- GET/POST /api/reservations/
- GET /api/dashboard/