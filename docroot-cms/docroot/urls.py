"""docroot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
# ITEMS BETWEEN THESE HEADINGS WILL BE UPDATED
# ------------------------ DOCROOT CMS URLS ------------------------------------
# add our different urls for the cms to work
from django.conf.urls import include

# sas comment to be removed so I know this is working
urlpatterns += [
    path('_cms/', include('docroot-cms.urls')),
]
# ------------------------ DOCROOT CMS URLS ------------------------------------
