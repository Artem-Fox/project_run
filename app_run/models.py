from django.contrib.auth.models import User
from django.db import models


class Run(models.Model):
    STATUS_CHOICES = [
        ("init", "Забег инициализирован"),
        ("in_progress", "Забег начат"),
        ("finished", "Забег закончен")
    ]

    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name="runs", verbose_name="Атлет")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default="init", verbose_name="Статус")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Забег"
        verbose_name_plural = "Забеги"

    def __str__(self):
        return f"{self.athlete.username} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"
