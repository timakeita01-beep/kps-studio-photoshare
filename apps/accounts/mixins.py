from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Réserve la vue aux utilisateurs administrateurs."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin


class PhotographerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Réserve la vue aux utilisateurs photographes."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_photographer
