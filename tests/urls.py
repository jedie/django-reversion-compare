# coding: utf-8

from django.conf.urls import include, url

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.shortcuts import redirect

from tests.views import SimpleModelHistoryCompareView

admin.autodiscover()

urlpatterns = [
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^test_view/(?P<pk>\d+)$', SimpleModelHistoryCompareView.as_view() ),
    
    # redirect root view to admin page:
    url(r'^$', lambda x: redirect("admin:index")),
]

urlpatterns += staticfiles_urlpatterns()
