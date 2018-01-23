from django import forms
from django.forms import ModelForm
from .models import Customer, Account, Employee, Loan
import django.contrib.auth.password_validation as validators


class PasswordField(forms.CharField):
    def to_python(self, value):
        if not value:
            return ''
        else:
            return value

    def validate(self, value):
        super(PasswordField, self).validate(value)
        validators.validate_password(value)


class EmpRegForm(ModelForm):
    password = PasswordField(help_text=validators._password_validators_help_text_html(), widget=forms.PasswordInput())

    key = forms.IntegerField()

    class Meta:
        model = Employee
        fields = ['e_id', 'name', 'password', 'key', 'salary']


class EmpCustLoginForm(forms.Form):
    e_id = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


class CustomerRegForm(ModelForm):
    password = PasswordField(help_text=validators._password_validators_help_text_html(), widget=forms.PasswordInput())

    class Meta:
        model = Customer
        fields = ['aadhar_id', 'e_id', 'salary', 'password']


class AccountRegForm(ModelForm):
    class Meta:
        model = Account
        fields = ['acc_id', 'type', 'balance']


class CustomerDepositWithdrawForm(forms.Form):
    amount = forms.IntegerField()


class TakeLoanForm(ModelForm):
    class Meta:
        model = Loan
        fields = ['amount_taken', 'end_time']


class RepayLoan(forms.Form):
    amount = forms.IntegerField()

    def __init__(self, max_value, min_value, *args, **kwargs):
        super(RepayLoan, self).__init__(*args, **kwargs)
        self.fields['amount'] = forms.IntegerField(max_value=max_value, min_value=min_value)


class CustomerUpdateForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['e_id']


class EmployeeUpdateForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['e_id', 'name']
