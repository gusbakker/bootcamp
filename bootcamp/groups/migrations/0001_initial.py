# Generated by Django 2.1.1 on 2018-09-21 09:43

from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(max_length=500)),
                ('cover', models.ImageField(blank=True, null=True, upload_to='group_covers/')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('admins', models.ManyToManyField(related_name='inspected_groups', to=settings.AUTH_USER_MODEL)),
                ('banned_users', models.ManyToManyField(related_name='forbidden_groups', to=settings.AUTH_USER_MODEL)),
                ('subscribers', models.ManyToManyField(related_name='subscribed_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
    ]
