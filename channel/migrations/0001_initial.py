# Generated by Django 4.2.7 on 2023-11-04 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='No name channel', max_length=128, verbose_name='Название канала')),
                ('category', models.CharField(default='Без категории', max_length=128, verbose_name='Категория чата')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлен')),
            ],
            options={
                'verbose_name': 'Канал',
                'verbose_name_plural': 'Каналы',
            },
        ),
    ]
