from django.db import models
from accounts.models import CustomUser


class Task(models.Model):
    # Priority levels with game analogs
    PRIORITY_CHOICES = [
        (1, 'F'),
        (2, 'E'),
        (3, 'D'),
        (4, 'C'),
        (5, 'B'),
        (6, 'A'),
        (7, 'S'),
        (8, 'SS'),
        (9, 'SSS'),
        (10, 'EX'),
    ]

    # Task status
    STATUS_CHOICES = [
        ('CREATED', 'Created'),
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('PROCESSING', 'Processing'),
        ('ON_HOLD', 'On Hold'),
        ('DEFERRED', 'Deferred'),
        ('UNDER_REVIEW', 'Under Review'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CREATED')
    deadline = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')


    def __str__(self):
        return self.title
    

class SubTask(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField(choices=Task.PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=Task.STATUS_CHOICES, default='CREATED')
    deadline = models.DateTimeField(blank=True, null=True)
    task = models.ForeignKey(Task, related_name='subtasks', on_delete=models.CASCADE)