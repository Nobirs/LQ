from django.contrib import admin
from .models import Task, SubTask


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'deadline', 'user')
    list_filter = ('status', 'priority', 'deadline')
    search_fields = ('title', 'description')
    ordering = ('-deadline',)


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'deadline', 'task')
    list_filter = ('status', 'priority', 'deadline')
    search_fields = ('title', 'description')
    ordering = ('-deadline',)
