# Generated by Django 4.1.1 on 2022-10-11 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welcome', '0007_alter_userclasses_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userclasses',
            name='id',
        ),
        migrations.AlterField(
            model_name='userclasses',
            name='catalog_number',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
