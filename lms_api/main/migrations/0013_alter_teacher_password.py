# Generated by Django 5.0.2 on 2024-03-19 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_rename_profile_image_teacher_profile_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='password',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
