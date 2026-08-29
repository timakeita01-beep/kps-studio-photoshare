from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.EmailLoginView.as_view(), name='login'),
    path('logout/', views.EmailLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/password/', views.AccountPasswordChangeView.as_view(), name='password_change'),

    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/new/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<uuid:pk>/toggle/', views.UserToggleActiveView.as_view(), name='user_toggle_active'),
]
