from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Поля - в списке пользователей
    list_display = ('username', 'email', 'first_name', 'last_name', 'gender', 'is_staff', 'level', 'points')

    # - можно редактировать прямо из списка
    list_editable = ('level', 'points', 'email')

    # - по которым можно искать пользователей
    search_fields = ('email', 'username', 'first_name', 'last_name')

    # - отображаемые при просмотре/редактировании пользователя
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Game Data', {'fields': ('points', 'level')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
