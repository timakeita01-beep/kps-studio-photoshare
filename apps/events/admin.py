from django.contrib import admin

from .models import Event, Photo, ShareLink


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    readonly_fields = ['uploaded_at', 'file_size']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'photographer', 'event_type', 'created_at', 'expires_at', 'is_expired']
    list_filter = ['event_type', 'is_disabled']
    search_fields = ['title', 'photographer__email']
    inlines = [PhotoInline]


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ['event', 'token', 'is_active', 'created_at']
    search_fields = ['event__title', 'token']
