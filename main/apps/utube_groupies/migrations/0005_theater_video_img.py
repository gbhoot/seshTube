# Generated by Django 2.1.2 on 2018-10-26 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utube_groupies', '0004_theater_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='theater',
            name='video_img',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
