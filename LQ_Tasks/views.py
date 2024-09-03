from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Task, SubTask, Note
from .serializers import TaskSerializer, SubTaskSerializer, NoteSerializer
from django.contrib.contenttypes.models import ContentType

from itertools import chain
from django.db.models import Q


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['priority', 'deadline']
    ordering = ['priority']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Connect task to current user
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        if task.status != 'COMPLETED':
            raise PermissionDenied("You can only delete task that are completed.")
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def high_priority(self, request):
        high_priority_tasks = self.get_queryset().filter(priority__gte=7)
        serializer = self.get_serializer(high_priority_tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def subtasks(self, request, pk=None):
        task = self.get_object()
        if request.method == 'GET':
            subtasks = task.subtasks.all()
            serializer = SubTaskSerializer(subtasks, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = SubTaskSerializer(data=request.data)
            if serializer.is_valid():
                # Ensure that the task is associated with the correct user
                if serializer.validated_data['task'] != task:
                    raise PermissionDenied("You cannot add subtasks to this task.")
                serializer.save(task=task)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTaskViewSet(viewsets.ModelViewSet):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SubTask.objects.filter(task__user=self.request.user)
    
    def perform_create(self, serializer):
        task = serializer.validated_data['task']
        if task.user != self.request.user:
            raise PermissionDenied("You do not have permission to add subtasks to this task.")
        serializer.save()
    
    def perform_update(self, serializer):
        task = self.get_object().task
        if task.user != self.request.user:
            raise PermissionDenied("You do not have permission to update subtasks for this task.")
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.task.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this subtask.")
        instance.delete()


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        task_content_type = ContentType.objects.get_for_model(Task)
        subtask_content_type = ContentType.objects.get_for_model(SubTask)

        queryset = Note.objects.filter(
            Q(content_type=task_content_type, object_id__in=Task.objects.filter(user=user).values('id')) |
            Q(content_type=subtask_content_type, object_id__in=SubTask.objects.filter(task__user=user).values('id'))
        ).prefetch_related('content_object')

        return queryset

    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # Логируем ошибки сериализатора
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            print(serializer.errors)  # Логируем ошибки сериализатора
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
        return super().update(request, *args, **kwargs)
    
    def have_permission(self, obj):
        if hasattr(obj, 'user'):
            return obj.user == self.request.user
        else:
            return obj.task.user == self.request.user

    def perform_create(self, serializer):
        obj = serializer.validated_data['content_object']

        if not self.have_permission(obj):
            raise PermissionDenied("You do not have permission to add notes to this object.")
        serializer.save()
    
    def perform_update(self, serializer):
        obj = serializer.validated_data['content_object']
        if not self.have_permission(obj):
            raise PermissionDenied("You do not have permission to update notes for this object.")
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.content_object.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this note.")
        instance.delete()