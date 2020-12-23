import debug_toolbar
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.views.generic import RedirectView

from reversion_compare_tests.views import SimpleModelHistoryCompareView


admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/')),

    url(r"^test_view/(?P<pk>\d+)$", SimpleModelHistoryCompareView.as_view()),

    path('__debug__/', include(debug_toolbar.urls)),
]

urlpatterns += staticfiles_urlpatterns()
