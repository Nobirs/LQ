from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import TaskViewSet, SubTaskViewSet, NoteViewSet


router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

tasks_router = nested_routers.NestedSimpleRouter(router, r'tasks', lookup='task')
tasks_router.register(r'subtasks', SubTaskViewSet, basename='subtask')

# Создаем вложенный роутер для Note, связанный с Task и SubTask
notes_router = nested_routers.NestedSimpleRouter(router, r'tasks', lookup='task')
notes_router.register(r'notes', NoteViewSet, basename='task-note')

subtask_notes_router = nested_routers.NestedSimpleRouter(tasks_router, r'subtasks', lookup='subtask')
subtask_notes_router.register(r'notes', NoteViewSet, basename='subtask-note')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(tasks_router.urls)),
    path('', include(notes_router.urls)),
    path('', include(subtask_notes_router.urls)),
]
