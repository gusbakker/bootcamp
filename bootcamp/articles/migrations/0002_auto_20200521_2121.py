# Generated by Django 2.2.9 on 2020-05-21 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='image',
            field=models.ImageField(upload_to='articles_pictures/%Y/%m/', verbose_name='Featured image'),
        ),
    ]