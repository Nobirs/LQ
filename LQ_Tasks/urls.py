from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from .views import TaskViewSet, SubTaskViewSet


router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

tasks_router = nested_routers.NestedSimpleRouter(router, r'tasks', lookup='task')
tasks_router.register(r'subtasks', SubTaskViewSet, basename='subtask')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(tasks_router.urls)),
]
