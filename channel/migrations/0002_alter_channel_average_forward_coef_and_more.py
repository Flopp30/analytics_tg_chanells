# Generated by Django 4.2.7 on 2023-11-19 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='average_forward_coef',
            field=models.DecimalField(blank=True, decimal_places=5, default=None, max_digits=5, null=True, verbose_name='Коэф. репоста'),
        ),
        migrations.AlterField(
            model_name='channel',
            name='average_react_coef',
            field=models.DecimalField(blank=True, decimal_places=5, default=None, max_digits=5, null=True, verbose_name='Коэф. реакции'),
        ),
    ]
