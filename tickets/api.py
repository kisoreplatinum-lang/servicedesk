from rest_framework import filters, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from .models import Ticket
from .serializers import TicketCustomerCreateSerializer, TicketSerializer, TicketStatusSerializer


class TicketPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if view.action in ("update", "partial_update"):
            return user.is_team
        if view.action == "destroy":
            return user.is_admin_role
        return True


class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [TicketPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "customer__name"]
    ordering_fields = ["created_at", "priority", "status"]

    def get_queryset(self):
        qs = Ticket.objects.for_user(self.request.user).select_related("customer", "assigned_to")
        status = self.request.query_params.get("status")
        return qs.filter(status=status) if status else qs

    def get_serializer_class(self):
        user = self.request.user
        if self.action == "create" and user.is_customer_role:
            return TicketCustomerCreateSerializer
        if self.action in ("update", "partial_update") and user.is_employee_role:
            return TicketStatusSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_customer_role:
            profile = getattr(user, "customer_profile", None)
            if profile is None:
                raise PermissionDenied("No customer profile is linked to this account.")
            serializer.save(customer=profile)
        elif user.is_employee_role:
            serializer.save(assigned_to=user)
        else:
            serializer.save()
