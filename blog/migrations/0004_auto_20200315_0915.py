# Generated by Django 3.0.4 on 2020-03-15 09:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0003_auto_20200314_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='read_by',
            field=models.ManyToManyField(default=None, null=True, related_name='user_read', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL),
        ),
    ]
