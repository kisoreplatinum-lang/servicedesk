from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    ticket_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "name", "email", "phone", "company", "address", "is_active", "created_at", "ticket_count"]
        read_only_fields = ["created_at"]
