# ------------------------ DOCROOT CMS URLS ------------------------------------
# add our different urls for the cms to work
from django.conf.urls import include

urlpatterns += [
    path('_cms/', include('docroot-cms.urls')),
]
# ------------------------ DOCROOT CMS URLS ------------------------------------
