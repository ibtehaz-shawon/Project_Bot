# Generated by Django 2.0.1 on 2018-01-29 06:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blood_bank', '0003_donationhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('getStartedStatus', models.BooleanField(default=False)),
                ('donationStatus', models.BooleanField(default=False)),
                ('informationStatus', models.BooleanField(default=False)),
                ('donationAvail', models.DateField()),
                ('userID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blood_bank.UserTable')),
            ],
        ),
    ]