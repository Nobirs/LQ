from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['priority', 'deadline']
    ordering = ['priority']
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    

    def perform_create(self, serializer):
        # Connect current task to user
        serializer.save(user=self.request.user)


    @action(detail=False, methods=['get'])
    def high_priority(self, request):
        high_priority_tasks = self.get_queryset().filter(priority__gte=7)
        serializer = self.get_serializer(high_priority_tasks, many=True)
        return Response(serializer.data)


