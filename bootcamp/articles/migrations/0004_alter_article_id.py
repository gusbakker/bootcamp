# Generated by Django 5.1.7 on 2025-03-14 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0003_auto_20200521_2125"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
