from django.urls import path

from . import views

urlpatterns = [
    path("", views.TicketListView.as_view(), name="ticket-list"),
    path("new/", views.TicketCreateView.as_view(), name="ticket-create"),
    path("<int:pk>/", views.TicketDetailView.as_view(), name="ticket-detail"),
    path("<int:pk>/edit/", views.TicketUpdateView.as_view(), name="ticket-update"),
    path("<int:pk>/delete/", views.TicketDeleteView.as_view(), name="ticket-delete"),
]
