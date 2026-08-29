from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(DjangoUserAdmin):
    ordering = ['-date_joined']
    list_display = ['email', 'company_name', 'is_admin', 'is_photographer', 'is_active', 'date_joined']
    list_filter = ['is_admin', 'is_photographer', 'is_active']
    search_fields = ['email', 'company_name']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations', {'fields': ('company_name',)}),
        ('Rôles', {'fields': ('is_admin', 'is_photographer', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'company_name', 'password1', 'password2', 'is_admin', 'is_photographer'),
        }),
    )
    readonly_fields = ['date_joined']
