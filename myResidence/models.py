# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove ` ` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User, Group
import os
from django.core.exceptions import ValidationError
from uuid import uuid4
from django.contrib import admin, messages
from django.db.models import Q

# image upload


def admin_upload(instance, filename):
    upload_to = 'static/uploaded/profile/admin/'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.account.username + "_" + str(instance.pk), ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


def tenant_upload(instance, filename):
    upload_to = 'static/uploaded/profile/tenant/'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.account.username + "_" + str(instance.pk), ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


def reg_upload(instance, filename):
    upload_to = 'static/uploaded/profile/registration/'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format("regis_" + instance.username + "_" + str(instance.pk), ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


def repair_upload(instance, filename):
    upload_to = 'static/uploaded/tickets/repair/'
    ext = filename.split('.')[-1]

    filename = '{}.{}'.format( "repair_" + instance.tenant.account.username + "_" + uuid4().hex , ext)

    # return the whole path to the file
    return os.path.join(upload_to, filename)


def report_upload(instance, filename):
    upload_to = 'static/uploaded/tickets/report/'
    ext = filename.split('.')[-1]

    filename = '{}.{}'.format( "report_" + instance.tenant.account.username + "_" + uuid4().hex , ext)

    # return the whole path to the file
    return os.path.join(upload_to, filename)


def proof_upload(instance, filename):
    upload_to = 'static/uploaded/proofpayments/'
    ext = filename.split('.')[-1]

    filename = '{}.{}'.format( "billing" + str(instance.billing.id) + "_" + instance.billing.tenant.account.username, ext)

    # return the whole path to the file
    return os.path.join(upload_to, filename)


def news_upload(instance, filename):
    upload_to = 'static/uploaded/news/'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format("news_" + str(instance.pk), ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


def ad_upload(instance, filename):
    upload_to = 'static/uploaded/news/'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format("advertisement_" + str(instance.pk), ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


# TPS Models
class AccountCustomization(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE)
    color_scheme = models.CharField(max_length=255, blank=True, null=True)
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.account.first_name + " " + self.account.last_name

    class Meta:
         
        db_table = 'account_customize'


class Admin(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.CharField(max_length=100)
    dateofbirth = models.DateField()
    image = models.ImageField(null=True, blank=True, upload_to=admin_upload, default="static/uploaded/profile/default.png")
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
            return self.account.first_name + " " + self.account.last_name

    class Meta:
         
        db_table = 'admin'


class TenantUnit(models.Model):
    floor = models.IntegerField()
    room = models.CharField(max_length=11)
    tenant_num = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.floor) + str(self.room)

    class Meta:
         
        db_table = 'tenant_unit'


class Tenant(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE)
    unit = models.ForeignKey(TenantUnit, on_delete=models.CASCADE)
    contact = models.CharField(max_length=100)
    work_address = models.CharField(max_length=100)
    dateofbirth = models.DateField()
    image = models.ImageField(null=True, blank=True, upload_to=tenant_upload, default="static/uploaded/profile/default.png")
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE, default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.account.first_name + " " + self.account.last_name

    class Meta:
         
        db_table = 'tenants'


class TenantRegistration(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    date_joined = models.DateField(auto_now_add=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    unit = models.ForeignKey(TenantUnit, on_delete=models.CASCADE)
    contact = models.CharField(max_length=100)
    work_address = models.CharField(max_length=255, blank=True, null=True)
    dateofbirth = models.DateField()
    image = models.ImageField(null=True, blank=True, upload_to=reg_upload, default="static/uploaded/profile/default.png")
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    )
    status = models.CharField(max_length=100, choices=STATUS, default=STATUS[0][0])
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return str(self.id)

    class Meta:
         
        db_table = 'tenant_registration'


class BillingType(models.Model):
    billing_code = models.CharField(max_length=50)
    billing_name = models.CharField(max_length=100)
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.billing_name

    class Meta:
         
        db_table = 'billing_type'


class Billing(models.Model):
    unit = models.ForeignKey(TenantUnit, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    date_issued = models.DateField(auto_now_add=True)
    billing_type = models.ForeignKey(BillingType,  on_delete=models.CASCADE)
    billing_fee = models.FloatField()
    due_date = models.DateField()
    STATUS = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue')
    )
    status = models.CharField(max_length=100, choices=STATUS, default=STATUS[0][0])
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    is_late = models.CharField(max_length=100)
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.tenant.account.first_name + " " + self.tenant.account.last_name + " | " + self.billing_type.billing_code

    def save(self, *args, **kwargs):
        if self.tenant is not None and self.unit is None:
            bcount = Billing.objects.all().count()
            if bcount == 0:
                lastid = 1
            else:
                lastid = Billing.objects.latest('id')
            idcount = 1

            if bcount == 0:
                self.id = lastid
            else:
                self.id = lastid.id + idcount
            self.date_issued = datetime.now()
            self.isactive = 'True'
            self.status = 'Pending'
            self.billing_fee = self.billing_fee
            self.tenant = self.tenant
            super().save(*args, **kwargs)

            from .forms import AdminLogsForm
            date_time = datetime.now()
            tenant = self.tenant
            activity = "Billing"
            action = "Billing #" + str(self.id)

            data = {'date_time': date_time, 'tenant': tenant, 'activity': activity, 'action': action, 'is_active': 'True', }
            form = AdminLogsForm(data)

            print(form.errors)
            if form.is_valid():
                form.save()

        elif self.tenant is None and self.unit is None:
            pass

        elif self.tenant is None and self.unit is not None:
            tenants = Tenant.objects.filter(unit=self.unit.id, isactive='True')
            bcount = Billing.objects.all().count()
            if bcount == 0:
                lastid = 1
            else:
                lastid = Billing.objects.latest('id')
            ct = tenants.count()
            billing_divide = self.billing_fee / ct
            idcount = 1

            for tenantunits in tenants:
                if bcount == 0:
                    self.id = lastid
                else:
                    self.id = lastid.id + idcount
                self.date_issued = datetime.now()
                self.isactive = 'True'
                self.status = 'Pending'
                self.billing_fee = billing_divide
                self.tenant = tenantunits
                super().save(*args, **kwargs)

                idcount = idcount + 1

                from myResidence.forms import AdminLogsForm
                date_time = datetime.now()
                tenant = self.tenant
                activity = "Billing"
                action = "Billing #" + str(self.id)

                data = {'date_time': date_time, 'tenant': tenant, 'activity': activity, 'action': action,
                        'is_active': 'True', }
                form = AdminLogsForm(data)

                print(form.errors)
                if form.is_valid():
                    form.save()


    class Meta:
         
        ordering = ['-date_issued']
        db_table = 'billings'


class ProofOfPayment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    date_submitted = models.DateField(auto_now_add=True)
    image = models.ImageField(null=True, blank=True, upload_to=proof_upload)
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    )
    status = models.CharField(max_length=100, choices=STATUS, default=STATUS[0][0])
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.billing.billing_type.billing_name

    class Meta:
         
        db_table = 'proof_payment'


class LogAdmin(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    activity = models.CharField(max_length=100)
    action = models.CharField(max_length=255)
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.admin.account.first_name + " " + self.admin.account.last_name

    class Meta:
         
        db_table = 'log_admin'


class LogTenant(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    activity = models.CharField(max_length=100)
    action = models.CharField(max_length=255)
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.tenant.account.first_name + " " + self.tenant.account.last_name

    class Meta:
         
        db_table = 'log_tenants'


class Repair(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    date_issued = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=100)
    details = models.TextField()
    date_available = models.DateField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to=repair_upload)
    STATUS = (
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Cancelled', 'Cancelled'),
        ('Date_Unavailable', 'Date Unavailable'),
        ('Scheduled', 'Scheduled'),
    )
    status = models.CharField(max_length=255, choices=STATUS, default=STATUS[0][0])
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.tenant.account.first_name + " " + self.tenant.account.last_name + " REPAIR TICKET #" + str(self.id)

    class Meta:
         
        ordering = ['-date_issued']
        db_table = 'repair'


class Report(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    date_issued = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=100)
    details = models.TextField()
    neighbour = models.CharField(max_length=100, blank=True, null=True)
    staff = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to=report_upload)
    STATUS = (
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
    )
    status = models.CharField(max_length=255, choices=STATUS, default=STATUS[0][0])
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.tenant.account.first_name + " " + self.tenant.account.last_name + " REPORT TICKET #" + str(self.id)

    class Meta:
         
        ordering = ['-date_issued']
        db_table = 'report'


class Visitor(models.Model):
    date_issued = models.DateField(auto_now_add=True)
    purpose = models.CharField(max_length=100)  # , choices=PURPOSE
    visitor_count = models.IntegerField()
    visitor_names = models.CharField(max_length=255)
    visit_date = models.DateField()
    duration = models.CharField(max_length=100)
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled')
    )
    status = models.CharField(max_length=100, choices=STATUS, default=STATUS[0][0])
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.tenant.account.first_name + " " + self.tenant.account.last_name + " VISITOR REQUEST #" + str(self.id)

    class Meta:
         
        ordering = ['-date_issued']
        db_table = 'visitors'


class TermsAndCondition(models.Model):
    date_updated = models.DateField(auto_now_add=True)
    tnc_content = models.TextField()

    def __str__(self):
        return "myResidence Terms and Conditions"

    class Meta:
         
        db_table = 'cms_tnc'


class TenantAnnouncement(models.Model):
    main_news = models.ForeignKey('AnnouncementNew', on_delete=models.CASCADE, related_name='mainnews')
    sub_news = models.ForeignKey('AnnouncementNew', on_delete=models.CASCADE, related_name='subnews')
    survey_link = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to=ad_upload)
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return "myResidence Announcements"

    class Meta:
         
        db_table = 'cms_announcements'


class AnnouncementNew(models.Model):
    image = models.ImageField(null=True, blank=True, upload_to=news_upload)
    headline = models.CharField(max_length=255)
    content = models.TextField()
    datepublished = models.DateField()
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.headline

    class Meta:
         
        ordering = ['-datepublished']
        db_table = 'cms_news'


class AttritionPrediction(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    attrition_probability = models.FloatField()
    ACTIVE = (
        ('True', 'True'),
        ('', 'False'),
    )
    isactive = models.CharField(db_column='isActive', max_length=100, null=True, blank=True, choices=ACTIVE,
                                default=ACTIVE[0][0])  # Field name made lowercase.

    def __str__(self):
        return self.tenant.account.first_name + " " + self.tenant.account.last_name

    class Meta:
         
        db_table = 'tenant_attrition'


class TenantContract(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    move_date = models.DateField(blank=True, null=True)
    rent = models.FloatField()
    late_collection = models.FloatField()
    grace_period = models.IntegerField()
    legal_rent = models.FloatField()
    deposit = models.FloatField()
    months_occupied = models.IntegerField()
    roommates = models.IntegerField()
    epay = models.IntegerField()
    confirmation = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
         
        db_table = 'tenant_contract'
