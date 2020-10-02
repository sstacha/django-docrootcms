"""cms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('content/', views.ContentApi.as_view(), name='cms_content'),
    path('login', views.LoginFormView.as_view(), name="cms_login"),
    path('logout', views.LogoutView.as_view(), name="cms_logout"),
    path('auth', views.AuthenticateView.as_view(), name="cms_authenticate"),
    # sas 2020-09-27 : attempting to override the markdownx url and apply our overridden view/form instead
    # NOTE: don't forget to copy the js changes into static for transferring the new field to the view
    path('markdownx/upload/', views.MarkdownImageUploadView.as_view(), name='markdownx_upload')
]
