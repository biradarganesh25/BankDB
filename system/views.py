# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .forms import EmpRegForm, EmpCustLoginForm, CustomerRegForm, AccountRegForm, EmployeeUpdateForm
from .forms import CustomerDepositWithdrawForm, TakeLoanForm, RepayLoan, CustomerUpdateForm
from .models import Customer, Employee, EmpAccess, Account, Loan
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError


# Create your views here.


# Helper function to check whether is active or not
def is_active_check(user):
    return user.is_active == True


# Used to redirect. Might be made obsolete due to changing page redirection in future.
def index(request):
    return render(request, 'system/index.html', {})


def employee_reg_login(request, str):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:

        if str == 'emp_login':
            username = request.POST['e_id']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.user_prof.p_type == 0:
                    return HttpResponseRedirect(reverse('invalid_error_page'))
                login(request, user)
                return HttpResponseRedirect(reverse('employee_details'))


            else:
                # If the user has wrong credentials, redirect and inform the user.
                error = 'Invalid username or password.'
                messages.add_message(request, messages.INFO, error)
                return HttpResponseRedirect(reverse('employee_reg_login', args=('emp_login',)))

        else:
            # Display a form for a get request.
            username = request.POST['e_id']
            password = request.POST['password']
            # name = request.POST['name']
            access_obj = EmpAccess.objects.get(e_id=username)
            if access_obj is None or access_obj.access_key != int(request.POST['key']):
                return HttpResponseRedirect(reverse('invalid_error_page'))

            employee_form = EmpRegForm(request.POST)
            if employee_form.is_valid():
                employee_object = employee_form.save(commit=False)
                user = User.objects.create(username=username)  # Creating user object for each employee

                user.set_password(password)
                user.user_prof.p_type = 1
                user.save()
                user.user_prof.save()
                employee_object.user = user  # Linking employee object with user object(OneToOne field).
                user.emp.save()

            return HttpResponseRedirect(reverse('index'))

    elif str == 'emp_reg':
        # Deciding whether it is for registration or login.
        form = EmpRegForm()
        return render(request, 'system/emp_signup.html', {'form': form})
    elif str == 'emp_login':
        form = EmpCustLoginForm()
        return render(request, 'system/emp_login.html', {'form': form})


# Doing the same thing for customer as for employee.
# This function takes care of registering new customers.
def customer_register(request):
    if request.method == 'POST':

        curr_user = request.user
        username = request.POST['e_id']
        password = request.POST['password']
        emp_email = curr_user.username
        emp = Employee.objects.get(e_id=emp_email)

        customer_form = CustomerRegForm(request.POST)
        customer_form.is_valid()
        if not customer_form.is_valid():
            return HttpResponse("Please follow all the instruction next to the fields properly.")

        if customer_form.is_valid():
            user = User.objects.create(username=username)
            user.set_password(password)
            user.user_prof.p_type = 0
            user.save()

            customer_object = customer_form.save(commit=False)
            customer_object.emp = emp
            customer_object.user = user
            user.customer.save()  # Linking customer to user object. Again, (OneToOne Field).

            account_form = AccountRegForm(request.POST)
            account_object = account_form.save(commit=False)
            account_object.customer = customer_object
            customer_object.account.save()

            return HttpResponseRedirect(reverse('employee_details'))

    else:
        customer_form = CustomerRegForm()
        account_form = AccountRegForm()
        return render(request, 'system/customer_signup.html', {'customer_form': customer_form,
                                                               'account_form': account_form})


# This function handles customer logins.
def customer_login(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
        username = request.POST['e_id']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.user_prof.p_type == 1:
                return HttpResponseRedirect(reverse('invalid_error_page'))
            login(request, user)
            return HttpResponseRedirect(reverse('customer_details'))

        else:
            return HttpResponseRedirect(reverse('invalid_error_page'))

    else:

        return render(request, 'system/customer_login.html')


# To logout users.
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


# Used to redirect users to an error page.
def invalid_error_page(request):
    error = "Invalid username or password."
    return render(request, 'system/invalid_error_page.html', {'error': error})


# Used when there are insufficient funds in customer's account to take the requested action.
def insufficient_error_page(request):
    error = "Insufficient funds."
    return render(request, 'system/invali')


# Withdraws amount from customer's account and updates the information.
def customer_withdraw(request):
    if request.method == 'POST':

        user = request.user
        customer_email = user.username

        customer = Customer.objects.get(e_id=customer_email)
        account = Account.objects.get(customer=customer)
        amount = int(request.POST['amount'])

        if account.balance < amount:
            error = "You do not have sufficient funds."
            messages.add_message(request, messages.INFO, error)
            return HttpResponseRedirect(reverse('customer_details'))
        else:
            account.balance = account.balance - amount
            account.save()
            return HttpResponseRedirect(reverse('customer_details'))

    else:
        withdraw_form = CustomerDepositWithdrawForm()
        return render(request, 'system/customer_deposit_withdraw.html', {'withdraw_form': withdraw_form,
                                                                         'withdraw': 'withdraw'})


# Customer can add cash to their account.
def customer_deposit(request, customer_email):
    if request.method == 'POST':
        customer = Customer.objects.get(e_id=customer_email)
        account = Account.objects.get(customer=customer)
        amount = int(request.POST['amount'])

        account.balance = account.balance + amount
        account.save()
        return HttpResponseRedirect(reverse('employee_details'))
    else:
        deposit_form = CustomerDepositWithdrawForm()

        return render(request, 'system/customer_deposit_withdraw.html', {'deposit_form': deposit_form,
                                                                         'deposit': 'deposit',
                                                                         'email': customer_email})


# Used when customer applies loan.
def apply_loan(request):
    if not request.user.is_authenticated:
        return HttpResponse("You are not allowed to view this.")
    if request.method == 'POST':
        loan_form = TakeLoanForm(request.POST)
        if loan_form.is_valid():
            loan_object = loan_form.save(commit=False)

            customer = Customer.objects.get(e_id=request.user.username)
            account = Account.objects.get(customer=customer)
            loan_object.account = account
            interest_rate = .15
            if account.type == 'Saving':
                interest_rate = .15
            elif account.type == 'Current':
                interest_rate = .2
            per_month = loan_object.amount_taken / 12 + interest_rate * loan_object.amount_taken * 1
            # EMI scheme used. Taking minimum requirment for the customer to be eligible is /
            # for them to have at least half the income to support their family.
            if per_month > (customer.salary * 0.5):
                error = "Not eligible."
                messages.add_message(request, messages.INFO, error)
                return HttpResponseRedirect(reverse('customer_details'))

            loan_object.amount_left = loan_object.amount_taken
            loan_object.due_date = datetime.today() + timedelta(days=loan_object.end_time * 365)
            loan_object.monthly_due_date = datetime.today() + timedelta(days=31)
            loan_object.interest_rate = interest_rate
            loan_object.last_payment_date = datetime.today()
            loan_object.save()

            return HttpResponseRedirect(reverse('customer_details'))
        else:
            error = "You entered the wrong amount. Check amount left and min amount."
            messages.add_message(request, messages.INFO, error)
            return HttpResponseRedirect(reverse('customer_details'))
    else:
        loan_form = TakeLoanForm()
        return render(request, 'system/apply_loan.html', {'loan_form': loan_form})


# This function should only be accessible to logged in users.
# Used to get a customer's details.
@user_passes_test(is_active_check, login_url='index')
def customer_details(request):
    if not request.user.is_authenticated:
        return HttpResponse("You are not allowed to view this.")

    customer = Customer.objects.get(e_id=request.user.username)
    account = Account.objects.get(customer=customer)
    try:
        loan = Loan.objects.get(account=account)
        days = float(relativedelta(timezone.now(), loan.last_payment_date).days)
        interest_amount = float(days * loan.interest_rate * float(loan.amount_taken)) / 30.0

        if int(relativedelta(loan.monthly_due_date + timedelta(days=62), timezone.now()).days) < 0:
            request.user.is_active = False
            request.user.save()
            locked_out = "Defaulter. You have been locked out."
            messages.add_message(request, messages.INFO, locked_out)
            return HttpResponseRedirect(reverse('index'))

        return render(request, 'system/customer_details.html', {'customer': customer,
                                                                'account': account,
                                                                'loan': loan,
                                                                'interest_amount': interest_amount})

    except ObjectDoesNotExist:
        return render(request, 'system/customer_details.html', {'customer': customer,
                                                                'account': account
                                                                })


# Used to repay loan by the customer.
def repay_loan(request):
    if not request.user.is_authenticated:
        return HttpResponse("You are not allowed to view this.")
    customer = Customer.objects.get(e_id=request.user.username)
    account = Account.objects.get(customer=customer)
    loan = Loan.objects.get(account=account)
    if request.method == 'POST':
        amount = int(request.POST['amount'])

        if amount > account.balance:
            error = "Put cash into your account first."
            messages.add_message(request, messages.INFO, error)
            return HttpResponseRedirect(reverse('customer_details'))

        days = int(relativedelta(timezone.now(), loan.last_payment_date).days)
        interest_amount = days * loan.interest_rate * loan.amount_left / 30
        loan.amount_left = loan.amount_left - (amount) + interest_amount
        if loan.amount_left <= 0:
            done = "You have fully repaid your loan"
            messages.add_message(request, messages.INFO, done)
            account.balance -= amount
            account.save()
            loan.delete()
            return HttpResponseRedirect(reverse('customer_details'))
        else:
            message_ = "Amount deducted. "
            messages.add_message(request, messages.INFO, message_)
            loan.last_payment_date = timezone.now()
            loan.monthly_due_date = datetime.now() + timedelta(days=31)
            account.balance -= amount
            account.save()
            loan.save()
            return HttpResponseRedirect(reverse('customer_details'))
    else:
        days = float(relativedelta(timezone.now(), loan.last_payment_date).days)
        interest_amount = float(days * loan.interest_rate * float(loan.amount_taken)) / 30.0
        max_value = loan.amount_left + interest_amount
        repay_form = RepayLoan(max_value=max_value, min_value=interest_amount)
        return render(request, 'system/repay_loan.html', {'repay_form': repay_form})


# Shows employee details.
def employee_details(request):
    emp = Employee.objects.get(e_id=request.user.username)
    customers = emp.customer_set.all()
    defaulters = User.objects.filter(is_active=False)
    if len(defaulters) == 0:
        return render(request, 'system/employee_details.html', {'emp': emp,
                                                                'customers': customers})
    else:
        return render(request, 'system/employee_details.html', {'emp': emp,
                                                                'customers': customers,
                                                                'defaulters': defaulters})


# Used to delete a customer from the database.
@login_required
def delete_customer(request, customer_email):
    user = get_object_or_404(User, username=customer_email)
    user.delete()
    return HttpResponseRedirect(reverse('employee_details'))


# Used by employee to reactive a disabled user's account.
@login_required(login_url='index')
def renew(request, customer_email):
    customer = Customer.objects.get(e_id=customer_email)
    account = Account.objects.get(customer=customer)
    loan = Loan.objects.get(account=account)
    loan.delete()
    customer_user = User.objects.get(username=customer_email)
    customer_user.is_active = True
    customer_user.save()
    return HttpResponseRedirect(reverse('employee_details'))


# Used by the user's to transfer cash to other customers.
@login_required
def transfer(request):
    if not request.user.is_authenticated:
        return HttpResponse("You are not allowed to view this.")
    email = request.POST['email']
    amount = int(request.POST['amount'])
    try:
        to_customer = Customer.objects.get(e_id=email)
        curr_customer = Customer.objects.get(e_id=request.user.username)
        curr_account = Account.objects.get(customer=curr_customer)
        to_account = Account.objects.get(customer=to_customer)
        if curr_account.balance < amount:
            error = "Don't have sufficient funds."
            messages.add_message(request, messages.INFO, error)
            return HttpResponseRedirect(reverse('customer_details'))
        curr_account.balance -= amount
        to_account.balance += amount
        curr_account.save()
        to_account.save()
        success = "Transferred."
        messages.add_message(request, messages.INFO, success)
        return HttpResponseRedirect(reverse('customer_details'))
    except ObjectDoesNotExist:
        messages.add_message(request, messages.INFO, 'Cutomer does not exist.')
        return HttpResponseRedirect(reverse('customer_details'))


# Used by the customers to update their profile.
def customer_update_profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    customer = Customer.objects.get(e_id=request.user.username)
    if request.method == 'POST':

        customer_form = CustomerUpdateForm(request.POST, instance=customer)
        if customer_form.is_valid():
            try:
                customer_object = customer_form.save(commit=False)
                customer_object.save()
                customer_object.user.username = request.POST['e_id']
                customer_object.user.save()
                return HttpResponseRedirect(reverse('customer_details'))

            except IntegrityError:
                messages.add_message(request, messages.INFO, 'Please choose another username')
                update_form = CustomerUpdateForm(instance=customer)
                return render(request, 'system/customer_update_profile.html', {'form': update_form})


    else:

        update_form = CustomerUpdateForm(instance=customer)
        return render(request, 'system/customer_update_profile.html', {'form': update_form})


# Used by employee to update their profile.
@login_required(login_url='index')
def employee_update_profile(request):
    employee = Employee.objects.get(e_id=request.user.username)
    if request.method == 'POST':
        employee_form = EmployeeUpdateForm(request.POST, instance=employee)
        if employee_form.is_valid():
            try:
                employee_object = employee_form.save()
                employee_object.user.username = request.POST['e_id']
                employee_object.user.save()
                return HttpResponseRedirect(reverse('employee_details'))
            except:
                messages.add_message(request, messages.INFO, 'Please choose another username')
                employee_update_form = EmployeeUpdateForm(instance=customer)
                return render(request, 'system/employee_update_profile.html', {'form': employee_update_form})


    else:
        employee_update_form = EmployeeUpdateForm(instance=employee)
        return render(request, 'system/employee_update_profile.html', {'form': employee_update_form})


# Used by employee to update customer's salary.
@login_required(login_url='index')
def customer_update_salary(request, customer_email):
    customer = get_object_or_404(Customer, e_id=customer_email)
    if request.method == 'POST':
        amount = request.POST['salary']

        customer.salary = amount
        customer.save()
        return HttpResponseRedirect(reverse('employee_details'))
    else:
        return render(request, 'system/customer_update_salary.html', {'customer': customer})
