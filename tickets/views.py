from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.models import User
from core.mixins import QueryStringMixin, RoleRequiredMixin
from customers.models import Customer
from .forms import TicketForm
from .models import Ticket


class TicketListView(LoginRequiredMixin, QueryStringMixin, ListView):
    paginate_by = 10

    def get_queryset(self):
        qs = Ticket.objects.for_user(self.request.user).select_related("customer", "assigned_to")
        status = self.request.GET.get("status", "")
        if status in Ticket.Status.values:
            qs = qs.filter(status=status)
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(customer__name__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = Ticket.Status.choices
        ctx["current_status"] = self.request.GET.get("status", "")
        return ctx


class TicketDetailView(LoginRequiredMixin, DetailView):
    def get_queryset(self):
        return Ticket.objects.for_user(self.request.user).select_related("customer", "assigned_to")


class TicketCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    success_url = reverse_lazy("ticket-list")
    success_message = "Ticket created."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        if user.is_customer_role:
            profile, _ = Customer.objects.get_or_create(
                user=user,
                defaults={"name": user.get_full_name() or user.username, "email": user.email},
            )
            form.instance.customer = profile
        elif user.is_employee_role:
            form.instance.assigned_to = user
        return super().form_valid(form)


class TicketUpdateView(RoleRequiredMixin, SuccessMessageMixin, UpdateView):
    allowed_roles = (User.Role.ADMIN, User.Role.EMPLOYEE)
    form_class = TicketForm
    success_message = "Ticket updated."

    def get_queryset(self):
        return Ticket.objects.for_user(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("ticket-detail", args=[self.object.pk])


class TicketDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = (User.Role.ADMIN,)
    model = Ticket
    success_url = reverse_lazy("ticket-list")

    def form_valid(self, form):
        messages.success(self.request, "Ticket deleted.")
        return super().form_valid(form)
