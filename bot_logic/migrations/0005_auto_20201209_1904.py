# Generated by Django 3.1.3 on 2020-12-09 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_logic', '0004_auto_20201209_1858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='category',
            field=models.CharField(blank=True, default='Без категории', max_length=255),
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.TextField(),
        ),
    ]
