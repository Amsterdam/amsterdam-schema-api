from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic.base import RedirectView
from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularSwaggerView,
    SpectacularYAMLAPIView,
)
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter(trailing_slash=False)
router.register(r"datasets", views.DatasetViewSet, basename="dataset")
router.register(r"scopes", views.ScopeViewSet, basename="scope")
router.register(r"publishers", views.PublisherViewSet, basename="publisher")
router.register(r"profiles", views.ProfileViewSet, basename="profile")
router.register(r"changelog", views.ChangelogViewSet, basename="changelog")

urlpatterns = [
    path("status", views.RootView.as_view()),
    path("v1/", include(router.urls)),
    path("", RedirectView.as_view(url="v1/", permanent=True)),
    path(
        "v1/schema",
        SpectacularSwaggerView.as_view(url_name="schema-json"),
        name="swagger-ui",
    ),
    path("v1/openapi.json", SpectacularJSONAPIView.as_view(), name="schema-json"),
    path("v1/openapi.yaml", SpectacularYAMLAPIView.as_view(), name="schema-yaml"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
