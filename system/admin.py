# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Customer, Account, Employee, UserProfile, EmpAccess, Loan

# Register your models here.
admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(Employee)
admin.site.register(UserProfile)
admin.site.register(EmpAccess)
admin.site.register(Loan)
