# Generated by Django 2.2 on 2022-03-27 17:34

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sudoku', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='savedsudoku',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 27, 17, 34, 42, 451605, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
