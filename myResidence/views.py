from datetime import datetime, date, timedelta
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.db.models import Q, Count, FloatField, Max, Sum
from django.db.models.functions import Cast, StrIndex, Substr
from django_tables2.views import SingleTableView
from django_tables2.export.views import ExportMixin
import pandas as pd
import xgboost as xgb

model2 = xgb.XGBRegressor()
model2.load_model("static/json/churnprediction.json")


def is_leap_year(year):
    if year % 100 == 0:
        return year % 100 == 0

    return year % 4 == 0


def get_lapse():
    last_month = datetime.today().month
    current_year = datetime.today().year

    # is last month a month with 30 days?
    if last_month in [9, 4, 6, 11]:
        lapse = 30

    # is last month a month with 31 days?
    elif last_month in [1, 3, 5, 7, 8, 10, 12]:
        lapse = 31

    # is last month February?
    else:
        if is_leap_year(current_year):
            lapse = 29
        else:
            lapse = 30

    return lapse


# not used (def tenantregister)
def tenantregister(request):
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.warning(request, 'We will now verify your Tenant Account Validation.')
            return redirect('login')
        else:
            return redirect('register')

    context = {'form': form}
    return render(request, 'tenant/tenant_register2.html', context)


def register(request):
    tncontent = TermsAndCondition.objects.get(pk=1)
    regform = TenantRegistrationForm(initial={'status': 'Pending', 'date_joined': datetime.now(), 'isactive': 'True'})
    todate = date.today()

    if request.method == 'POST':
        regform = TenantRegistrationForm(request.POST)
        print(regform.errors)
        if regform.is_valid():
            regform.save()
            messages.warning(request, 'We will now verify your Tenant Account Validation.')
            return redirect('login')
        else:
            return redirect('register')

    context = {'form': regform, 'tncontent': tncontent, 'todate': todate}
    return render(request, 'tenant/tenant_register.html', context)


def loginpage(request):
    # ---------------------------------- init functions ---------------------------------- #
    # billings overdue
    todate = date.today()
    todate1 = todate.strftime("%Y-%m-%d")
    Billing.objects.filter(due_date__lte=todate, status='Pending').update(status='Overdue')

    # visitor request overdue
    Visitor.objects.filter(visit_date__lte=todate, status='Pending').update(status='Rejected', isactive='')

    # repair request overdue
    Repair.objects.filter(date_available__lte=todate, status='Pending').update(status='Date Unavailable')

    # billings overdue and grace period
    billings_ud = Billing.objects.all()

    for each in billings_ud:
        if each.is_late == "No" and each.status == "Overdue":
            datepay = each.due_date
            contract = TenantContract.objects.get(tenant=each.tenant)
            b = abs(relativedelta(datepay, todate))

            if b.days >= contract.grace_period:
                latecollection = contract.late_collection
                if latecollection <= 5:
                    addpay = float(latecollection) * .01
                    percentpay = float(each.billing_fee) * float(addpay)
                    totalpay = float(each.billing_fee) + float(percentpay)
                    Billing.objects.filter(id=each.id).update(is_late='Yes', billing_fee=totalpay)
                else:
                    totalpay = float(latecollection) + float(each.billing_fee)
                    Billing.objects.filter(id=each.id).update(is_late='Yes', billing_fee=totalpay)
        else:
            pass

    # create rent billing
    last_month_filter = datetime.today() - timedelta(days=get_lapse())
    for each_t in Tenant.objects.all():
        updaterent = Billing.objects.filter(date_issued__lte=last_month_filter,
                                            billing_type__billing_code="RB", tenant__id=each_t.id)
        # monthly rentbills
        if updaterent:
            if Billing.objects.filter(date_issued__gte=last_month_filter, billing_type__billing_code="RB", tenant__id=each_t.id):
                pass
            else:
                tenant = each_t.id
                billing_type = BillingType.objects.get(billing_name="Rent Bill")
                billing_fee = TenantContract.objects.get(tenant__id=each_t.id)
                due_date = date.today() + relativedelta(months=+1)
                due_date1 = due_date.strftime("%Y-%m-%d")

                data = {'tenant': tenant, 'date_issued': todate1, 'billing_type': billing_type.id, 'is_late': 'No',
                        'billing_fee': billing_fee.rent, 'due_date': due_date1, 'status': 'Pending',
                        'is_active': 'True', }
                form = BillingForm(data)

                print(form.errors)
                if form.is_valid():
                    form.save()
                else:
                    messages.error(request, "Monthly Rent Billing save failed.")

        # create new rentbills
        else:
            contract = TenantContract.objects.filter(tenant__id=each_t.id)

            # must have contract first
            if contract:
                createrent = Billing.objects.filter(billing_type__billing_code="RB", tenant__id=each_t.id)
                tc = TenantContract.objects.get(tenant__id=each_t.id)
                d = tc.move_date

                if d.day == todate.day and not createrent:
                    tenant = each_t.id
                    billing_type = BillingType.objects.get(billing_name="Rent Bill")
                    billing_fee = tc.rent
                    due_date = date.today() + relativedelta(months=+1)
                    due_date1 = due_date.strftime("%Y-%m-%d")

                    data = {'tenant': tenant, 'date_issued': todate1, 'billing_type': billing_type.id, 'is_late': 'No',
                            'billing_fee': billing_fee, 'due_date': due_date1, 'status': 'Pending', 'is_active': 'True', }
                    form = BillingForm(data)

                    print(form.errors)
                    if form.is_valid():
                        form.save()
                    else:
                        messages.error(request, "New Rent Billing save failed.")

    # login form
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if str(user.is_staff) == "False":
                login(request, user)

                date_time = datetime.now()
                tenantuser = user.tenant.id
                activity = "Access"
                action = "Logged In"

                data1 = {'date_time': date_time, 'tenant': tenantuser, 'activity': activity, 'action': action,
                         'is_active': 'True', }
                form1 = TenantLogsForm(data1)

                print(form1.errors)
                if form1.is_valid():
                    form1.save()
                else:
                    messages.error(request, "Tenant Log failed.")

                return redirect('home')
            else:
                messages.error(request, 'Only tenants can access the myResidence Portal.')
                return redirect('login')
        elif TenantRegistration.objects.filter(username=username).exists() and TenantRegistration.objects.filter(
                password=password).exists():
            try:
                regacc = TenantRegistration.objects.get(username=username, password=password)

                if regacc.status == 'Rejected':
                    messages.error(request, 'Sorry, your account registration has been rejected.')
                if regacc.status == 'Pending':
                    messages.warning(request, 'Please wait for your account verification.')
            except TenantRegistration.DoesNotExist:
                messages.warning(request, 'Account does not exists.')
        else:
            messages.error(request, 'Username/Password is incorrect.')

    context = {}
    return render(request, 'tenant/tenant_login.html', context)


def logoutpage(request):
    if request.user.is_anonymous is True:
        return redirect('login')
    else:
        date_time = datetime.now()
        tenantuser = request.user.tenant.id
        activity = "Access"
        action = "Logged Out"

        data1 = {'date_time': date_time, 'tenant': tenantuser, 'activity': activity, 'action': action,
                 'is_active': 'True', }
        form1 = TenantLogsForm(data1)

        print(form1.errors)
        if form1.is_valid():
            form1.save()
        else:
            messages.error(request, "Tenant Log failed.")

        logout(request)

    context = {}
    return render(request, 'tenant/tenant_logout.html', context)


def admin_change(request):
    aid = request.user.admin.id

    context = {'aid': aid}
    return render(request, 'admin/myResidence/admin/', context)


# login_required(login_url='login')
# allowed_users(allowed_roles=['tenant'])
def home(request):
    tid = request.user.tenant.id
    announcement = TenantAnnouncement.objects.get(pk=1)
    news = AnnouncementNew.objects.order_by('-datepublished')
    notif = LogAdmin.objects.filter(tenant__id=tid, isactive='True')
    contract = TenantContract.objects.filter(tenant__id=tid, confirmation='None')

    if notif:
        notifctr = LogAdmin.objects.filter(tenant__id=tid, isactive='True').count()
        notiflast = notif = LogAdmin.objects.filter(tenant__id=tid, isactive='True').latest('date_time')
    else:
        notifctr = 0
        notiflast = ""

    if request.method == 'POST':
        if request.POST.get("form_type") == 'con_notify':
            tenantid = request.POST.get('id')
            LogAdmin.objects.filter(tenant=tenantid, isactive='True').update(isactive='', )
            return redirect('billings')
        elif request.POST.get("form_type") == 'con_contract' and request.POST.get("confirmation") == 'Yes':
            tenantid = request.POST.get('id')
            confirmation = request.POST.get('confirmation')
            # TenantContract.objects.filter(tenant=tenantid).update(confirmation=confirmation, )
            messages.success(request, "Your Contract has now been confirmed. Thank you for your time.")
            return redirect('contract')
        elif request.POST.get("form_type") == 'con_contract' and request.POST.get("confirmation") == 'No':
            messages.warning(request, "Please visit our office with regards to your contract ")
            return redirect('home')

    context = {'announcement': announcement, 'news': news, 'notif': notif, 'notifctr': notifctr, 'notiflast': notiflast, 'contract':contract}
    return render(request, 'tenant/tenant_home.html', context)


def contract(request):
    tid = request.user.tenant.id
    contract_info = TenantContract.objects.filter(tenant__id=tid, confirmation='None')

    context = {'contract': contract_info}
    return render(request, 'tenant/tenant_contract.html', context)


def billings(request):
    tid = request.user.tenant.id
    bills = Billing.objects.filter(tenant=tid, status='Pending') | Billing.objects.filter(tenant=tid, status='Overdue')

    form = ProofForm(initial={'status': 'Pending', 'date_submitted': datetime.now(), 'isactive': 'True'})

    if request.method == 'POST':
        form = ProofForm(request.POST, request.FILES)
        tenant_id = Tenant.objects.get(id=tid)
        print(form.errors)
        if form.is_valid():
            bid = request.POST.get('billing')
            comp = form.save(commit=False)
            comp.tenant = tenant_id
            comp.save()

            date_time = datetime.now()
            activity = "Proof of Payment"
            action = "Submitted Proof of Payment for Billing #" + str(bid)

            data1 = {'date_time': date_time, 'tenant': tid, 'activity': activity, 'action': action,
                     'is_active': 'True', }
            form1 = TenantLogsForm(data1)

            print(form1.errors)
            if form1.is_valid():
                form1.save()
            else:
                messages.error(request, "Tenant Log failed.")

            messages.success(request, 'Proof of Payment successfully submitted.')
            return redirect('proof_history')
        else:
            messages.error(request, 'Proof of Payment submission failed.')
            return redirect('billings')

    context = {'bills': bills, 'form': form}
    return render(request, 'tenant/tenant_billings.html', context)


def billings_history(request):
    tid = request.user.tenant.id
    bills = Billing.objects.filter(tenant=tid, status='Paid')

    context = {'bills': bills}
    return render(request, 'tenant/tenant_billings_history.html', context)


def payment_methods(request):
    return render(request, 'tenant/tenant_payment_methods.html')


def profile(request):
    tid = request.user.tenant.id
    uid = request.user.tenant.unit
    logs = LogTenant.objects.filter(tenant_id=tid).order_by('-date_time')[:5]
    logs2 = LogTenant.objects.filter(tenant_id=tid).order_by('-date_time')
    recount = LogTenant.objects.filter(tenant_id=tid).count()
    roomies = Tenant.objects.filter(unit=uid, isactive='True')

    datejoin = request.user.date_joined.date()
    context = {'datejoin': datejoin, 'roomies': roomies, 'logs': logs, 'logs2': logs2, 'recount': recount, }
    return render(request, 'tenant/tenant_profile.html', context)


def proof_history(request):
    tid = request.user.tenant.id
    proofpay = ProofOfPayment.objects.filter(billing__tenant_id=tid)

    context = {'proofpay': proofpay}
    return render(request, 'tenant/tenant_proof_history.html', context)


def repair_add(request):
    form = RepairForm(initial={'status': 'Pending', 'date_issued': datetime.now(), 'isactive': 'True'})

    if request.method == 'POST':
        form = RepairForm(request.POST, request.FILES)
        tenant = request.user.tenant.id
        tenant_id = Tenant.objects.get(id=tenant)
        print(form.errors)
        if form.is_valid():
            comp = form.save(commit=False)
            comp.tenant = tenant_id
            comp.save()
            raid = comp.id

            date_time = datetime.now()
            tenantuser = request.user.tenant.id
            activity = "Repair"
            action = "Submitted Repair Request #" + str(raid)

            data1 = {'date_time': date_time, 'tenant': tenantuser, 'activity': activity, 'action': action,
                     'is_active': 'True', }
            form1 = TenantLogsForm(data1)

            print(form1.errors)
            if form1.is_valid():
                form1.save()
            else:
                messages.error(request, "Tenant Log failed.")

            messages.success(request, 'Repair Request successfully submitted.')
            return redirect('repair_track')
        else:
            messages.error(request, 'Repair Request submission failed.')
            return redirect('report_add')

    context = {'form': form}
    return render(request, 'tenant/tenant_repair_add.html', context)


def repair_tickets(request):
    tid = request.user.tenant.id
    repair = Repair.objects.filter(tenant=tid, status='Resolved') | Repair.objects.filter(tenant=tid,
                                                                                          status='Cancelled')

    context = {'repair': repair}
    return render(request, 'tenant/tenant_repair_tickets.html', context)


def repair_track(request):
    tid = request.user.tenant.id
    repair = Repair.objects.filter(tenant=tid, status='Pending') | Repair.objects.filter(tenant=tid,
                                                                                         status='Date_Unavailable') | Repair.objects.filter(
        tenant=tid, status='Scheduled')

    if request.method == 'POST':
        if request.POST.get("form_type") == 'cancelform':
            rid = request.POST.get('id')

            Repair.objects.filter(id=rid).update(status='Cancelled', isactive='', )

            date_time = datetime.now()
            activity = "Repair"
            action = "Cancelled Repair Request #" + str(rid)

            data1 = {'date_time': date_time, 'tenant': tid, 'activity': activity, 'action': action,
                     'is_active': 'True', }
            form1 = TenantLogsForm(data1)

            print(form1.errors)
            if form1.is_valid():
                form1.save()
            else:
                messages.error(request, "Tenant Log failed.")

            messages.success(request, 'Repair Request #' + rid + ' Cancelled.')
            return redirect('repair_tickets')

        elif request.POST.get("form_type") == 'reschedform':
            rid = request.POST.get('id')
            rdate = request.POST.get('date_available')

            Repair.objects.filter(id=rid).update(date_available=rdate, status='Pending')

            date_time = datetime.now()
            activity = "Repair"
            action = "Rescheduled Repair Request #" + str(rid)

            data1 = {'date_time': date_time, 'tenant': tid, 'activity': activity, 'action': action,
                     'is_active': 'True', }
            form1 = TenantLogsForm(data1)

            print(form1.errors)
            if form1.is_valid():
                form1.save()
            else:
                messages.error(request, "Tenant Log failed.")

            messages.success(request, 'Repair Request #' + rid + ' Resheduled.')
            return redirect('repair_track')

        elif request.POST.get("form_type") == 'resolvedform':
            rid = request.POST.get('id')

            Repair.objects.filter(id=rid).update(status='Resolved', isactive='', )

            date_time = datetime.now()
            activity = "Repair"
            action = "Repair Request #" + str(rid) + " Resolved."

            data1 = {'date_time': date_time, 'tenant': tid, 'activity': activity, 'action': action,
                     'is_active': 'True', }
            form1 = TenantLogsForm(data1)

            print(form1.errors)
            if form1.is_valid():
                form1.save()
            else:
                messages.error(request, "Tenant Log failed.")

            messages.success(request, 'Repair Request #' + rid + ' Resolved.')
            return redirect('repair_track')

    context = {'repair': repair}
    return render(request, 'tenant/tenant_repair_track.html', context)


def report_add(request):
    form = ReportForm(initial={'status': 'Pending', 'date_issued': datetime.now(), 'isactive': 'True'})

    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        tenant = request.user.tenant.id
        tenant_id = Tenant.objects.get(id=tenant)
        print(form.errors)
        if form.is_valid():
            comp = form.save(commit=False)
            comp.tenant = tenant_id
            comp.save()
            roid = comp.id

            date_time = datetime.now()
            tenantuser = request.user.tenant.id
            activity = "Report"
            action = "Submitted Report #" + str(roid)

            data1 = {'date_time': date_time, 'tenant': tenantuser, 'activity': activity, 'action': action,
                     'is_active': 'True', }
            form1 = TenantLogsForm(data1)

            print(form1.errors)
            if form1.is_valid():
                form1.save()
            else:
                messages.error(request, "Tenant Log failed.")

            messages.success(request, 'Report successfully submitted.')
            return redirect('report_tickets')
        else:
            messages.error(request, 'Report submission failed.')
            return redirect('report_add')

    context = {'form': form}
    return render(request, 'tenant/tenant_report_add.html', context)


def report_tickets(request):
    tid = request.user.tenant.id
    report = Report.objects.filter(tenant=tid)

    if request.method == 'POST':
        rid = request.POST.get('id')

        Report.objects.filter(id=rid).update(status='Resolved', isactive='', )

        date_time = datetime.now()
        activity = "Report"
        action = "Report #" + str(rid) + " Resolved."

        data1 = {'date_time': date_time, 'tenant': tid, 'activity': activity, 'action': action,
                 'is_active': 'True', }
        form1 = TenantLogsForm(data1)

        print(form1.errors)
        if form1.is_valid():
            form1.save()
        else:
            messages.error(request, "Tenant Log failed.")

        messages.success(request, 'Report #' + rid + ' Resolved.')
        return redirect('report_tickets')

    context = {'report': report}
    return render(request, 'tenant/tenant_report_tickets.html', context)


def settings(request):
    # Custom Form
    colorform = CustomForm(initial={'isactive': 'True'})
    cid = AccountCustomization.objects.get(pk=request.user.accountcustomization.id)

    # Tenant Form
    tenantuserform = request.user.tenant
    dob1 = request.user.tenant.dateofbirth
    dob = dob1.strftime("%Y-%m-%d")
    form1 = TenantForm(instance=tenantuserform)

    # Account Form
    form2 = AccountForm(instance=request.user)

    # Password Form
    form3 = PasswordChangeForm(user=request.user)

    # Log Form
    date_time = datetime.now()
    tenantuser = request.user.tenant.id

    if request.method == 'POST':
        # Custom Save
        if request.POST.get("form_type") == 'customform':
            if AccountCustomization.objects.filter(account_id=request.user.id).exists():
                colorform = CustomForm(request.POST, instance=cid)
                print(colorform.errors)
                if colorform.is_valid():
                    selected = request.POST.get('color_scheme')
                    colorform.save()

                    activity = "Customization"
                    action = "Color Updated to " + selected

                    data4 = {'date_time': date_time, 'tenant': tenantuser, 'activity': activity, 'action': action,
                             'is_active': 'True', }
                    form4 = TenantLogsForm(data4)

                    print(form4.errors)
                    if form4.is_valid():
                        form4.save()
                    else:
                        messages.error(request, "Tenant Log failed.")

                    messages.success(request, 'Display color successfully updated.')
                    return redirect('settings')
                else:
                    messages.error(request, 'Display color update failed.')
                    return redirect('settings')
            else:
                colorform = CustomForm(request.POST)
                if colorform.is_valid():
                    selected = request.POST.get('color_scheme')
                    colorform.save()

                    activity = "Customization"
                    action = "Color Updated to " + selected

                    data4 = {'date_time': date_time, 'tenant': tenantuser, 'activity': activity, 'action': action,
                             'is_active': 'True', }
                    form4 = TenantLogsForm(data4)

                    print(form4.errors)
                    if form4.is_valid():
                        form4.save()
                    else:
                        messages.error(request, "Tenant Log failed.")

                    messages.success(request, 'Display color successfully added.')
                    return redirect('settings')
                else:
                    messages.error(request, 'Display color add failed.')
                    return redirect('settings')

        # Tenant Save
        elif request.POST.get("form_type") == 'tenantform':
            form1 = TenantForm(request.POST, request.FILES, instance=tenantuserform)
            print(form1.errors)
            if form1.is_valid():
                form1.save()

                activity = "Profile"
                action = "Profile Information Updated"

                data4 = {'date_time': date_time, 'tenant': tenantuser, 'activity': activity, 'action': action,
                         'is_active': 'True', }
                form4 = TenantLogsForm(data4)

                print(form4.errors)
                if form4.is_valid():
                    form4.save()
                else:
                    messages.error(request, "Tenant Log failed.")

                messages.success(request, 'Tenant information successfully updated.')
                return redirect('profile')
            else:
                messages.error(request, 'Tenant information update failed.')
                return redirect('settings')

        # Account Save
        elif request.POST.get("form_type") == 'accountform':
            form2 = AccountForm(request.POST, instance=request.user)
            print(form2.errors)
            if form2.is_valid():
                form2.save()

                activity = "Account"
                action = "Account Information Updated"

                data4 = {'date_time': date_time, 'tenant': tenantuser, 'activity': activity, 'action': action,
                         'is_active': 'True', }
                form4 = TenantLogsForm(data4)

                print(form4.errors)
                if form4.is_valid():
                    form4.save()
                else:
                    messages.error(request, "Tenant Log failed.")

                messages.success(request, 'Account information successfully updated.')
                return redirect('settings')
            else:
                messages.error(request, 'Account information update failed.')
                return redirect('settings')

        # Password Save
        elif request.POST.get("form_type") == 'passwordform':
            form3 = PasswordChangeForm(data=request.POST, user=request.user)
            print(form3.errors)
            if form3.is_valid():
                form3.save()

                activity = "Password"
                action = "Password Updated"

                data4 = {'date_time': date_time, 'tenant': tenantuser, 'activity': activity, 'action': action,
                         'is_active': 'True', }
                form4 = TenantLogsForm(data4)

                print(form4.errors)
                if form4.is_valid():
                    form4.save()
                else:
                    messages.error(request, "Tenant Log failed.")

                messages.success(request, 'Account password successfully updated. Please login with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Account password update failed.')
                return redirect('settings')

    context = {'form': colorform, 'form1': form1, 'form2': form2, 'form3': form3, 'dob': dob}
    return render(request, 'tenant/tenant_settings.html', context)


def visitor(request):
    form = VisitorForm(
        initial={'status': 'Pending', 'date_issued': datetime.now(), 'reason': 'None', 'isactive': 'True'})

    if request.method == 'POST':
        form = VisitorForm(request.POST)
        tenant = request.user.tenant.id
        tenant_id = Tenant.objects.get(id=tenant)
        print(form.errors)
        if form.is_valid():
            comp = form.save(commit=False)
            comp.tenant = tenant_id
            comp.save()
            vrid = comp.id

            date_time = datetime.now()
            tenantuser = request.user.tenant.id
            activity = "Visitor"
            action = "Submitted Visitor Request #" + str(vrid)

            data1 = {'date_time': date_time, 'tenant': tenantuser, 'activity': activity, 'action': action,
                     'is_active': 'True', }
            form1 = TenantLogsForm(data1)

            print(form1.errors)
            if form1.is_valid():
                form1.save()
            else:
                messages.error(request, "Tenant Log failed.")

            messages.success(request, 'Visitor Request successfully submitted.')
            return redirect('visitor_history')
        else:
            messages.error(request, 'Visitor Request submission failed.')
            return redirect('visitor')

    context = {'form': form}
    return render(request, 'tenant/tenant_visitor.html', context)


def visitor_history(request):
    tid = request.user.tenant.id
    visitors = Visitor.objects.filter(tenant=tid)

    if request.method == 'POST':
        vid = request.POST.get('id')

        Visitor.objects.filter(id=vid).update(status='Cancelled', isactive='', )

        date_time = datetime.now()
        activity = "Visitor"
        action = "Cancelled Visitor Request #" + str(vid)

        data1 = {'date_time': date_time, 'tenant': tid, 'activity': activity, 'action': action,
                 'is_active': 'True', }
        form1 = TenantLogsForm(data1)

        print(form1.errors)
        if form1.is_valid():
            form1.save()
        else:
            messages.error(request, "Tenant Log failed.")

        messages.success(request, 'Visitor Request #' + vid + ' Cancelled.')
        return redirect('visitor_history')

    context = {'visitor': visitors}
    return render(request, 'tenant/tenant_visitor_history.html', context)


# admin
def report(request):
    # visitors
    vctr = Visitor.objects.count()
    v1 = Visitor.objects.filter(purpose='Lounge').count()
    v2 = Visitor.objects.filter(purpose='Stay').count()
    v3 = Visitor.objects.filter(purpose='Vacation').count()
    v4 = Visitor.objects.filter(purpose='Refuge').count()
    v5 = Visitor.objects.filter(purpose='Meeting').count()
    v6 = Visitor.objects.filter(purpose='Event').count()
    v7 = Visitor.objects.filter(purpose='User').count()
    v8 = vctr - (v1 + v2 + v3 + v4 + v5 + v6 + v7)

    vavg = v1 + v2 + v3 + v4 + v5 + v6 + v7 + v8
    vfloat = Visitor.objects.order_by('purpose').values('purpose').annotate(
        count=Cast(((Count('purpose') / 0.1) / vavg) / 0.1, FloatField())).order_by('-count')

    # report
    rectr = Report.objects.count()
    re1 = Report.objects.filter(category='Payment').count()
    re2 = Report.objects.filter(category='Facility').count()
    re3 = Report.objects.filter(category='Repair').count()
    re4 = Report.objects.filter(category='Neighbour').count()
    re5 = Report.objects.filter(category='Staff').count()
    re6 = Report.objects.filter(category='Noise').count()
    re7 = Report.objects.filter(category='Pets').count()
    re8 = Report.objects.filter(category='Rules').count()
    re9 = Report.objects.filter(category='Website').count()
    re0 = rectr - (re1 + re2 + re3 + re4 + re5 + re6 + re7 + re8 + re9)

    renames = Report.objects.filter(isactive='True').exclude(staff__isnull=True)
    renames2 = Report.objects.filter(isactive='True').exclude(neighbour__isnull=True)

    reavg = re1 + re2 + re3 + re4 + re5 + re6 + re7 + re8 + re9 + re0
    refloat = Report.objects.order_by('category').values('category').annotate(
        count=Cast(((Count('category') / 0.1) / reavg) / 0.1, FloatField())).order_by('-count')

    # repair
    ractr = Repair.objects.count()
    ra1 = Repair.objects.filter(category='Foundation').count()
    ra2 = Repair.objects.filter(category='Drainage').count()
    ra3 = Repair.objects.filter(category='Plumbing').count()
    ra4 = Repair.objects.filter(category='Electrical').count()
    ra5 = ractr - (ra1 + ra2 + ra3 + ra4)

    raavg = ra1 + ra2 + ra3 + ra4 + ra5
    rafloat = Repair.objects.order_by('category').values('category').annotate(
        count=Cast(((Count('category') / 0.1) / raavg) / 0.1, FloatField())).order_by('-count')

    # login
    lnctr = LogTenant.objects.filter(action='Logged In').count()
    ln1 = LogTenant.objects.filter(action='Logged In', date_time__month=1).count()
    ln2 = LogTenant.objects.filter(action='Logged In', date_time__month=2).count()
    ln3 = LogTenant.objects.filter(action='Logged In', date_time__month=3).count()
    ln4 = LogTenant.objects.filter(action='Logged In', date_time__month=4).count()
    ln5 = LogTenant.objects.filter(action='Logged In', date_time__month=5).count()
    ln6 = LogTenant.objects.filter(action='Logged In', date_time__month=6).count()
    ln7 = LogTenant.objects.filter(action='Logged In', date_time__month=7).count()
    ln8 = LogTenant.objects.filter(action='Logged In', date_time__month=8).count()
    ln9 = LogTenant.objects.filter(action='Logged In', date_time__month=9).count()
    ln10 = LogTenant.objects.filter(action='Logged In', date_time__month=10).count()
    ln11 = LogTenant.objects.filter(action='Logged In', date_time__month=11).count()
    ln12 = LogTenant.objects.filter(action='Logged In', date_time__month=12).count()

    # billings
    bctr = Billing.objects.filter(status='Paid').count()
    b1 = Billing.objects.filter(status='Paid', date_issued__month=1).count()
    b2 = Billing.objects.filter(status='Paid', date_issued__month=2).count()
    b3 = Billing.objects.filter(status='Paid', date_issued__month=3).count()
    b4 = Billing.objects.filter(status='Paid', date_issued__month=4).count()
    b5 = Billing.objects.filter(status='Paid', date_issued__month=5).count()
    b6 = Billing.objects.filter(status='Paid', date_issued__month=6).count()
    b7 = Billing.objects.filter(status='Paid', date_issued__month=7).count()
    b8 = Billing.objects.filter(status='Paid', date_issued__month=8).count()
    b9 = Billing.objects.filter(status='Paid', date_issued__month=9).count()
    b10 = Billing.objects.filter(status='Paid', date_issued__month=10).count()
    b11 = Billing.objects.filter(status='Paid', date_issued__month=11).count()
    b12 = Billing.objects.filter(status='Paid', date_issued__month=12).count()

    bdctr = Billing.objects.filter(status='Pending').count()
    bd1 = Billing.objects.filter(status='Pending', date_issued__month=1).count()
    bd2 = Billing.objects.filter(status='Pending', date_issued__month=2).count()
    bd3 = Billing.objects.filter(status='Pending', date_issued__month=3).count()
    bd4 = Billing.objects.filter(status='Pending', date_issued__month=4).count()
    bd5 = Billing.objects.filter(status='Pending', date_issued__month=5).count()
    bd6 = Billing.objects.filter(status='Pending', date_issued__month=6).count()
    bd7 = Billing.objects.filter(status='Pending', date_issued__month=7).count()
    bd8 = Billing.objects.filter(status='Pending', date_issued__month=8).count()
    bd9 = Billing.objects.filter(status='Pending', date_issued__month=9).count()
    bd10 = Billing.objects.filter(status='Pending', date_issued__month=10).count()
    bd11 = Billing.objects.filter(status='Pending', date_issued__month=11).count()
    bd12 = Billing.objects.filter(status='Pending', date_issued__month=12).count()

    boctr = Billing.objects.filter(status='Overdue').count()
    bo1 = Billing.objects.filter(status='Overdue', date_issued__month=1).count()
    bo2 = Billing.objects.filter(status='Overdue', date_issued__month=2).count()
    bo3 = Billing.objects.filter(status='Overdue', date_issued__month=3).count()
    bo4 = Billing.objects.filter(status='Overdue', date_issued__month=4).count()
    bo5 = Billing.objects.filter(status='Overdue', date_issued__month=5).count()
    bo6 = Billing.objects.filter(status='Overdue', date_issued__month=6).count()
    bo7 = Billing.objects.filter(status='Overdue', date_issued__month=7).count()
    bo8 = Billing.objects.filter(status='Overdue', date_issued__month=8).count()
    bo9 = Billing.objects.filter(status='Overdue', date_issued__month=9).count()
    bo10 = Billing.objects.filter(status='Overdue', date_issued__month=10).count()
    bo11 = Billing.objects.filter(status='Overdue', date_issued__month=11).count()
    bo12 = Billing.objects.filter(status='Overdue', date_issued__month=12).count()

    context = {
        'vavg': vavg, "vfloat": vfloat,
        'v1': v1, 'v2': v2, 'v3': v3, 'v4': v4, 'v5': v5, 'v6': v6, 'v7': v7, 'v8': v8,
        'reavg': reavg, "refloat": refloat, "renames": renames, "renames2": renames2,
        're1': re1, 're2': re2, 're3': re3, 're4': re4, 're5': re5, 're6': re6, 're7': re7, 're8': re8, 're9': re9,
        're0': re0,
        'raavg': raavg, "rafloat": rafloat,
        'ra1': ra1, 'ra2': ra2, 'ra3': ra3, 'ra4': ra4, 'ra5': ra5,
        'lnctr': lnctr,
        'ln1': ln1, 'ln2': ln2, 'ln3': ln3, 'ln4': ln4, 'ln5': ln5, 'ln6': ln6, 'ln7': ln7, 'ln8': ln8, 'ln9': ln9,
        'ln10': ln10, 'ln11': ln11, 'ln12': ln12,
        'bctr': bctr,
        'b1': b1, 'b2': b2, 'b3': b3, 'b4': b4, 'b5': b5, 'b6': b6, 'b7': b7, 'b8': b8, 'b9': b9, 'b10': b10,
        'b11': b11, 'b12': b12,
        'bdctr': bdctr,
        'bd1': bd1, 'bd2': bd2, 'bd3': bd3, 'bd4': bd4, 'bd5': bd5, 'bd6': bd6, 'bd7': bd7, 'bd8': bd8, 'bd9': bd9,
        'bd10': bd10, 'bd11': bd11, 'bd12': bd12,
        'boctr': bdctr,
        'bo1': bo1, 'bo2': bo2, 'bo3': bo3, 'bo4': bo4, 'bo5': bo5, 'bo6': bo6, 'bo7': bo7, 'bo8': bo8, 'bo9': bo9,
        'bo10': bo10, 'bo11': bo11, 'bo12': bo12,

    }
    return render(request, 'analytics/report.html', context)


def attrition(request):
    ct_report = 0
    ct_overdues = 0
    ct_score = 0.00
    ct_name = ""

    # reports
    tenantctr = Tenant.objects.all().count()
    if AttritionPrediction.objects.all():
        attritctr = AttritionPrediction.objects.all().count()
    else:
        attritctr = 1
    noattrit_tot = tenantctr - attritctr

    if TenantContract.objects.all():
        contctr = TenantContract.objects.all().count()
    else:
        contctr = 1
    nocont_tot = tenantctr - contctr

    last_month_filter = datetime.today() - timedelta(days=get_lapse())
    updatetot = AttritionPrediction.objects.filter(datetime__lte=last_month_filter).count()

    scores = 0
    for each in AttritionPrediction.objects.all():
        scores = scores + each.attrition_probability
    scoreavg = float(scores) / float(attritctr)

    hightot = AttritionPrediction.objects.filter(attrition_probability__gte=60).count()

    # form
    tenants = Tenant.objects.all().order_by('unit__floor','unit__room')
    tenants_attr = AttritionPrediction.objects.filter(attrition_probability__gte=60).order_by('-attrition_probability')
    contract = TenantContract.objects.all()
    attrit = AttritionPrediction.objects.all()
    form = ContractForm()

    # CREATE CONTRACT
    if request.method == 'POST':
        if request.POST.get("form_type") == 'addcontract':
            tenant = request.POST.get('tenant')
            tenant_id = Tenant.objects.get(id=tenant)

            rent = request.POST.get('rent')
            late_collection = request.POST.get('late_collection')
            grace_period = request.POST.get('grace_period')
            legal_rent = request.POST.get('legal_rent')
            deposit = request.POST.get('deposit')
            roommates = request.POST.get('roommates')
            epay = request.POST.get('epay')

            date_time = datetime.now()
            movedate = request.POST.get('move_date')
            mdate = datetime.strptime(movedate, '%Y-%m-%d')
            m = relativedelta(date_time, mdate)
            # latecoll = float(rent) * 0.05

            data = {'move_date': mdate, 'tenant': tenant, 'rent': rent, 'late_collection': late_collection, 'grace_period': grace_period,
                    'legal_rent': legal_rent, 'deposit': deposit, 'months_occupied': m.months + (12*m.years), 'roommates': roommates, 'epay': epay,
                    'confirmation': 'None'}
            form = ContractForm(data)

            print(form.errors)
            if form.is_valid():
                comp = form.save(commit=False)
                comp.tenant = tenant_id
                comp.save()

                messages.success(request, 'Tenant Contract create successful.')
                return redirect('attrition')
            else:
                messages.error(request, 'Tenant Contract create failed.')
                return redirect('attrition')

    # UPDATE CONTRACT
        elif request.POST.get("form_type") == 'updatecontract':
            tcid = request.POST.get('id')
            tenant = request.POST.get('tenant')
            rent = request.POST.get('rent')
            late_collection = request.POST.get('late_collection')
            grace_period = request.POST.get('grace_period')
            legal_rent = request.POST.get('legal_rent')
            deposit = request.POST.get('deposit')
            roommates = request.POST.get('roommates')
            epay = request.POST.get('epay')

            date_time = datetime.now()
            movedate = TenantContract.objects.get(id=tcid)
            # mdate = movedate.move_date.strftime(movedate.move_date, '%Y-%m-%d')
            m = relativedelta(date_time, movedate.move_date)

            TenantContract.objects.filter(id=tcid).update(
                tenant=tenant, rent=rent, late_collection=late_collection,
                grace_period=grace_period, legal_rent=legal_rent, deposit=deposit,
                roommates=roommates, epay=epay, months_occupied= m.months + (12*m.years),
            )

            messages.success(request, 'Tenant Contract update successful.')
            return redirect('attrition')

    # CREATE CHURN
        elif request.POST.get("form_type") == 'churnprediction':
            tenant = request.POST.get('churn_tenant')
            contract = TenantContract.objects.get(tenant=tenant)
            # rectr = Report.objects.filter(tenant=tenant).count()
            # blctr = Billing.objects.filter(tenant=tenant, status='Overdue').count()
            # retot = float(rectr) * 0.5
            blctr = 0
            retot = 0

            date_time = datetime.now()

            var1 = contract.rent
            var2 = contract.late_collection
            var3 = contract.grace_period
            var4 = contract.legal_rent
            var5 = contract.deposit
            var6 = contract.months_occupied
            var7 = contract.roommates
            var8 = contract.epay

            predicts = [[var1, var2, var3, var4, var5, var6, var7, var8]]
            data = pd.DataFrame(predicts)
            predicts2 = model2.predict(data)

            predicts3 = predicts2 * 100
            finalna = predicts3.round(2)
            lst_str = str(finalna)[1:-1]
            fattr = float(lst_str) + retot + float(blctr)

            data = {'tenant': tenant, 'attrition_probability': fattr, 'is_active': 'True', }
            form = AttritionForm(data)

            print(form.errors)

            if form.is_valid():
                ct_report = Report.objects.filter(tenant=tenant).count()
                ct_overdues = Billing.objects.filter(tenant=tenant, status='Overdue').count()
                ct_name = contract.tenant.account.first_name + " " + contract.tenant.account.last_name
                ct_score = fattr

                form.save()
                messages.info(request, "Attrition Prediction Success.", extra_tags='one_attrition')
            else:
                messages.error(request, "Attrition Prediction Failed.")
                return redirect('attrition')

    # UPDATE CHURN
        elif request.POST.get("form_type") == 'updatechurnprediction':
            cid = request.POST.get('churn_id')
            tenant = request.POST.get('churn_tenant')
            contract = TenantContract.objects.get(tenant=tenant)
            # rectr = Report.objects.filter(tenant=tenant).count()
            # blctr = Billing.objects.filter(tenant=tenant, status='Overdue').count()
            # retot = float(rectr) * 0.5
            blctr = 0
            retot = 0

            var1 = contract.rent
            var2 = contract.late_collection
            var3 = contract.grace_period
            var4 = contract.legal_rent
            var5 = contract.deposit
            var6 = contract.months_occupied
            var7 = contract.roommates
            var8 = contract.epay

            predicts = [[var1, var2, var3, var4, var5, var6, var7, var8]]
            data = pd.DataFrame(predicts)
            predicts2 = model2.predict(data)

            predicts3 = predicts2 * 100
            finalna = predicts3.round(2)
            lst_str = str(finalna)[1:-1]
            fattr = float(lst_str) + float(blctr) + retot

            date_time = datetime.now()

            ct_report = Report.objects.filter(tenant=tenant).count()
            ct_overdues = Billing.objects.filter(tenant=tenant, status='Overdue').count()
            ct_name = contract.tenant.account.first_name + " " + contract.tenant.account.last_name
            ct_score = fattr
            AttritionPrediction.objects.filter(id=cid).update(datetime=date_time, attrition_probability=fattr,)
            messages.info(request, "Attrition Prediction Update Success.", extra_tags='one_attrition')

    # CHURN ALL
        elif request.POST.get("form_type") == 'confirm':
            tenantlist = TenantContract.objects.all()

            for each in tenantlist:
                tenant = each.tenant
                cid = AttritionPrediction.objects.filter(tenant=tenant)
                # rectr = Report.objects.filter(tenant=tenant).count()
                # blctr = Billing.objects.filter(tenant=tenant, status='Overdue').count()
                # retot = float(rectr) * 0.5
                blctr = 0
                retot = 0

                var1 = each.rent
                var2 = each.late_collection
                var3 = each.grace_period
                var4 = each.legal_rent
                var5 = each.deposit
                var6 = each.months_occupied
                var7 = each.roommates
                var8 = each.epay

                predicts = [[var1, var2, var3, var4, var5, var6, var7, var8]]
                data = pd.DataFrame(predicts)
                predicts2 = model2.predict(data)

                predicts3 = predicts2 * 100
                finalna = predicts3.round(2)
                lst_str = str(finalna)[1:-1]
                fattr = float(lst_str) + float(blctr) + retot

                date_time = datetime.now()

                if cid:
                    attrid = AttritionPrediction.objects.get(tenant=tenant)
                    AttritionPrediction.objects.filter(id=attrid.id).update(datetime=date_time, attrition_probability=fattr, )
                else:
                    data = {'tenant': tenant, 'attrition_probability': fattr, 'is_active': 'True', }
                    form = AttritionForm(data)

                    print(form.errors)
                    if form.is_valid():
                        form.save()
                        return redirect('attrition')
                    else:
                        return redirect('attrition')


            messages.info(request, 'Attrition of all tenants successfully processed.', extra_tags='all_attrition')
            return redirect('attrition')

    context = {'tenants': tenants, 'tenants_attr':tenants_attr, 'contract': contract, 'attrit': attrit, 'form': form, 'nocont_tot':nocont_tot,
               'tenantctr': tenantctr, 'noattrit_tot': noattrit_tot, 'updatetot': updatetot, 'scoreavg': scoreavg,  'hightot': hightot,
               'ct_report': ct_report, 'ct_overdues': ct_overdues, 'ct_name': ct_name, 'ct_score': ct_score,}
    return render(request, 'analytics/attrition.html', context)
