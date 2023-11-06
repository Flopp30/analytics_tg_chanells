# Generated by Django 4.2.7 on 2023-11-06 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_parts', '0002_externalsettings_starting_interval_second_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='externalsettings',
            name='min_messages_count_before_repost',
            field=models.IntegerField(default=20, help_text='Минимальное количество сообщений в канале до отправки репоста', verbose_name='Минимальное количество сообщений'),
        ),
        migrations.AddField(
            model_name='externalsettings',
            name='min_metrics_count_before_repost',
            field=models.IntegerField(default=5, help_text='Количество метрик у сообщения до отправки репоста', verbose_name='Количество метрик'),
        ),
    ]