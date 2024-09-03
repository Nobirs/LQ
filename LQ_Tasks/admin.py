from django.contrib import admin
from .models import Task, SubTask, Note


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


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'content_type')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)