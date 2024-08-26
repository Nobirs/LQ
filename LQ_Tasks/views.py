from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Task, SubTask
from .serializers import TaskSerializer, SubTaskSerializer


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
