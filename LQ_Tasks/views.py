from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


    @action(detail=False, methods=['get'])
    def high_priority(self, request):
        high_priority_tasks = self.queryset.filter(priority__gte=7)
        serializer = self.get_serializer(high_priority_tasks, many=True)
        return Response(serializer.data)
