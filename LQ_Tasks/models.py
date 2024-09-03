from django.db import models
from accounts.models import CustomUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


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
    notes = GenericRelation('Note')

    def __str__(self):
        return self.title
    

class SubTask(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField(choices=Task.PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=Task.STATUS_CHOICES, default='CREATED')
    deadline = models.DateTimeField(blank=True, null=True)
    task = models.ForeignKey(Task, related_name='subtasks', on_delete=models.CASCADE)
    notes = GenericRelation('Note')

    def __str__(self):
        return f'{self.task} ->  {self.title}'
    

    def save(self, *args, **kwargs):
        # Устанавливаем приоритет подзадачи равным приоритету родительской задачи
        if self.task.priority > 1:
            self.priority = self.task.priority - 1
        else:
            self.priority = self.task.priority
        super(SubTask, self).save(*args, **kwargs)


class Note(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.content_object} -> {self.title}'