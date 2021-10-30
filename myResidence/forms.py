from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib import admin
from .models import *


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email_name = self.cleaned_data['email']

        if commit:
            user.save()
        return user


class TenantRegistrationForm(forms.ModelForm):
    unit = forms.ModelChoiceField(queryset=TenantUnit.objects.all().order_by('floor','room'))
    unit.widget.attrs.update({'class': 'form-select'})

    class Meta:
        model = TenantRegistration
        fields = '__all__'
        exclude = ("date_joined", "status", "isActive")


class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = '__all__'
        exclude = ("date_issued","status","reason","tenant","isActive")


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'
        exclude = ("date_issued","status","tenant","isActive")


class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = '__all__'
        exclude = ("date_issued","status","tenant","isActive")


class CustomForm(forms.ModelForm):
    class Meta:
        model = AccountCustomization
        fields = '__all__'


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['unit', 'contact', 'work_address', 'dateofbirth', 'image']


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class AccountRegForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'


class TenantRegForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = '__all__'


class TenantLogsForm(forms.ModelForm):
    class Meta:
        model = LogTenant
        fields = '__all__'


class AdminLogsForm(forms.ModelForm):
    class Meta:
        model = LogAdmin
        fields = '__all__'


class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = '__all__'
        exclude = ('status', 'isactive', 'date_issued',)


class ProofForm(forms.ModelForm):
    class Meta:
        model = ProofOfPayment
        fields = '__all__'
        exclude = ("date_submitted","status","isActive")


class ContractForm(forms.ModelForm):
    class Meta:
        model = TenantContract
        fields = '__all__'


class AttritionForm(forms.ModelForm):
    class Meta:
        model = AttritionPrediction
        fields = '__all__'


