# Generated by Django 5.0.2 on 2024-03-28 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_studymaterial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attemptquiz',
            options={'verbose_name_plural': '95. Attempted Questions/quiz'},
        ),
        migrations.RemoveField(
            model_name='attemptquiz',
            name='question',
        ),
    ]
