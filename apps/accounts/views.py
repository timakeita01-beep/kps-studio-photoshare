from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView

from apps.events.models import Event, Photo

from .forms import EmailLoginForm, PhotographerInviteForm, ProfileForm
from .mixins import AdminRequiredMixin
from .models import CustomUser


def humanize_bytes(num_bytes):
    value = float(num_bytes or 0)
    for unit in ['o', 'Ko', 'Mo', 'Go', 'To']:
        if value < 1024 or unit == 'To':
            return f'{value:.1f} {unit}'.replace('.0 ', ' ')
        value /= 1024
    return f'{value:.1f} To'


class EmailLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_admin:
            return reverse_lazy('accounts:admin_dashboard')
        return reverse_lazy('events:dashboard')


class EmailLogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('accounts:login')


class ProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Vos informations ont été mises à jour.')
        return super().form_valid(form)


class AccountPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        messages.success(self.request, 'Votre mot de passe a été modifié.')
        return super().form_valid(form)


class AdminDashboardView(AdminRequiredMixin, ListView):
    template_name = 'accounts/admin_dashboard.html'
    context_object_name = 'recent_events'

    def get_queryset(self):
        return Event.objects.select_related('photographer').order_by('-created_at')[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = list(Event.objects.all())
        total_events = len(events)
        pending_events = sum(1 for e in events if e.status == 'pending')
        active_events = sum(1 for e in events if e.status == 'active')
        expired_events = sum(1 for e in events if e.status == 'expired')

        context['total_photographers'] = CustomUser.objects.filter(is_photographer=True).count()
        context['active_photographers'] = CustomUser.objects.filter(is_photographer=True, is_active=True).count()
        context['total_events'] = total_events
        context['active_events'] = active_events
        context['pending_events'] = pending_events
        context['expired_events'] = expired_events
        context['active_pct'] = round(active_events / total_events * 100) if total_events else 0
        context['pending_pct'] = round(pending_events / total_events * 100) if total_events else 0

        context['total_photos'] = Photo.objects.count()
        context['total_storage'] = humanize_bytes(Photo.objects.aggregate(total=Sum('file_size'))['total'])

        context['top_photographers'] = (
            CustomUser.objects.filter(is_photographer=True)
            .annotate(event_count=Count('events'))
            .order_by('-event_count')[:5]
        )
        return context


class UserListView(AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        qs = CustomUser.objects.filter(is_photographer=True).annotate(event_count=Count('events'))
        status = self.request.GET.get('status')
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)
        return qs.order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status', 'all')
        return context


class UserCreateView(AdminRequiredMixin, View):
    template_name = 'accounts/user_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': PhotographerInviteForm()})

    def post(self, request):
        form = PhotographerInviteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le photographe a été créé.')
            return redirect('accounts:user_list')
        return render(request, self.template_name, {'form': form})


class UserToggleActiveView(AdminRequiredMixin, View):
    def post(self, request, pk):
        target = get_object_or_404(CustomUser, pk=pk, is_photographer=True)
        target.is_active = not target.is_active
        target.save(update_fields=['is_active'])
        state = 'activé' if target.is_active else 'désactivé'
        messages.success(request, f'Le compte de {target.email} a été {state}.')
        return redirect('accounts:user_list')
