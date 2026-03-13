# Backend Setup Instructions

## 1. Install Dependencies
```bash
cd c:\Users\hp\Desktop\CAPSTONE\vequiso_build_hub_backend\title
pip install -r requirements.txt
```

## 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 3. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

## 4. Run Server
```bash
python manage.py runserver
```

Backend will run on: http://localhost:8000

## API Endpoints
- Employees: http://localhost:8000/api/employees/
- Requests: http://localhost:8000/api/requests/
- Leaves: http://localhost:8000/api/leaves/
- Salary Payments: http://localhost:8000/api/salary-payments/
- Admin Panel: http://localhost:8000/admin/

## Frontend Setup
```bash
cd c:\Users\hp\Desktop\CAPSTONE\vequiso-build-hub-main\vequiso-build-hub-main
npm run dev
```

Frontend will run on: http://localhost:5173
