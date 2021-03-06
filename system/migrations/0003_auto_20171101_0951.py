# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-01 09:51
from __future__ import unicode_literals

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_auto_20171101_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='acc_id',
            field=models.IntegerField(help_text='Must be 5 digits', max_length=10, unique=True, validators=[django.core.validators.RegexValidator('\\d{10,10}', 'Number must be 10 digits', 'Invalid number')]),
        ),
        migrations.AlterField(
            model_name='customer',
            name='aadhar_id',
            field=models.IntegerField(help_text='Must be 11 digits.', validators=[django.core.validators.RegexValidator('\\d{11,11}', 'Number must be 11 digits', 'Invalid number')]),
        ),
        migrations.AlterField(
            model_name='loan',
            name='last_payment_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 1, 9, 51, 11, 743412)),
        ),
    ]
