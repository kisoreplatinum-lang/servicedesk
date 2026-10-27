from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Logged-in users whose role is in allowed_roles (superusers always pass)."""

    allowed_roles = ()

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.role in self.allowed_roles


class QueryStringMixin:
    """Exposes the current GET params minus 'page' so pagination links keep filters."""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["querystring"] = params.urlencode()
        return ctx
