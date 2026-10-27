from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.views.generic import TemplateView

from customers.models import Customer
from tickets.models import Ticket


def last_months(n=6):
    today = timezone.localdate()
    y, m = today.year, today.month
    months = []
    for _ in range(n):
        months.append(date(y, m, 1))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return months[::-1]


def monthly_counts(qs, field, months):
    rows = (
        qs.filter(**{f"{field}__date__gte": months[0]})
        .annotate(m=TruncMonth(field))
        .values("m")
        .annotate(c=Count("id"))
    )
    lookup = {(r["m"].year, r["m"].month): r["c"] for r in rows}
    return [lookup.get((d.year, d.month), 0) for d in months]


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        tickets = Ticket.objects.for_user(user)
        S = Ticket.Status
        months = last_months(6)

        ctx["stats"] = {
            "customers": Customer.objects.count() if user.is_team else None,
            "open": tickets.filter(status=S.OPEN).count(),
            "in_progress": tickets.filter(status=S.IN_PROGRESS).count(),
            "completed": tickets.filter(status=S.COMPLETED).count(),
            "total": tickets.count(),
        }
        ctx["chart_data"] = {
            "labels": [d.strftime("%b %Y") for d in months],
            "created": monthly_counts(tickets, "created_at", months),
            "completed": monthly_counts(
                tickets.filter(status=S.COMPLETED, completed_at__isnull=False),
                "completed_at",
                months,
            ),
        }
        ctx["recent"] = tickets.select_related("customer", "assigned_to")[:5]
        return ctx
