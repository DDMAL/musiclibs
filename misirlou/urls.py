"""misirlou URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url, patterns
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from misirlou import views

urlpatterns = []
urlpatterns += format_suffix_patterns(
    patterns('misirlou.views.views',
             url(r'^admin/', include(admin.site.urls)),

             url(r'^$', views.ApiRootView.as_view(), name='api-root'),
             url('manifests/$', views.ManifestList.as_view(),
                 name='manifest-list'),
             url('manifests/(?P<pk>[0-9]+)/$', views.ManifestDetail.as_view(),
                 name='manifest-detail'),

             url(r'search/$', views.SearchView.as_view(), name='search')
             )
)
