# Generated by Django 2.0.4 on 2018-05-08 21:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blood_bank', '0007_auto_20180509_0305'),
    ]

    operations = [
        migrations.RenameField(
            model_name='flowcontroller',
            old_name='previousRequest',
            new_name='requestIdentifier',
        ),
    ]
