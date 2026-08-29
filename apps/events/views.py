from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.accounts.mixins import PhotographerRequiredMixin

from .forms import EventForm, validate_uploaded_photo
from .models import Event, Photo, ShareLink


def get_owned_event(request, pk):
    return get_object_or_404(Event, pk=pk, photographer=request.user)


class DashboardView(PhotographerRequiredMixin, ListView):
    model = Event
    template_name = 'events/dashboard.html'
    context_object_name = 'events'

    def get_queryset(self):
        events = list(Event.objects.filter(photographer=self.request.user).order_by('-created_at'))
        status = self.request.GET.get('status')
        if status in ('active', 'pending', 'expired'):
            events = [e for e in events if e.status == status]
        return events

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status', 'all')
        return context


class EventCreateView(PhotographerRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def form_valid(self, form):
        form.instance.photographer = self.request.user
        should_mark_paid = form.cleaned_data.get('is_paid', False)
        form.instance.is_paid = False
        response = super().form_valid(form)
        ShareLink.objects.create(event=self.object)
        if should_mark_paid:
            self.object.mark_paid()
        messages.success(self.request, "L'événement a été créé.")
        return response

    def get_success_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.object.pk})


class EventDetailView(PhotographerRequiredMixin, DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.filter(photographer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.all()
        context['share_link'] = getattr(self.object, 'share_link', None)
        return context


class EventUpdateView(PhotographerRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def get_queryset(self):
        return Event.objects.filter(photographer=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "L'événement a été mis à jour.")
        return reverse('events:event_detail', kwargs={'pk': self.object.pk})


class EventDeleteView(PhotographerRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'

    def get_queryset(self):
        return Event.objects.filter(photographer=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "L'événement a été supprimé.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('events:dashboard')


class PhotoUploadView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        event = get_owned_event(request, pk)
        files = request.FILES.getlist('images')

        if not files:
            messages.error(request, "Aucun fichier sélectionné.")
            return redirect('events:event_detail', pk=event.pk)

        created, errors = 0, []
        for f in files:
            error = validate_uploaded_photo(f)
            if error:
                errors.append(error)
                continue
            Photo.objects.create(event=event, image=f)
            created += 1

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'created': created, 'errors': errors})

        if created:
            messages.success(request, f'{created} photo(s) importée(s).')
        for error in errors:
            messages.error(request, error)
        return redirect('events:event_detail', pk=event.pk)


class PhotoDeleteView(PhotographerRequiredMixin, View):
    def post(self, request, pk, photo_pk):
        event = get_owned_event(request, pk)
        photo = get_object_or_404(Photo, pk=photo_pk, event=event)
        photo.image.delete(save=False)
        photo.delete()
        messages.success(request, 'La photo a été supprimée.')
        return redirect('events:event_detail', pk=event.pk)


class ShareLinkRegenerateView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        event = get_owned_event(request, pk)
        share_link, _ = ShareLink.objects.get_or_create(event=event)
        share_link.regenerate()
        messages.success(request, 'Le lien de partage a été régénéré.')
        return redirect('events:event_detail', pk=event.pk)


class ShareLinkToggleView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        event = get_owned_event(request, pk)
        share_link, _ = ShareLink.objects.get_or_create(event=event)
        share_link.is_active = not share_link.is_active
        share_link.save(update_fields=['is_active'])
        state = 'activé' if share_link.is_active else 'désactivé'
        messages.success(request, f'Le lien de partage a été {state}.')
        return redirect('events:event_detail', pk=event.pk)


class EventMarkPaidView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        event = get_owned_event(request, pk)
        event.mark_paid()
        messages.success(
            request,
            "L'événement est marqué comme payé : le lien de partage est actif et expire dans 15 jours.",
        )
        return redirect('events:event_detail', pk=event.pk)


class EventMarkUnpaidView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        event = get_owned_event(request, pk)
        event.mark_unpaid()
        messages.success(request, "L'événement est marqué comme impayé : le lien de partage est bloqué.")
        return redirect('events:event_detail', pk=event.pk)


class EventExtendExpirationView(PhotographerRequiredMixin, View):
    def post(self, request, pk):
        event = get_owned_event(request, pk)
        if not event.is_paid:
            messages.error(request, "Impossible de prolonger un événement non payé.")
        else:
            event.extend_expiration(15)
            messages.success(request, "L'expiration a été prolongée de 15 jours.")
        return redirect('events:event_detail', pk=event.pk)
