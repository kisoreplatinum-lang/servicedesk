from rest_framework import serializers

from accounts.models import User
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.EMPLOYEE), allow_null=True, required=False
    )
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.username", read_only=True, default=None)

    class Meta:
        model = Ticket
        fields = [
            "id", "title", "description", "customer", "customer_name", "assigned_to",
            "assigned_to_name", "status", "priority", "created_at", "updated_at", "completed_at",
        ]
        read_only_fields = ["created_at", "updated_at", "completed_at"]


class TicketCustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "title", "description", "priority", "status"]
        read_only_fields = ["status"]


class TicketStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "status"]
