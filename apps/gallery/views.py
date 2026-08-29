import io
import zipfile

from django.contrib import messages
from django.db.models import F
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from apps.events.models import Event, Photo, ShareLink


def _access_reason(share_link):
    """Renvoie None si le lien est utilisable, sinon un motif d'inaccessibilité."""
    event = share_link.event
    if not share_link.is_active:
        return 'inactive'
    if not event.is_paid:
        return 'pending'
    if event.is_expired:
        return 'expired'
    return None


def _get_valid_share_link(token):
    share_link = get_object_or_404(ShareLink, token=token)
    return None if _access_reason(share_link) else share_link


def public_gallery(request, token):
    share_link = get_object_or_404(ShareLink, token=token)
    reason = _access_reason(share_link)

    if reason:
        return render(
            request, 'gallery/expired.html',
            {'event': share_link.event, 'reason': reason}, status=410,
        )

    event = share_link.event
    Event.objects.filter(pk=event.pk).update(view_count=F('view_count') + 1)

    context = {
        'event': event,
        'photographer': event.photographer,
        'photos': event.photos.all(),
        'share_link': share_link,
    }
    return render(request, 'gallery/public_gallery.html', context)


def access_by_code(request):
    code = (request.POST.get('code') or request.GET.get('code') or '').strip()
    share_link = ShareLink.objects.filter(token=code).first() if code else None

    if not share_link:
        messages.error(request, "Code d'accès invalide. Vérifiez le code transmis par votre photographe.")
        return redirect('home')

    return redirect('gallery:public_gallery', token=share_link.token)


def download_photo(request, token, photo_pk):
    share_link = _get_valid_share_link(token)
    if share_link is None:
        return render(request, 'gallery/expired.html', status=410)

    photo = get_object_or_404(Photo, pk=photo_pk, event=share_link.event)
    Event.objects.filter(pk=share_link.event_id).update(download_count=F('download_count') + 1)
    return FileResponse(photo.image.open('rb'), as_attachment=True, filename=photo.original_filename or photo.image.name)


def download_all(request, token):
    share_link = _get_valid_share_link(token)
    if share_link is None:
        return render(request, 'gallery/expired.html', status=410)

    event = share_link.event
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_STORED) as zip_file:
        for photo in event.photos.all():
            if not photo.image:
                continue
            with photo.image.open('rb') as fh:
                zip_file.writestr(photo.original_filename or photo.image.name, fh.read())
    buffer.seek(0)

    Event.objects.filter(pk=event.pk).update(download_count=F('download_count') + 1)

    response = HttpResponse(buffer.read(), content_type='application/zip')
    filename = f"{slugify(event.title) or 'galerie'}.zip"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
