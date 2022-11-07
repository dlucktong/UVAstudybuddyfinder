# Generated by Django 4.1.3 on 2022-11-07 05:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('welcome', '0005_class'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='students',
            field=models.ManyToManyField(related_name='classes', to=settings.AUTH_USER_MODEL),
        ),
    ]