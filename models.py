# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountCustomize(models.Model):
    account = models.ForeignKey('AuthUser', models.DO_NOTHING)
    color_scheme = models.CharField(max_length=255, blank=True, null=True)
    isactive = models.CharField(db_column='isActive', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'account_customize'


class Admin(models.Model):
    account = models.ForeignKey('AuthUser', models.DO_NOTHING)
    contact = models.CharField(max_length=100)
    dateofbirth = models.DateField()
    image = models.TextField(blank=True, null=True)
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'admin'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BillingType(models.Model):
    billing_code = models.CharField(max_length=50)
    billing_name = models.CharField(max_length=100)
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'billing_type'


class Billings(models.Model):
    unit_id = models.BigIntegerField(blank=True, null=True)
    tenant_id = models.BigIntegerField(blank=True, null=True)
    date_issued = models.DateField()
    billing_type = models.ForeignKey(BillingType, models.DO_NOTHING, db_column='billing_type')
    billing_fee = models.FloatField()
    due_date = models.DateField()
    status = models.CharField(max_length=100)
    is_late = models.CharField(max_length=100)
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'billings'


class CmsAnnouncements(models.Model):
    main_news = models.ForeignKey('CmsNews', models.DO_NOTHING, db_column='main_news')
    sub_news = models.ForeignKey('CmsNews', models.DO_NOTHING, db_column='sub_news')
    survey_link = models.TextField()
    image = models.TextField(blank=True, null=True)
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cms_announcements'


class CmsNews(models.Model):
    image = models.TextField(blank=True, null=True)
    headline = models.CharField(max_length=255)
    content = models.TextField()
    datepublished = models.DateField()
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cms_news'


class CmsPayment(models.Model):
    account_name = models.CharField(max_length=200)
    bank = models.CharField(max_length=200)
    account_number = models.CharField(max_length=200)
    contact = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    days_available = models.CharField(max_length=200)
    time_available = models.CharField(max_length=200)
    contact_tel = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'cms_payment'


class CmsTnc(models.Model):
    date_updated = models.DateField()
    tnc_content = models.TextField()

    class Meta:
        managed = False
        db_table = 'cms_tnc'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class LogAdmin(models.Model):
    admin = models.ForeignKey(Admin, models.DO_NOTHING, blank=True, null=True)
    date_time = models.DateTimeField()
    tenant = models.ForeignKey('Tenants', models.DO_NOTHING, blank=True, null=True)
    activity = models.CharField(max_length=100)
    action = models.CharField(max_length=255)
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'log_admin'


class LogTenants(models.Model):
    tenant = models.ForeignKey('Tenants', models.DO_NOTHING)
    date_time = models.DateTimeField()
    activity = models.CharField(max_length=100)
    action = models.CharField(max_length=255)
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'log_tenants'


class ProofPayment(models.Model):
    tenant = models.ForeignKey('Tenants', models.DO_NOTHING, blank=True, null=True)
    date_submitted = models.DateField()
    image = models.TextField()
    status = models.CharField(max_length=100)
    billing = models.ForeignKey(Billings, models.DO_NOTHING)
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'proof_payment'


class Repair(models.Model):
    tenant = models.ForeignKey('Tenants', models.DO_NOTHING)
    date_issued = models.DateField()
    category = models.CharField(max_length=100)
    details = models.TextField()
    date_available = models.DateField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255)
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'repair'


class Report(models.Model):
    tenant = models.ForeignKey('Tenants', models.DO_NOTHING)
    date_issued = models.DateField()
    category = models.CharField(max_length=100)
    details = models.TextField()
    neighbour = models.CharField(max_length=100, blank=True, null=True)
    staff = models.CharField(max_length=100, blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255)
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'report'


class TenantAttrition(models.Model):
    tenant = models.ForeignKey('Tenants', models.DO_NOTHING)
    datetime = models.DateTimeField()
    attrition_probability = models.FloatField()
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tenant_attrition'


class TenantContract(models.Model):
    tenant = models.ForeignKey('Tenants', models.DO_NOTHING)
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
        managed = False
        db_table = 'tenant_contract'


class TenantLease(models.Model):
    tenant = models.ForeignKey('Tenants', models.DO_NOTHING)
    landlord = models.ForeignKey(AuthUser, models.DO_NOTHING)
    lease_address = models.CharField(max_length=255)
    tenant_address = models.CharField(max_length=255)
    tenant_signature = models.TextField(blank=True, null=True)
    ctc_number = models.IntegerField()
    date_signed = models.DateField()

    class Meta:
        managed = False
        db_table = 'tenant_lease'


class TenantRegistration(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    date_joined = models.DateField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    unit = models.ForeignKey('TenantUnit', models.DO_NOTHING, db_column='unit')
    contact = models.CharField(max_length=100)
    work_address = models.CharField(max_length=255, blank=True, null=True)
    dateofbirth = models.DateField()
    image = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100)
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tenant_registration'


class TenantUnit(models.Model):
    floor = models.IntegerField()
    room = models.CharField(max_length=11)
    tenant_num = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tenant_unit'


class Tenants(models.Model):
    account = models.ForeignKey(AuthUser, models.DO_NOTHING)
    unit = models.ForeignKey(TenantUnit, models.DO_NOTHING, db_column='unit')
    contact = models.CharField(max_length=100)
    work_address = models.CharField(max_length=100)
    dateofbirth = models.DateField()
    image = models.TextField(blank=True, null=True)
    isactive = models.CharField(db_column='isActive', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tenants'


class Visitors(models.Model):
    date_issued = models.DateField()
    purpose = models.CharField(max_length=100)
    visitor_count = models.IntegerField()
    visitor_names = models.CharField(max_length=255)
    visit_date = models.DateField()
    duration = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    tenant = models.ForeignKey(Tenants, models.DO_NOTHING)
    reason = models.CharField(max_length=255)
    isactive = models.CharField(db_column='isActive', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'visitors'
