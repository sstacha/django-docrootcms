from . import views
from django.urls import path

urlpatterns = [
    # path('simple/', views.PostList.as_view(), name='blog_home'),
    # path('simple/<slug:slug>/', views.PostDetail.as_view(), name='blog_detail'),
    path('', views.PostList.as_view(), name='blog_home'),
    path('<slug:slug>/', views.PostDetail.as_view(), name='blog_detail'),
]
