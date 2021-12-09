from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from myResidence.models import *
from myResidence.forms import BillingForm
from datetime import datetime, date, timedelta
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from django.contrib import messages


class MyAdminSite(AdminSite):
    @never_cache
    def index(self, request, extra_context=None):
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

        # ---------------------------------- init functions ---------------------------------- #
        for each in TenantUnit.objects.all():
            tuctr = Tenant.objects.filter(unit__id=each.id).count()
            TenantUnit.objects.filter(id=each.id).update(tenant_num=tuctr)

        # billings overdue
        todate = date.today()
        todate_month = todate.strftime("%B")
        todate1 = todate.strftime("%Y-%m-%d")
        Billing.objects.filter(due_date__lte=todate, status='Pending').update(status='Overdue')

        # visitor request overdue
        Visitor.objects.filter(visit_date__lte=todate, status='Pending').update(status='Rejected', isactive='')

        # repair request overdue
        Repair.objects.filter(date_available__lte=todate, status='Pending').update(status='Date_Unavailable')

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
                if Billing.objects.filter(date_issued__gte=last_month_filter, billing_type__billing_code="RB",
                                          tenant__id=each_t.id):
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
            # else:
            #    contract = TenantContract.objects.filter(tenant__id=each_t.id)
            #
            # must have contract first
            #    if contract:
            #        createrent = Billing.objects.filter(billing_type__billing_code="RB", tenant__id=each_t.id)
            #        tc = TenantContract.objects.get(tenant__id=each_t.id)
            #        d = tc.move_date
            #
            #        if d.day == todate.day and not createrent:
            #            tenant = each_t.id
            #            billing_type = BillingType.objects.get(billing_name="Rent Bill")
            #            billing_fee = tc.rent
            #            due_date = date.today() + relativedelta(months=+1)
            #            due_date1 = due_date.strftime("%Y-%m-%d")

            # data = {'tenant': tenant, 'date_issued': todate1, 'billing_type': billing_type.id, 'is_late': 'No',
            # 'billing_fee': billing_fee, 'due_date': due_date1, 'status': 'Pending', 'is_active': 'True',
            # } form = BillingForm(data)

            #            print(form.errors)
            #            if form.is_valid():
            #                form.save()
            #            else:
            #                messages.error(request, "New Rent Billing save failed.")

        # ---------------------------------- dashboard ---------------------------------- #
        tenantctr = TenantRegistration.objects.all().count()
        receiptctr = ProofOfPayment.objects.filter(status='Pending').count()
        reportctr = Report.objects.filter(status='Pending').count()
        repairctr = Repair.objects.filter(status='Pending').count()
        visitorctr = Visitor.objects.filter(status='Pending').count()

        paidctr = 0.0
        for each in Billing.objects.filter(status='Paid', date_issued__month=todate.month):
            paidctr = paidctr + float(each.billing_fee)

        overduectr = 0.0
        for each in Billing.objects.filter(status='Overdue'):
            overduectr = overduectr + float(each.billing_fee)

        app_list = self.get_app_list(request)

        context = {
            **self.each_context(request),
            'title': self.index_title,
            'subtitle': None,
            'app_list': app_list,
            **(extra_context or {}),
            'tenantctr': tenantctr,
            'receiptctr': receiptctr,
            'reportctr': reportctr,
            'repairctr': repairctr,
            'visitorctr': visitorctr,
            'paidctr': paidctr,
            'overduectr': overduectr,
            'todate_month': todate_month,
        }

        request.current_app = self.name

        return TemplateResponse(request, self.index_template or 'admin/index.html', context)


admin_site = MyAdminSite()