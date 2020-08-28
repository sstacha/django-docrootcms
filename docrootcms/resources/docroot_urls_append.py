# ------------------------ DOCROOT CMS URLS ------------------------------------
# add our different urls for the cms to work
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static

urlpatterns += [
    path('_cms/', include('docrootcms.urls')),
    path('blog/', include('docrootcms.contrib.blog.urls')),
    path('markdownx/', include('markdownx.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ------------------------ DOCROOT CMS URLS ------------------------------------
