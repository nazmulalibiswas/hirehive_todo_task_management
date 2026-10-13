from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class CustomUserInfoModel(AbstractUser):
    """Custom user model with full_name field."""
    full_name = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.username} - {self.full_name}'


class TaskModel(models.Model):
    """Task model linked to a user."""
    STATUS = [
        ('Pending', 'Pending'),
        ('InProgress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='Pending',
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.title or '(Untitled)'
