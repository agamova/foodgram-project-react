from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Represents the model User in admin interface."""
    list_display = ('id',
                    'first_name',
                    'username',
                    'email',
                    'last_name',
                    'password',
                    )
    list_filter = ('email', 'username')


@admin.register(Follow)
class FolllowAdmin(admin.ModelAdmin):
    """Represents the model Follow in admin interface."""
    list_display = ('id', 'user', 'following')
