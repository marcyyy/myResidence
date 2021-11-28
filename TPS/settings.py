"""
Django settings for TPS project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
from django.conf.global_settings import LANGUAGES as DJANGO_LANGUAGES

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6=(wmp^)a6jufk#=bl*5)*72%a427mc$l8%@smw(t6=zjyzcrq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['tps-myresidence.herokuapp.com', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'admin_reorder',
    'jazzmin',
    'django_extensions',
    'django.contrib.humanize',
    'import_export',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # LOCAL APPS
    'TPS',
    'myResidence',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

ROOT_URLCONF = 'TPS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'TPS.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tpsdb',
        'HOST': '127.0.0.1',
        'USER': 'root',
        'PASSWORD': '',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

USE_L10N = True

USE_TZ = False

LANGUAGES = DJANGO_LANGUAGES

# MEDIA_ROOT = os.path.join(BASE_DIR, "/static/uploaded/profile/")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ADMIN_REORDER = (
    {'app': 'myResidence', 'label': 'Tenant Services',
     'models': (
         {'model': 'myResidence.Visitor', 'label': 'Visitors'},
         {'model': 'myResidence.Report', 'label': 'Reports'},
         {'model': 'myResidence.Repair', 'label': 'Repairs'},
         {'model': 'myResidence.TenantUnit', 'label': 'Floor & Units'},
     )
     },
    {'app': 'myResidence', 'label': 'Tenant Billing',
     'models': (
         {'model': 'myResidence.Billing', 'label': 'Billings'},
         {'model': 'myResidence.BillingType', 'label': 'Billing Types'},
         {'model': 'myResidence.ProofOfPayment', 'label': 'Proof of Payments'},
     )
     },
    {'app': 'myResidence', 'label': 'Tenant Attrition',
     'models': (
         {'model': 'myResidence.TenantContract', 'label': 'Tenant Contract'},
         {'model': 'myResidence.AttritionPrediction', 'label': 'Tenants Attrition Score'},
     )
     },
    {'app': 'myResidence', 'label': 'Account Management',
     'models': (
         {'model': 'auth.User', 'label': 'Accounts'},
         'myResidence.Admin',
         {'model': 'myResidence.Tenant', 'label': 'Tenants'},
         {'model': 'myResidence.TenantRegistration', 'label': 'Tenants Registration'},
         # {'model': 'myResidence.AccountCustomization', 'label': 'Account Customization'},
     )
     },
    {'app': 'myResidence', 'label': 'Content Management',
     'models': (
         {'model': 'myResidence.TermsAndCondition', 'label': 'Terms and Conditions'},
         {'model': 'myResidence.TenantAnnouncement', 'label': 'myResidence Announcements'},
         {'model': 'myResidence.AnnouncementNew', 'label': 'Announcement News'},
     )
     },
    {'app': 'myResidence', 'label': 'Activity Logs',
     'models': (
         {'model': 'myResidence.LogTenant', 'label': 'Tenant Logs'},
         {'model': 'myResidence.LogAdmin', 'label': 'Admin Logs'},
     )
     },

)

JAZZMIN_SETTINGS = {
    "site_title": "myResidence",
    "site_header": "myResidence",
    "site_brand": "myResidence",
    "site_logo": "logo/myResidence_tab.png",

    # Welcome text on the login screen
    "welcome_sign": "AIJM Developers",

    # Copyright on the footer
    "copyright": "AIJM Developers ",

    "hide_models" : "myResidence.accountcustomization",

    "topmenu_links": [
        {"name": "Reports & Analytics", "url": "report"},
        {"name": "Tenant Attrition", "url": "attrition"},
        {"name": "myResidence Website", "url": "login", "new_window": True},
    ],

    "order_with_respect_to": [
        "myResidence.report", "myResidence.repair", "myResidence.visitor", "myResidence.attritionprediction",
        "myResidence.billing", "myResidence.billingtype", "myResidence.proofofpayment",
        "auth.user", "myResidence.admin", "myResidence.tenant", "myResidence.tenantregistration",
        "myResidence.tenantunit", "myResidence.termsandcondition", "myResidence.tenantannouncement",
        "myResidence.announcementnew","myResidence.logtenant", "myResidence.logadmin"],

    "icons": {
        "admin.index": "fas fa-id-card",
        "auth.user": "fas fa-id-card",
        "auth.group": "fas fa-plus-square",
        "myResidence.attritionprediction": "fas fa-tasks",
        "myResidence.tenantunit": "fas fa-building",
        "myResidence.report": "fas fa-inbox",
        "myResidence.repair": "fas fa-wrench",
        "myResidence.visitor": "fas fa-history",
        "myResidence.billingtype": "fas fa-edit",
        "myResidence.billing": "fas fa-archive",
        "myResidence.proofofpayment": "fas fa-print",
        "myResidence.accountcustomization": "fas fa-object-group",
        "myResidence.admin": "fas fa-coffee",
        "myResidence.tenant": "fas fa-users",
        "myResidence.tenantregistration": "fas fa-user-plus",
        "myResidence.termsandcondition": "fas fa-info",
        "myResidence.tenantannouncement": "fas fa-newspaper",
        "myResidence.announcementnew": "fas fa-quote-left",
        "myResidence.logadmin": "fas fa-cog",
        "myResidence.logtenant": "fas fa-cogs",
        "myResidence.tenantcontract": "fas fa-comments",
    },

    "changeform_format_overrides": {"auth.user": "collapsible"},

    # "related_modal_active": True,

    "language_chooser": True,

    # "show_ui_builder": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-teal navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": False,  # True
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-olive",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "sandstone",
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    },
    "actions_sticky_top": False
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

import django_heroku
django_heroku.settings(locals())
