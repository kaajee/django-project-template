"""Root URL configuration.

Two auth surfaces share one user model:
  * ``/accounts/``  -> allauth standard template views (browser session login)
  * ``/_allauth/``  -> allauth headless JSON API (issues JWTs for the REST API)
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.common.health import liveness, readiness

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth: web (session) + API (headless JWT).
    path("accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
    # Server-rendered web UI (CRM user management).
    path("crm/", include("apps.crm.urls")),
    # Health probes.
    path("healthz/", liveness, name="healthz"),
    path("readyz/", readiness, name="readyz"),
    # OpenAPI schema + docs.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # REST API (v1).
    path("api/v1/", include("apps.users.urls")),
    # Optional simplejwt token endpoints (allauth issues JWTs by default):
    # from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
    # path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
