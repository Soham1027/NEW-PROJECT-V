# Generated by Django 5.0 on 2025-01-31 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VApp', '0002_otpsave_user_fullname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
    ]
