# Generated by Django 4.2.2 on 2023-06-12 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distributor', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='App',
        ),
        migrations.DeleteModel(
            name='Database',
        ),
    ]
