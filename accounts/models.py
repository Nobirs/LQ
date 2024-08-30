from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('coach', 'Coach'),
        ('user', 'User'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    experience_level = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    notification_preferences = models.JSONField(default=dict)

    def increase_level(self):
        self.level += 1
        if self.points >= 100:
            self.points -= 100
    

    def can_manage_task(self, task):
        return self.role == 'admin' or task.user == self
    

    def __str__(self):
        return f'[{self.role}] - {self.username}'