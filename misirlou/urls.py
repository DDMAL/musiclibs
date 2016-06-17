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
from django.conf.urls import include, url
from django.contrib import admin
from misirlou import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.RootView.as_view(), name='api-root'),
    url('^about/$', views.AboutView.as_view(), name='about'),
    url('^manifests/$',
        views.ManifestList.as_view(),
        name='manifest-list'),
    url('^manifests/(?P<pk>[^/]{36})/$',
        views.ManifestDetail.as_view(),
        name='manifest-detail'),
    url('^manifests/(?P<pk>[^/]{36})/search/$',
        views.ManifestDetailSearch.as_view(),
        name='manifest-detail-search'),
    url('^manifests/recent/$',
        views.RecentManifestList.as_view(),
        name='recent-manifest-list'),
    url('^manifests/upload/$',
        views.ManifestUpload.as_view(),
        name='manifest-upload'),
    url(r'^suggest/$',
        views.SuggestView.as_view(),
        name='suggest'),
    url(r'^status/(?P<pk>[^/]{36})/$',
        views.StatusView.as_view(),
        name='status'),
    url(r'^stats/$', views.StatsView.as_view(), name='stats_view'),
    url(r'^login/$', views.LoginView.as_view(), name="login"),
    url(r'^logout/$', views.LogoutView.as_view(), name="logout"),
    ]
