# Generated by Django 5.0.4 on 2024-04-12 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ft', '0002_rename_board_fairytale_rename_writer_fairytale_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fairytale',
            name='date',
            field=models.DateField(),
        ),
    ]
