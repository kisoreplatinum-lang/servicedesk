# ServiceDesk – Service Management System

Django 5 + DRF + PostgreSQL. Roles: Admin, Employee, Customer.

## Run locally (Windows PowerShell)
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py seed_de mo        # optional demo data (local only)
    python manage.py runserver
Open http://127.0.0.1:8000  (seed logins: admin/admin12345, ravi/employee123, customer1/customer123)

PostgreSQL locally: set `DATABASE_URL=postgres://user:pass@localhost:5432/servicedesk` before migrate.
Tests: `python manage.py test`

## Roles
- Admin: everything; creates employees in /admin/ (set Role = Employee); assigns tickets; deletes.
- Employee: customers (view/add/edit); sees tickets assigned to them; updates status only.
- Customer: self sign-up at /accounts/signup/; creates and views own tickets.

## API (login via session or Basic auth)
GET/POST /api/customers/ , /api/customers/<id>/  (Admin/Employee; delete = Admin)
GET/POST /api/tickets/ , /api/tickets/<id>/      (scoped by role; ?status=open&search=...)

## Deploy on Render
1. Push to GitHub.  2. Render > New > Blueprint > pick repo (uses render.yaml).
3. Set DJANGO_SUPERUSER_PASSWORD when prompted.  4. Open the URL, log in as `admin`.
Free Render Postgres expires after 30 days - use a paid/external DB for a long-lived demo.
