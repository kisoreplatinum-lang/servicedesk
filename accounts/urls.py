from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import LoginForm
from .views import SignupView

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(authentication_form=LoginForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", SignupView.as_view(), name="signup"),
]
