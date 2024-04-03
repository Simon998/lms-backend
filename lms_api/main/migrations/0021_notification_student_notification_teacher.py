# Generated by Django 5.0.2 on 2024-03-21 14:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_alter_notification_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='student',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.student'),
        ),
        migrations.AddField(
            model_name='notification',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.teacher'),
        ),
    ]
