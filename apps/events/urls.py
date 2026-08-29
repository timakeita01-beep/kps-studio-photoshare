from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('events/new/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<uuid:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<uuid:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/<uuid:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('events/<uuid:pk>/photos/upload/', views.PhotoUploadView.as_view(), name='photo_upload'),
    path('events/<uuid:pk>/photos/<uuid:photo_pk>/delete/', views.PhotoDeleteView.as_view(), name='photo_delete'),
    path('events/<uuid:pk>/share-link/regenerate/', views.ShareLinkRegenerateView.as_view(), name='share_link_regenerate'),
    path('events/<uuid:pk>/share-link/toggle/', views.ShareLinkToggleView.as_view(), name='share_link_toggle'),
    path('events/<uuid:pk>/mark-paid/', views.EventMarkPaidView.as_view(), name='event_mark_paid'),
    path('events/<uuid:pk>/mark-unpaid/', views.EventMarkUnpaidView.as_view(), name='event_mark_unpaid'),
    path('events/<uuid:pk>/extend/', views.EventExtendExpirationView.as_view(), name='event_extend'),
]
