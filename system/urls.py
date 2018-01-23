from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^employee_reg_login/(?P<str>[\w\-]+)/$', views.employee_reg_login, name='employee_reg_login'),
    url(r'^logout/$', views.logout_view, name='logout_view'),

    url(r'^invalid_error_page/$', views.invalid_error_page, name='invalid_error_page'),
    url(r'^customer_withdraw/$', views.customer_withdraw,
        name='customer_withdraw'),
    url(r'^apply_loan/$', views.apply_loan, name='apply_loan'),
    url(r'^customer_details/$', views.customer_details, name='customer_details'),
    url(r'^employee_details/$', views.employee_details, name='employee_details'),
    url(r'^repay_loan/$', views.repay_loan, name='repay_loan'),
    url(r'^delete_customer/(?P<customer_email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.delete_customer,
        name='delete_customer'),
    url(r'^customer_register/$', views.customer_register, name='customer_register'),
    url(r'^customer_login/$', views.customer_login, name='customer_login'),
    url(r'^renew/(?P<customer_email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        views.renew, name='renew'),
    url(r'^transfer/$', views.transfer, name='transfer'),
    url(r'^customer_deposit/(?P<customer_email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$', views.customer_deposit,
        name='customer_deposit'),
    url(r'^customer_update_profile/$', views.customer_update_profile, name='customer_update_profile'),
    url(r'^employee_update_profile/$', views.employee_update_profile, name='employee_update_profile'),
    url(r'^customer_udpate_salary/(?P<customer_email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        views.customer_update_salary, name='customer_update_salary'),

]
