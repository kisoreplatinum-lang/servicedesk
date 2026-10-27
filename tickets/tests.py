from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from customers.models import Customer
from .models import Ticket

PW = "Pw-12345-xyz"


class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        R = User.Role
        cls.admin = User.objects.create_user("admin1", password=PW, role=R.ADMIN)
        cls.emp = User.objects.create_user("emp1", password=PW, role=R.EMPLOYEE)
        cls.emp2 = User.objects.create_user("emp2", password=PW, role=R.EMPLOYEE)
        cls.cu1 = User.objects.create_user("cust1", password=PW, role=R.CUSTOMER)
        cls.cu2 = User.objects.create_user("cust2", password=PW, role=R.CUSTOMER)
        cls.c1 = Customer.objects.create(user=cls.cu1, name="Cust One", email="c1@x.com")
        cls.c2 = Customer.objects.create(user=cls.cu2, name="Cust Two", email="c2@x.com")
        cls.t1 = Ticket.objects.create(customer=cls.c1, title="Ticket-A", description="d", assigned_to=cls.emp)
        cls.t2 = Ticket.objects.create(customer=cls.c2, title="Ticket-B", description="d", assigned_to=cls.emp2)

    def login(self, user):
        self.client.login(username=user.username, password=PW)


class WebTests(Base):
    def test_dashboard_for_all_roles(self):
        for u in (self.admin, self.emp, self.cu1):
            self.login(u)
            self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)

    def test_anonymous_redirected(self):
        self.assertEqual(self.client.get(reverse("ticket-list")).status_code, 302)

    def test_customer_sees_only_own_tickets(self):
        self.login(self.cu1)
        r = self.client.get(reverse("ticket-list"))
        self.assertContains(r, "Ticket-A")
        self.assertNotContains(r, "Ticket-B")
        self.assertEqual(self.client.get(reverse("ticket-detail", args=[self.t2.pk])).status_code, 404)

    def test_customer_cannot_open_customers(self):
        self.login(self.cu1)
        self.assertEqual(self.client.get(reverse("customer-list")).status_code, 403)

    def test_employee_sees_only_assigned(self):
        self.login(self.emp)
        r = self.client.get(reverse("ticket-list"))
        self.assertContains(r, "Ticket-A")
        self.assertNotContains(r, "Ticket-B")

    def test_employee_cannot_delete_but_admin_can(self):
        self.login(self.emp)
        self.assertEqual(self.client.post(reverse("ticket-delete", args=[self.t1.pk])).status_code, 403)
        self.client.logout(); self.login(self.admin)
        self.client.post(reverse("ticket-delete", args=[self.t1.pk]))
        self.assertFalse(Ticket.objects.filter(pk=self.t1.pk).exists())

    def test_employee_updates_status_only(self):
        self.login(self.emp)
        r = self.client.get(reverse("ticket-update", args=[self.t1.pk]))
        self.assertEqual(list(r.context["form"].fields), ["status"])
        self.client.post(reverse("ticket-update", args=[self.t1.pk]), {"status": "completed"})
        self.t1.refresh_from_db()
        self.assertEqual(self.t1.status, "completed")
        self.assertIsNotNone(self.t1.completed_at)

    def test_customer_creates_ticket_for_self(self):
        self.login(self.cu1)
        self.client.post(reverse("ticket-create"), {"title": "New", "description": "x", "priority": "high"})
        t = Ticket.objects.get(title="New")
        self.assertEqual(t.customer, self.c1)

    def test_customer_search(self):
        self.login(self.admin)
        r = self.client.get(reverse("customer-list"), {"q": "Two"})
        self.assertContains(r, "Cust Two")
        self.assertNotContains(r, "Cust One")

    def test_signup_creates_customer_profile(self):
        r = self.client.post(reverse("signup"), {
            "username": "newbie", "first_name": "New", "last_name": "Bie", "email": "n@x.com",
            "phone": "123", "password1": PW, "password2": PW})
        self.assertEqual(r.status_code, 302)
        u = User.objects.get(username="newbie")
        self.assertEqual(u.role, "customer")
        self.assertEqual(u.customer_profile.email, "n@x.com")


class ApiTests(Base):
    def test_unauthenticated(self):
        self.assertIn(APIClient().get("/api/tickets/").status_code, (401, 403))

    def test_customer_scope_and_customers_forbidden(self):
        c = APIClient(); c.force_authenticate(self.cu1)
        self.assertEqual(c.get("/api/tickets/").json()["count"], 1)
        self.assertEqual(c.get("/api/customers/").status_code, 403)

    def test_admin_lists_and_creates(self):
        c = APIClient(); c.force_authenticate(self.admin)
        self.assertEqual(c.get("/api/tickets/").json()["count"], 2)
        r = c.post("/api/customers/", {"name": "API Cust", "email": "a@x.com"}, format="json")
        self.assertEqual(r.status_code, 201)

    def test_customer_creates_ticket_via_api(self):
        c = APIClient(); c.force_authenticate(self.cu1)
        r = c.post("/api/tickets/", {"title": "Via API", "description": "x"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Ticket.objects.get(title="Via API").customer, self.c1)

    def test_employee_status_only_and_no_delete(self):
        c = APIClient(); c.force_authenticate(self.emp)
        r = c.patch(f"/api/tickets/{self.t1.pk}/", {"status": "in_progress", "title": "hack"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.t1.refresh_from_db()
        self.assertEqual((self.t1.status, self.t1.title), ("in_progress", "Ticket-A"))
        self.assertEqual(c.delete(f"/api/tickets/{self.t1.pk}/").status_code, 403)
