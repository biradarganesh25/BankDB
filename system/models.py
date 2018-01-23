# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from datetime import datetime
from django.db import models


class Employee(models.Model):
    e_id = models.EmailField(unique=True, default='default', blank=True)
    name = models.CharField(max_length=20, blank=True)
    salary = models.IntegerField(default=0, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='emp')

    def __str__(self):
        return self.name


# Create your models here.
class Customer(models.Model):
    e_id = models.EmailField(unique=True)
    aadhar_id = models.IntegerField(help_text='Must be 11 digits.',
                                    validators=[
                                        RegexValidator(r'\d{11,11}', 'Number must be 11 digits', 'Invalid number')])
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    salary = models.IntegerField(default=5000)
    user = models.OneToOneField(User, related_name='customer', on_delete=models.CASCADE)

    def __str__(self):
        return self.e_id


class Account(models.Model):
    acc_id = models.IntegerField(unique=True, help_text='Must be 10 digits',
                                 validators=[
                                     RegexValidator(r'\d{10,10}', 'Number must be 10 digits', 'Invalid number')])
    savings = "sv"
    current = "cr"
    account_choices = (
        (savings, 'Saving'),
        (current, 'Current'),
    )
    type = models.CharField(max_length=10, choices=account_choices, default=savings)
    balance = models.IntegerField(default=0)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='account')

    def __str__(self):
        return self.customer.e_id


class Loan(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='loan')
    start_time = models.DateField(auto_now_add=True)
    end_time = models.IntegerField(default=3, validators=[
        MaxValueValidator(15),
        MinValueValidator(1)
    ])
    amount_left = models.IntegerField()
    due_date = models.DateTimeField()
    monthly_due_date = models.DateTimeField()
    amount_taken = models.IntegerField(default=0)
    last_payment_date = models.DateTimeField(default=datetime.now())
    interest_rate = models.FloatField(default=0.15)

    def __str__(self):
        return self.account.customer.e_id


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user_prof')
    p_type = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class EmpAccess(models.Model):
    e_id = models.EmailField(unique=True)
    access_key = models.IntegerField(default=0)

    def __str__(self):
        return self.e_id


def create_profile(sender, **kwargs):
    if (kwargs['created']):
        user_profile = UserProfile(user=kwargs['instance'])
        user_profile.save()


post_save.connect(create_profile, sender=User)
