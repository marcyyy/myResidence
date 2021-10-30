from django.contrib import admin, messages
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from myResidence.forms import *
from myResidence.models import *
from import_export.admin import ExportActionMixin
from import_export import resources
from import_export.fields import Field

# run functions
for each in TenantUnit.objects.all():
    tuctr = Tenant.objects.filter(unit__id=each.id).count()
    TenantUnit.objects.filter(id=each.id).update(tenant_num=tuctr)


# ADD ADMIN ACTIONS
@admin.action(description='Mark selected as Approved')
def make_approved(modeladmin, request, queryset):
    queryset.update(status='Approved',isactive='True',)


@admin.action(description='Mark selected as Approved')
def make_approved_false(modeladmin, request, queryset):
    queryset.update(status='Approved',isactive='',)


@admin.action(description='Mark selected as Approved')
def make_approved_proof(modeladmin, request, queryset):
    for obj in queryset:
        Billing.objects.filter(id=obj.billing.id).update(status='Paid', isactive='', )
        ProofOfPayment.objects.filter(id=obj.id).update(status='Approved', isactive='', )


@admin.action(description='Register selected Tenants')
def make_approved_reg(modeladmin, request, queryset):
    for object in queryset:
        # save account
        regid = object.id
        username = object.username
        password = object.password
        is_superuser = 0
        first_name = object.first_name
        last_name = object.last_name
        email = object.email
        is_staff = 0
        is_active = 1
        date_joined = object.date_joined

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name = first_name,
            last_name = last_name,
            is_staff = is_staff,
            is_active = is_active,
            date_joined = date_joined,
            is_superuser = is_superuser
        )

        user.set_password(password)
        user.save()
        response = user.id
        messages.success(request, "Account successfully saved.")

        # save tenant
        account_id = response
        unit = object.unit.id
        tcount = int(object.unit.tenant_num)
        contact = object.contact
        work_address = object.work_address
        dateofbirth = object.dateofbirth
        image = object.image

        data2 = {'account': account_id, 'unit': unit, 'contact': contact, 'work_address': work_address,
                 'dateofbirth': dateofbirth, 'image': image, 'is_active': 'True',}
        form2 = TenantRegForm(data2)

        print(form2.errors)
        if form2.is_valid():
            form2.save()
            TenantRegistration.objects.filter(id=regid).delete()
            messages.success(request, "Tenant Information successfully saved.")
        else:
            messages.error(request, "Tenant Information save failed.")

        TenantUnit.objects.filter(id=unit).update(tenant_num= tcount + 1)

        #save
        color_scheme = '#4facfe'

        data3 = {'account': account_id, 'color_scheme': color_scheme, 'is_active': 'True', }
        form3 = CustomForm(data3)

        print(form3.errors)
        if form3.is_valid():
            form3.save()
            messages.success(request, "Account customization successfully saved.")
        else:
            messages.error(request, "Account customization save failed.")


@admin.action(description='Mark selected as Rejected')
def make_rejected(modeladmin, request, queryset):
    queryset.update(status='Rejected', isactive='',)


@admin.action(description='Mark selected as Rejected')
def make_rejected_reason(modeladmin, request, queryset):
    queryset.update(status='Rejected', isactive='',)


@admin.action(description='Mark selected as Paid')
def make_paid(modeladmin, request, queryset):
    queryset.update(status='Paid', isactive='',)


@admin.action(description='Mark selected as Overdue')
def make_overdue(modeladmin, request, queryset):
    queryset.update(status='Overdue', isactive='True',)


@admin.action(description='Mark selected as Resolved')
def make_resolved(modeladmin, request, queryset):
    queryset.update(status='Resolved', isactive='',)


@admin.action(description='Mark selected as Date Unavailable')
def make_dateunavailable(modeladmin, request, queryset):
    queryset.update(status='Date_Unavailable', isactive='True',)


@admin.action(description='Mark selected as Scheduled')
def make_scheduled(modeladmin, request, queryset):
    queryset.update(status='Scheduled', isactive='True',)


@admin.action(description='Mark selected as Inactive')
def make_inactive(modeladmin, request, queryset):
    queryset.update(isactive='',)


class ActiveFilter(SimpleListFilter):
    title = _('Active')

    parameter_name = 'isactive'

    def lookups(self, request, model_admin):
        return (
            (None, _('False')),
            ('all', _('All')),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() in ('True', ''):
            return queryset.filter(isactive=self.value())
        elif self.value() == None:
            return queryset.filter(isactive='True')


# EXPORT Resources
class AdminResource(resources.ModelResource):
    first_name = Field(attribute='account__first_name', column_name='first_name')
    last_name = Field(attribute='account__last_name', column_name='last_name')

    class Meta:
        model = Admin
        fields = ('id', 'first_name', 'last_name', 'contact', 'dateofbirth', 'isactive')
        export_order = ('id', 'first_name', 'last_name', 'contact', 'dateofbirth', 'isactive')


class TenantResource(resources.ModelResource):
    first_name = Field(attribute='account__first_name', column_name='first_name')
    last_name = Field(attribute='account__last_name', column_name='last_name')
    unit_floor = Field(attribute='unit__floor', column_name='floor')
    unit_room = Field(attribute='unit__room', column_name='room')

    class Meta:
        model = Tenant
        fields = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'contact', 'dateofbirth', 'isactive')
        export_order = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'contact', 'dateofbirth', 'isactive')


class BillingResource(resources.ModelResource):
    first_name = Field(attribute='tenant__account__first_name', column_name='first_name')
    last_name = Field(attribute='tenant__account__last_name', column_name='last_name')
    unit_floor = Field(attribute='tenant__unit__floor', column_name='floor')
    unit_room = Field(attribute='tenant__unit__room', column_name='room')
    type = Field(attribute='billing_type__billing_name', column_name='billing_type')

    class Meta:
        model = Billing
        fields = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_issued', 'type', 'billing_fee', 'due_date', 'status', 'isactive')
        export_order = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_issued', 'type', 'billing_fee', 'due_date', 'status', 'isactive')


class ProofResource(resources.ModelResource):
    first_name = Field(attribute='billing__tenant__account__first_name', column_name='first_name')
    last_name = Field(attribute='billing__tenant__account__last_name', column_name='last_name')
    unit_floor = Field(attribute='billing__tenant__unit__floor', column_name='floor')
    unit_room = Field(attribute='billing__tenant__unit__room', column_name='room')
    type = Field(attribute='billing__billing_type__billing_name', column_name='billing_type')

    class Meta:
        model = ProofOfPayment
        fields = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_submitted', 'type', 'status', 'isactive')
        export_order = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_submitted', 'type', 'status', 'isactive')


class VisitorResource(resources.ModelResource):
    first_name = Field(attribute='tenant__account__first_name', column_name='first_name')
    last_name = Field(attribute='tenant__account__last_name', column_name='last_name')
    unit_floor = Field(attribute='tenant__unit__floor', column_name='floor')
    unit_room = Field(attribute='tenant__unit__room', column_name='room')

    class Meta:
        model = Visitor
        fields = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_issued', 'purpose', 'visitor_count', 'visitor_names', 'visit_date', 'duration', 'status', 'isactive')
        export_order = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_issued', 'purpose', 'visitor_count', 'visitor_names', 'visit_date', 'duration', 'status', 'isactive')


class ReportResource(resources.ModelResource):
    first_name = Field(attribute='tenant__account__first_name', column_name='first_name')
    last_name = Field(attribute='tenant__account__last_name', column_name='last_name')
    unit_floor = Field(attribute='tenant__unit__floor', column_name='floor')
    unit_room = Field(attribute='tenant__unit__room', column_name='room')

    class Meta:
        model = Report
        fields = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_issued', 'category', 'details', 'neighbour', 'staff', 'status', 'isactive')
        export_order = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_issued', 'category', 'details', 'neighbour', 'staff', 'status', 'isactive')


class RepairResource(resources.ModelResource):
    first_name = Field(attribute='tenant__account__first_name', column_name='first_name')
    last_name = Field(attribute='tenant__account__last_name', column_name='last_name')
    unit_floor = Field(attribute='tenant__unit__floor', column_name='floor')
    unit_room = Field(attribute='tenant__unit__room', column_name='room')

    class Meta:
        model = Repair
        fields = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_issued', 'category', 'details', 'date_available', 'status', 'isactive')
        export_order = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_issued', 'category', 'details', 'date_available', 'status', 'isactive')


class AttritionResource(resources.ModelResource):
    first_name = Field(attribute='tenant__account__first_name', column_name='first_name')
    last_name = Field(attribute='tenant__account__last_name', column_name='last_name')
    unit_floor = Field(attribute='tenant__unit__floor', column_name='floor')
    unit_room = Field(attribute='tenant__unit__room', column_name='room')

    class Meta:
        model = AttritionPrediction
        fields = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'datetime', 'attrition_probability', 'isactive')
        export_order = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'datetime', 'attrition_probability', 'isactive')


class LogsResource(resources.ModelResource):
    first_name = Field(attribute='tenant__account__first_name', column_name='first_name')
    last_name = Field(attribute='tenant__account__last_name', column_name='last_name')
    unit_floor = Field(attribute='tenant__unit__floor', column_name='floor')
    unit_room = Field(attribute='tenant__unit__room', column_name='room')

    class Meta:
        model = LogTenant
        fields = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_time', 'activity', 'action', 'isactive')
        export_order = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'date_time', 'activity', 'action', 'isactive')


class ContractResource(resources.ModelResource):
    first_name = Field(attribute='tenant__account__first_name', column_name='first_name')
    last_name = Field(attribute='tenant__account__last_name', column_name='last_name')
    unit_floor = Field(attribute='tenant__unit__floor', column_name='floor')
    unit_room = Field(attribute='tenant__unit__room', column_name='room')
    epayment = Field(attribute='epay', column_name='can pay online')

    class Meta:
        model = TenantContract
        fields = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'rent', 'late_collection', 'grace_period', 'legal_rent', 'deposit', 'months_occupied', 'roommates', 'epayment')
        export_order = ('id', 'first_name', 'last_name', 'unit_floor', 'unit_room', 'rent', 'late_collection', 'grace_period', 'legal_rent', 'deposit', 'months_occupied', 'roommates', 'epayment')


# ADMIN LIST TABLES
class AdminList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id','get_account', 'image_tag', 'contact', 'get_dateofbirth', 'get_isactive',)
    list_filter = ('account__date_joined',)
    ordering = ('account',)
    resource_class = AdminResource

    def get_account(self, obj):
        return obj.account.first_name + " " + obj.account.last_name

    def get_dateofbirth(self, obj):
        return obj.dateofbirth

    def get_isactive(self, obj):
        return bool(obj.isactive)

    def image_tag(self, obj):
        if not obj.image:
            return "No image provided"
        else:
            return format_html('<a href="{}">Open Image<a/>'.format(obj.image.url))

    get_account.short_description = 'Account'
    get_dateofbirth.short_description = 'Date of Birth'
    get_isactive.short_description = 'Active'
    get_isactive.boolean = 'isactive'
    image_tag.short_description = 'Image'

    exclude = ('isactive',)


class TenantUnitList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_unit', 'floor', 'room', 'get_tenantnum')
    list_filter = ('floor',)
    ordering = ('floor','room')

    def get_unit(self, obj):
        return str(obj.floor) + str(obj.room)

    def get_tenantnum(self, obj):
        return obj.tenant_num

    get_unit.short_description = 'Unit'
    get_tenantnum.admin_order_field = 'tenant_num'
    get_tenantnum.short_description = 'Number of Tenants'

    exclude = ('tenant_num',)


class TenantList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'get_account', 'get_unit', 'image_tag', 'contact', 'get_dateofbirth', 'get_isactive',)
    list_filter = ('account__date_joined',)
    ordering = ('unit__floor',)
    resource_class = TenantResource

    def get_account(self, obj):
        return obj.account.first_name + " " + obj.account.last_name

    def get_unit(self, obj):
        return str(obj.unit.floor) + str(obj.unit.room)

    def get_dateofbirth(self, obj):
        return obj.dateofbirth

    def get_isactive(self, obj):
        return bool(obj.isactive)

    def image_tag(self, obj):
        if not obj.image:
            return "No image provided"
        else:
            return format_html('<a href="{}">Open Image<a/>'.format(obj.image.url))

    get_account.short_description = 'Name'
    get_unit.short_description = 'Unit'
    get_dateofbirth.short_description = 'Date of Birth'
    get_isactive.short_description = 'Active'
    get_isactive.boolean = 'isactive'
    image_tag.short_description = 'Image'

    exclude = ('isactive',)


class TenantRegistrationList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_name', 'get_unit', 'get_datejoined', 'image_tag', 'username', 'email', 'contact', 'get_dateofbirth', 'status', 'get_isactive',)
    list_filter = [ActiveFilter]
    ordering = ('-date_joined',)

    def get_name(self, obj):
        return obj.first_name + " " + obj.last_name

    def get_unit(self, obj):
        return str(obj.unit.floor) + str(obj.unit.room)

    def get_dateofbirth(self, obj):
        return obj.dateofbirth

    def get_datejoined(self, obj):
        return obj.date_joined

    def get_isactive(self, obj):
        return bool(obj.isactive)

    def get_id(self, obj):
        return obj.id

    def image_tag(self, obj):
        if not obj.image:
            return "No image provided"
        else:
            return format_html('<a href="{}">Open Image<a/>'.format(obj.image.url))

    get_name.short_description = 'Name'
    get_unit.short_description = 'Unit'
    get_datejoined.short_description = 'Date Registered'
    get_dateofbirth.short_description = 'Date of Birth'
    get_isactive.short_description = 'Active'
    get_isactive.boolean = 'isactive'
    image_tag.short_description = 'Image'

    actions = [make_approved_reg, make_rejected]


class CustomList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_account', 'get_colorscheme', 'get_isactive',)
    ordering = ('account',)

    def get_account(self, obj):
        return obj.account.first_name + " " + obj.account.last_name

    def get_colorscheme(self, obj):
        return obj.color_scheme

    def get_isactive(self, obj):
        return bool(obj.isactive)

    get_account.short_description = 'Tenant'
    get_colorscheme.short_description = 'Color Scheme'
    get_isactive.short_description = 'Active'
    get_isactive.boolean = 'isactive'


class BillingTypeList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_billingcode', 'get_billingname', 'get_isactive',)
    ordering = ('billing_code',)

    def get_billingcode(self, obj):
        return obj.billing_code

    def get_billingname(self, obj):
        return obj.billing_name

    def get_isactive(self, obj):
        return bool(obj.isactive)

    get_billingcode.short_description = 'Billing Code'
    get_billingname.short_description = 'Billing Name'
    get_isactive.short_description = 'Active'
    get_isactive.boolean = 'isactive'

    exclude = ('isactive',)


class BillingList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_unit', 'get_dateissued', 'get_name', 'get_billingname', 'get_billingfee', 'get_duedate', 'status', 'get_isactive',)
    list_filter = ('status','date_issued','due_date')
    actions = [make_paid]
    resource_class = BillingResource

    def get_unit(self, obj):
        return str(obj.tenant.unit.floor) + str(obj.tenant.unit.room)

    def get_dateissued(self, obj):
        return obj.date_issued

    def get_name(self, obj):
        return obj.tenant.account.first_name + " " + obj.tenant.account.last_name

    def get_billingname(self, obj):
        return obj.billing_type.billing_name

    def get_billingfee(self, obj):
        return str(obj.billing_fee)

    def get_duedate(self, obj):
        return obj.due_date

    def get_isactive(self, obj):
        return bool(obj.isactive)

    get_duedate.admin_order_field = 'due_date'
    get_unit.admin_order_field = 'tenant__unit__floor'
    get_name.admin_order_field = 'tenant__account__first_name'
    get_unit.short_description = 'Unit'
    get_dateissued.short_description = 'Date Issued'
    get_name.short_description = 'Tenant Name'
    get_billingname.short_description = 'Billing Name'
    get_billingfee.short_description = 'Amount'
    get_duedate.short_description = 'Due Date'
    get_isactive.short_description = 'Active'
    get_isactive.boolean = 'isactive'

    form = BillingForm


class ProofList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_unit', 'get_datesubmitted', 'get_name', 'get_billingname', 'get_billingfee', 'image_tag', 'get_duedate', 'status', 'get_isactive',)
    list_filter = [ActiveFilter]
    ordering = ('date_submitted',)
    actions = [make_approved_proof, make_rejected]
    resource_class = ProofResource

    def get_unit(self, obj):
        return str(obj.billing.tenant.unit.floor) + str(obj.billing.tenant.unit.room)

    def get_datesubmitted(self, obj):
        return obj.date_submitted

    def get_name(self, obj):
        return obj.billing.tenant.account.first_name + " " + obj.billing.tenant.account.last_name

    def get_billingname(self, obj):
        return obj.billing.billing_type.billing_name

    def get_billingfee(self, obj):
        return str(obj.billing.billing_fee)

    def get_duedate(self, obj):
        return obj.billing.due_date

    def get_isactive(self, obj):
        return bool(obj.isactive)

    def image_tag(self, obj):
        if not obj.image:
            return "No image provided"
        else:
            return format_html('<a href="{}">'.format(obj.image.url) +
                               '<img src="{}" width="300px"/></a>'.format(obj.image.url))

    get_duedate.admin_order_field = 'due_date'  # Allows column order sorting
    get_unit.short_description = 'Unit'
    get_datesubmitted.short_description = 'Date Submitted'
    get_name.short_description = 'Tenant Name'
    get_billingname.short_description = 'Billing Name'
    get_billingfee.short_description = 'Amount'
    get_duedate.short_description = 'Due Date'
    get_isactive.short_description = 'Active'
    image_tag.short_description = 'Image'
    get_isactive.boolean = 'isactive'

    exclude = ('isactive',)


class TncList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_date', 'get_content',)

    def get_date(self, obj):
        return obj.date_updated

    def get_content(self, obj):
        return obj.tnc_content

    get_date.short_description = 'Date Updated'
    get_content.short_description = 'Terms and Conditions'


class AnnouncementList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_main', 'get_sub', 'get_link', 'image_tag' ,'get_isactive',)

    def get_main(self, obj):
        return obj.main_news.headline

    def get_sub(self, obj):
        return obj.sub_news.headline

    def get_link(self, obj):
        return obj.survey_link

    def get_isactive(self, obj):
        return bool(obj.isactive)

    def image_tag(self, obj):
        if not obj.image:
            return "No image provided"
        else:
            return format_html('<a href="{}">Open Image<a/>'.format(obj.image.url))

    get_main.short_description = 'Main News'
    get_sub.short_description = 'Sub News'
    get_link.short_description = 'Survey Link'
    get_isactive.short_description = 'Active'
    image_tag.short_description = 'Advertisement'
    get_isactive.boolean = 'isactive'

    exclude = ('isactive',)


class NewsList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_date', 'image', 'headline', 'content', 'get_isactive',)
    list_filter = ('datepublished',)
    actions = [make_inactive,]

    def get_date(self, obj):
        return obj.datepublished

    def get_isactive(self, obj):
        return bool(obj.isactive)

    get_date.short_description = 'Unit'
    get_isactive.short_description = 'Active'
    get_isactive.boolean = 'isactive'


class VisitorList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_dateissued', 'get_name', 'purpose', 'get_visitdate', 'get_count', 'get_duration', 'status', 'reason', 'get_isactive',)
    list_filter = [ActiveFilter]
    actions = [make_approved_false, make_rejected]
    resource_class = VisitorResource

    def get_dateissued(self, obj):
        return obj.date_issued

    def get_duration(self, obj):
        return obj.duration

    def get_name(self, obj):
        return obj.tenant.account.first_name + " " + obj.tenant.account.last_name

    def get_visitdate(self, obj):
        return obj.visit_date

    def get_count(self, obj):
        return obj.visitor_count

    def get_isactive(self, obj):
        return bool(obj.isactive)

    get_dateissued.admin_order_field = 'date_issued'
    get_visitdate.admin_order_field = 'visit_date'  # Allows column order sorting
    get_name.short_description = 'Tenant Name'
    get_dateissued.short_description = 'Date Submitted'
    get_visitdate.short_description = 'Visit Date'
    get_count.short_description = 'No. of Visitors'
    get_isactive.short_description = 'Active'
    get_isactive.boolean = 'isactive'


class ReportList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('ticket_no', 'get_dateissued', 'get_name', 'get_unit', 'get_category', 'get_details', 'image_tag', 'status', 'get_isactive',)
    list_filter = ('status', 'category',)
    resource_class = ReportResource

    def ticket_no(self, obj):
        return "Ticket #" + str(obj.id)

    def get_unit(self, obj):
        return str(obj.tenant.unit.floor) + str(obj.tenant.unit.room)

    def get_dateissued(self, obj):
        return obj.date_issued

    def get_category(self, obj):
        return obj.category

    def get_details(self, obj):
        return obj.details

    def get_name(self, obj):
        return obj.tenant.account.first_name + " " + obj.tenant.account.last_name

    def get_isactive(self, obj):
        return bool(obj.isactive)

    def image_tag(self, obj):
        if not obj.image:
            return "No image provided"
        else:
            return format_html('<a href="{}">Open Image<a/>'.format(obj.image.url))

    get_isactive.admin_order_field = 'isactive'
    ticket_no.admin_order_field = 'id'
    get_details.short_description = 'Details'
    ticket_no.short_description = 'Ticket No.'
    get_name.short_description = 'Tenant Name'
    get_unit.short_description = 'Tenant Unit'
    get_category.short_description = 'Category'
    get_dateissued.short_description = 'Date Submitted'
    get_isactive.short_description = 'Active'
    get_isactive.boolean = 'isactive'
    image_tag.short_description = 'Image'


class RepairList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('ticket_no', 'get_dateissued', 'get_name', 'get_unit', 'get_category', 'get_details', 'image_tag', 'get_dateavailable', 'status', 'get_isactive',)
    list_filter = ('status', 'category',)
    actions = [make_scheduled, make_dateunavailable]
    resource_class = RepairResource

    def ticket_no(self, obj):
        return "Ticket #" + str(obj.id)

    def get_unit(self, obj):
        return str(obj.tenant.unit.floor) + str(obj.tenant.unit.room)

    def get_dateissued(self, obj):
        return obj.date_issued

    def get_category(self, obj):
        return obj.category

    def get_details(self, obj):
        return obj.details

    def get_name(self, obj):
        return obj.tenant.account.first_name + " " + obj.tenant.account.last_name

    def get_dateavailable(self, obj):
        return obj.date_available

    def get_isactive(self, obj):
        return bool(obj.isactive)

    def image_tag(self, obj):
        if not obj.image:
            return "No image provided"
        else:
            return format_html('<a href="{}">Open Image<a/>'.format(obj.image.url))

    ticket_no.admin_order_field = 'id'  # Allows column order sorting
    get_isactive.admin_order_field = 'isactive'
    ticket_no.short_description = 'Ticket No.'
    get_details.short_description = 'Details'
    get_name.short_description = 'Tenant Name'
    get_unit.short_description = 'Tenant Unit'
    get_dateavailable.short_description = 'Date Available'
    get_category.short_description = 'Category'
    get_dateissued.short_description = 'Date Submitted'
    get_isactive.short_description = 'Active'
    get_isactive.boolean = 'isactive'
    image_tag.short_description = 'Image'


class AttritionList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_name', 'get_unit', 'get_datetime', 'get_ap', 'get_isactive',)
    list_filter = ('attrition_probability',)
    resource_class = AttritionResource

    def get_unit(self, obj):
        return str(obj.tenant.unit.floor) + str(obj.tenant.unit.room)

    def get_name(self, obj):
        return obj.tenant.account.first_name + " " + obj.tenant.account.last_name

    def get_datetime(self, obj):
        return obj.datetime

    def get_ap(self, obj):
        return obj.attrition_probability

    def get_isactive(self, obj):
        return bool(obj.isactive)

    get_isactive.admin_order_field = 'isactive'  # Allows column order sorting
    get_name.short_description = 'Tenant Name'
    get_unit.short_description = 'Tenant Unit'
    get_datetime.short_description = 'Date Processed'
    get_ap.short_description = 'Attrition Probability'
    get_isactive.short_description = 'Active'
    get_isactive.boolean = 'isactive'

    exclude = ('isactive',)


class LogTenantList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_name', 'get_unit',  'get_datetime', 'activity', 'action',)
    list_filter = ('activity',)
    resource_class = LogsResource

    def get_unit(self, obj):
        return str(obj.tenant.unit.floor) + str(obj.tenant.unit.room)

    def get_name(self, obj):
        return obj.tenant.account.first_name + " " + obj.tenant.account.last_name

    def get_datetime(self, obj):
        return obj.date_time

    get_datetime.admin_order_field = 'date_time'
    get_datetime.short_description = 'Date and Time'
    get_name.short_description = 'Tenant Name'
    get_unit.short_description = 'Tenant Unit'


class ContractList(ExportActionMixin, admin.ModelAdmin):
    list_display = ('get_name', 'get_unit',  'rent', 'get_late', 'get_grace', 'get_legal', 'deposit', 'get_months', 'get_mates', 'get_epay', 'confirmation')
    resource_class = ContractResource

    def get_unit(self, obj):
        return str(obj.tenant.unit.floor) + str(obj.tenant.unit.room)

    def get_name(self, obj):
        return obj.tenant.account.first_name + " " + obj.tenant.account.last_name

    def get_late(self, obj):
        return obj.late_collection

    def get_grace(self, obj):
        return obj.grace_period

    def get_legal(self, obj):
        return obj.legal_rent

    def get_months(self, obj):
        return obj.months_occupied

    def get_mates(self, obj):
        if obj.roommates == 1:
            return "Yes"
        if obj.roommates == 0:
            return "No"

    def get_epay(self, obj):
        if obj.epay == 1:
            return "Yes"
        if obj.epay == 0:
            return "No"

    get_late.short_description = 'Late Collection Fee'
    get_grace.short_description = 'Grace Period'
    get_legal.short_description = 'Legal Rent'
    get_months.short_description = 'Months Occupied'
    get_mates.short_description = 'Have Roommates?'
    get_epay.short_description = 'Pay thru Online?'
    get_name.short_description = 'Tenant Name'
    get_unit.short_description = 'Tenant Unit'


# ADMIN TABLE REGISTER
admin.site.register(Admin, AdminList)
admin.site.register(TenantUnit, TenantUnitList)
admin.site.register(Tenant, TenantList)
admin.site.register(TenantRegistration, TenantRegistrationList)
admin.site.register(AccountCustomization, CustomList)
admin.site.register(BillingType, BillingTypeList)
admin.site.register(Billing, BillingList)
admin.site.register(ProofOfPayment, ProofList)
admin.site.register(TermsAndCondition, TncList)
admin.site.register(TenantAnnouncement, AnnouncementList)
admin.site.register(AnnouncementNew, NewsList)
admin.site.register(Visitor, VisitorList)
admin.site.register(Report, ReportList)
admin.site.register(Repair, RepairList)
admin.site.register(AttritionPrediction, AttritionList)
admin.site.register(LogTenant, LogTenantList)
admin.site.register(TenantContract, ContractList)


