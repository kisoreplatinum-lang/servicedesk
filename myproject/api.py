from rest_framework.routers import DefaultRouter

from customers.api import CustomerViewSet
from tickets.api import TicketViewSet

router = DefaultRouter()
router.register("customers", CustomerViewSet, basename="api-customer")
router.register("tickets", TicketViewSet, basename="api-ticket")
