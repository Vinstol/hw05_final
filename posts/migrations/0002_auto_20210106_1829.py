# Generated by Django 2.2.9 on 2021-01-06 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название группы')),
                ('slug', models.SlugField(unique=True, verbose_name='Идентификатор группы')),
                ('description', models.TextField(verbose_name='Описание группы')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='group',
            field=models.TextField(blank=True, null=True),
        ),
    ]
