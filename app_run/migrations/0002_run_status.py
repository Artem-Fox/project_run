# Generated by Django 5.2 on 2025-07-27 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='run',
            name='status',
            field=models.CharField(choices=[('init', 'Забег инициализирован'), ('in_progress', 'Забег начат'), ('finished', 'Забег закончен')], default='init', max_length=11),
        ),
    ]
