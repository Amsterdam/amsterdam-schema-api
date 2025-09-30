from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"datasets", views.DatasetViewSet, basename="dataset")
router.register(r"scopes", views.ScopeViewSet, basename="scope")
router.register(r"publishers", views.PublisherViewSet, basename="publisher")
router.register(r"profiles", views.ProfileViewSet, basename="profile")

urlpatterns = [
    path("status/", views.RootView.as_view()),
    path("", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
