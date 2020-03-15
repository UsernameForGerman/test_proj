# Generated by Django 3.0.4 on 2020-03-15 10:12

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0006_auto_20200315_1010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='read_by',
            field=models.ManyToManyField(blank=True, default=None, related_name='user_read', to=settings.AUTH_USER_MODEL),
        ),
    ]
