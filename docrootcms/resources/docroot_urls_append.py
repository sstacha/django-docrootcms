# ------------------------ DOCROOT CMS URLS ------------------------------------
# add our different urls for the cms to work
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from docrootcms.views import MarkdownImageUploadView

urlpatterns += [
    path('_cms/', include('docrootcms.urls')),
    path('blog/', include('docrootcms.contrib.blog.urls')),
    # sas 2020-09-27 : override the markdownx url and apply our overridden view/form instead
    # NOTE: don't forget to copy the js changes into static for transferring the new field to the view
    path('markdownx/upload/', MarkdownImageUploadView.as_view(), name='markdownx_upload'),

    path('markdownx/', include('markdownx.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ------------------------ DOCROOT CMS URLS ------------------------------------
