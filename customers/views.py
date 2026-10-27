from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import User
from core.mixins import QueryStringMixin, RoleRequiredMixin
from .forms import CustomerForm
from .models import Customer

TEAM = (User.Role.ADMIN, User.Role.EMPLOYEE)


class CustomerListView(RoleRequiredMixin, QueryStringMixin, ListView):
    allowed_roles = TEAM
    model = Customer
    paginate_by = 10

    def get_queryset(self):
        qs = Customer.objects.annotate(ticket_count=Count("tickets")).order_by("-created_at", "-id")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(email__icontains=q)
                | Q(phone__icontains=q) | Q(company__icontains=q)
            )
        return qs


class CustomerCreateView(RoleRequiredMixin, SuccessMessageMixin, CreateView):
    allowed_roles = TEAM
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy("customer-list")
    success_message = "Customer created."


class CustomerUpdateView(RoleRequiredMixin, SuccessMessageMixin, UpdateView):
    allowed_roles = TEAM
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy("customer-list")
    success_message = "Customer updated."


class CustomerDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = (User.Role.ADMIN,)
    model = Customer
    success_url = reverse_lazy("customer-list")

    def form_valid(self, form):
        messages.success(self.request, "Customer deleted.")
        return super().form_valid(form)
