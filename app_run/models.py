from django.contrib.auth.models import User
from django.db import models


class Run(models.Model):
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
