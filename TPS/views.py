from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponse
from myResidence.models import *


def index(request):
    return redirect('login')


def loginadmin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if str(user.is_staff) == "True":
                login(request, user)
                return redirect('admin:index')
            else:
                messages.error(request, 'Only Staffs can access the Tenant Management System.')
                return redirect('login_admin')
        elif TenantRegistration.objects.filter(username=username).exists() and TenantRegistration.objects.filter(
                password=password).exists():
            try:
                messages.warning(request, 'Only Staffs can access the Tenant Management System.')
            except TenantRegistration.DoesNotExist:
                messages.warning(request, 'Account does not exists.')
        elif Tenant.objects.filter(account__username=username).exists() and Tenant.objects.filter(account__password=password).exists():
            try:
                messages.warning(request, 'This is login for Staff only.')
            except Tenant.DoesNotExist:
                messages.warning(request, 'Account does not exists.')
        else:
            messages.error(request, 'Username/Password is incorrect.')

    context = {}
    return render(request, 'registration/login.html', context)