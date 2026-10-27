from django.conf import settings
from django.db import models
from django.utils import timezone

from customers.models import Customer


class TicketQuerySet(models.QuerySet):
    def for_user(self, user):
        """Admin: everything. Employee: assigned to them. Customer: their own."""
        if user.is_admin_role:
            return self.all()
        if user.is_employee_role:
            return self.filter(assigned_to=user)
        return self.filter(customer__user=user)


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=200)
    description = models.TextField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="tickets")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="assigned_tickets", limit_choices_to={"role": "employee"},
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    objects = TicketQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"#{self.pk} {self.title}"

    def save(self, *args, **kwargs):
        if self.status == self.Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != self.Status.COMPLETED:
            self.completed_at = None
        super().save(*args, **kwargs)

    @property
    def status_badge(self):
        return {"open": "danger", "in_progress": "warning", "completed": "success"}[self.status]

    @property
    def priority_badge(self):
        return {"low": "secondary", "medium": "info", "high": "danger"}[self.priority]
