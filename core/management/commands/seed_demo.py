from django.core.management.base import BaseCommand

from accounts.models import User
from customers.models import Customer
from tickets.models import Ticket


class Command(BaseCommand):
    help = "Create demo users, customers and tickets (LOCAL USE ONLY: known passwords)."

    def handle(self, *args, **opts):
        admin, _ = User.objects.get_or_create(username="admin", defaults={"role": "admin", "is_staff": True, "is_superuser": True, "email": "admin@example.com"})
        admin.set_password("admin12345"); admin.save()
        emps = []
        for name in ("ravi", "meena"):
            u, _ = User.objects.get_or_create(username=name, defaults={"role": "employee", "email": f"{name}@example.com"})
            u.set_password("employee123"); u.save(); emps.append(u)
        cust_user, _ = User.objects.get_or_create(username="customer1", defaults={"role": "customer", "email": "customer1@example.com"})
        cust_user.set_password("customer123"); cust_user.save()
        c1, _ = Customer.objects.get_or_create(email="customer1@example.com", defaults={"user": cust_user, "name": "Customer One", "phone": "9000000001"})
        c2, _ = Customer.objects.get_or_create(email="acme@example.com", defaults={"name": "Acme Traders", "company": "Acme", "phone": "9000000002"})
        if not Ticket.objects.exists():
            S = Ticket.Status
            Ticket.objects.create(customer=c1, title="Printer not working", description="Paper jam error.", assigned_to=emps[0], status=S.OPEN)
            Ticket.objects.create(customer=c1, title="Install accounting software", description="Needs setup on 2 PCs.", assigned_to=emps[1], status=S.IN_PROGRESS)
            Ticket.objects.create(customer=c2, title="Network down", description="Office WiFi unreachable.", assigned_to=emps[0], status=S.COMPLETED, priority=Ticket.Priority.HIGH)
            Ticket.objects.create(customer=c2, title="New user account", description="Create mail account.")
        self.stdout.write(self.style.SUCCESS("Seeded. admin/admin12345, ravi/employee123, customer1/customer123"))
