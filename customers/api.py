from django.db.models import Count
from rest_framework import filters, viewsets
from rest_framework.permissions import BasePermission

from .models import Customer
from .serializers import CustomerSerializer


class CustomerPermission(BasePermission):
    """Admin/Employee only; deleting is Admin only."""

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or not user.is_team:
            return False
        if view.action == "destroy":
            return user.is_admin_role
        return True


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [CustomerPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "email", "phone", "company"]

    def get_queryset(self):
        return Customer.objects.annotate(ticket_count=Count("tickets")).order_by("-created_at", "-id")
