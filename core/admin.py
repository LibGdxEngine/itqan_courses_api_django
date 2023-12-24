"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import User, Post, Tag


class UserAdmin(BaseUserAdmin):
    """Define admin pages for users"""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permissions'), {
            'fields':
                ('is_active',
                 'is_staff',
                 'is_superuser',
                 'groups',
                 'user_permissions'
                 ),
        }),
        (_('Important Dates'), {'fields': ('last_login',)}),
    )
    search_fields = ('email',)
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {'classes': ('wide',),
                'fields':
                    ('email',
                     'password1',
                     'password2',
                     'name',
                     'is_active',
                     'is_staff',
                     'is_superuser',
                     )
                }),
    )


class PostAdmin(admin.ModelAdmin):
    """Define admin pages for posts"""
    list_display = ['title', 'content', 'created_at', 'read_time_min', 'image']
    list_filter = ['created_at', 'status', 'by']
    search_fields = ['title', 'content', 'by__email', 'by__name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
