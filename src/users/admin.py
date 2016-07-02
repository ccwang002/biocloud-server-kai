from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import EmailUser as User
from .forms import AdminUserChangeForm, UserCreationForm


@admin.register(User)
class UserAdmin(UserAdmin):

    fieldsets = (
        (
            None,
            {'fields': ('email', 'password')}
        ),
        (
            _('Personal info'),
            {
                'fields': (
                    'name', 'auth_number',
                ),
            },
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'verified', 'is_active', 'is_staff', 'is_superuser',
                    'groups', 'user_permissions',
                ),
            },
        ),
        (
            _('Important dates'),
            {'fields': ('last_login', 'date_joined')},
        ),
    )
    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': (
                    'email', 'password1', 'password2',
                    'name', 'verified',
                ),
            },
        ),
    )

    form = AdminUserChangeForm
    add_form = UserCreationForm

    list_display = ('pk', 'email', 'name', 'is_staff')
    list_display_links = ('email',)
    list_filter = (
        'verified', 'is_active', 'is_staff', 'is_superuser', 'groups',
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
