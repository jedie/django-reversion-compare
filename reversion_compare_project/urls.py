from django.conf import settings
from django.conf.urls import include, static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from reversion_compare_project.views import SimpleModelHistoryCompareView


admin.autodiscover()


urlpatterns = i18n_patterns(
    path("test_view/<path:pk>/", SimpleModelHistoryCompareView.as_view(), name='test_view'),
    #
    # The Django admin with redirect:
    path('', RedirectView.as_view(url="/admin/")),
    path("admin/", admin.site.urls),
)


if settings.SERVE_FILES:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
