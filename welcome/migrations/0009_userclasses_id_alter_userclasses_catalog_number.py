# Generated by Django 4.1.1 on 2022-10-11 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welcome', '0008_remove_userclasses_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userclasses',
            name='id',
            field=models.AutoField(auto_created=True, default=0, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userclasses',
            name='catalog_number',
            field=models.IntegerField(),
        ),
    ]
