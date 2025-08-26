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
    distance = models.FloatField(blank=True, null=True, verbose_name="Пройденная дистанция")

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


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="positions", verbose_name="Забег")
    latitude = models.DecimalField(max_digits=6, decimal_places=4, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=7, decimal_places=4, verbose_name="Долгота")

    class Meta:
        verbose_name = "Позиция"
        verbose_name_plural = "Позиции"

    def __str__(self):
        return f"{self.run}: {self.latitude}, {self.longitude}"


class CollectibleItem(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    uid = models.CharField(max_length=255, verbose_name="UID")
    latitude = models.DecimalField(max_digits=6, decimal_places=4, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=7, decimal_places=4, verbose_name="Долгота")
    picture = models.URLField(verbose_name="Ссылка на картинку")
    value = models.IntegerField(verbose_name="Значение")
    users = models.ManyToManyField(User, blank=True, related_name="items", verbose_name="Атлеты")

    class Meta:
        verbose_name = "Коллекционный предмет"
        verbose_name_plural = "Коллекционные предметы"
