from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include, re_path
from . import views
from TPS.admin import admin_login

urlpatterns = [
    path('tenant/register', views.register, name='register'),
    path('tenant/login', views.loginpage, name='login'),
    path('tenant/logout', views.logoutpage , name='logout'),
    path('tenant/home', views.home, name='home'),
    path('tenant/billings', views.billings, name='billings'),
    path('tenant/billings_history', views.billings_history, name='billings_history'),
    path('tenant/payment_methods', views.payment_methods, name='payment_methods'),
    path('tenant/profile', views.profile, name='profile'),
    path('tenant/proof_history', views.proof_history, name='proof_history'),
    path('tenant/repair_add', views.repair_add, name='repair_add'),
    path('tenant/repair_tickets', views.repair_tickets, name='repair_tickets'),
    path('tenant/repair_track', views.repair_track, name='repair_track'),
    path('tenant/report_add', views.report_add, name='report_add'),
    path('tenant/report_tickets', views.report_tickets, name='report_tickets'),
    path('tenant/settings', views.settings, name='settings'),
    path('tenant/visitor', views.visitor, name='visitor'),
    path('tenant/contract', views.contract, name='contract'),
    path('tenant/visitor_history', views.visitor_history, name='visitor_history'),
    url('admin/myResidence/admin/(?P<pk>\d+)/change', views.admin_change, name='admin_change'),
    path('analytics/report', views.report, name='report'),
    path('analytics/attrition', views.attrition, name='attrition'),
    path('landlord/login/', views.loginadmin, name='login_admin'),
]

