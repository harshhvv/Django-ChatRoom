# Generated by Django 4.2.4 on 2023-08-10 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Rooms",
            new_name="Room",
        ),
    ]
