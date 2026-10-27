from django import forms

from accounts.models import User
from core.forms import BootstrapFormMixin
from .models import Ticket


class TicketForm(BootstrapFormMixin, forms.ModelForm):
    """Fields depend on role and on create vs edit."""

    class Meta:
        model = Ticket
        fields = ["customer", "title", "description", "priority", "assigned_to", "status"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(role=User.Role.EMPLOYEE, is_active=True)
        self.fields["assigned_to"].required = False
        creating = self.instance.pk is None

        if user.is_customer_role:
            keep = {"title", "description", "priority"} if creating else set()
        elif user.is_employee_role:
            keep = {"customer", "title", "description", "priority"} if creating else {"status"}
        else:
            keep = set(self.fields)
        for name in list(self.fields):
            if name not in keep:
                del self.fields[name]
