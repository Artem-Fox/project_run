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


class AthleteInfo(models.Model):
    athlete = models.OneToOneField(User, on_delete=models.CASCADE, related_name="athlete_info", verbose_name="Атлет")
    goals = models.TextField(blank=True, verbose_name="Цели")
    weight = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Вес")

    class Meta:
        verbose_name = "Информация об атлете"
        verbose_name_plural = "Информация об атлетах"

    def __str__(self):
        return self.athlete.username


class Challenge(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="Название челленджа")
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name="challenges", verbose_name="Атлет")

    class Meta:
        verbose_name = "Челлендж"
        verbose_name_plural = "Челленджи"
        constraints = [
            models.UniqueConstraint(
                fields=["full_name", "athlete"],
                name="unique_challenge_per_athlete"
            )
        ]

    def __str__(self):
        return self.full_name
