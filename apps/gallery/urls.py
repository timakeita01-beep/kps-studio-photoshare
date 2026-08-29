from django.urls import path

from . import views

app_name = 'gallery'

urlpatterns = [
    path('access/', views.access_by_code, name='access_by_code'),
    path('g/<str:token>/', views.public_gallery, name='public_gallery'),
    path('g/<str:token>/download/<uuid:photo_pk>/', views.download_photo, name='download_photo'),
    path('g/<str:token>/download-all/', views.download_all, name='download_all'),
]
