from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from .views import HealthCheckAPIView, swagger_password_protect

schema_view = get_schema_view(
    openapi.Info(
        title='Water Ambassador API',
        default_version='v1',
        description='Documentation complète du backend Water Ambassador.',
        terms_of_service='#',
        contact=openapi.Contact(email='contact@example.local'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=[AllowAny],
)

protected_swagger = swagger_password_protect(schema_view.with_ui('swagger', cache_timeout=0))
protected_redoc = swagger_password_protect(schema_view.with_ui('redoc', cache_timeout=0))
protected_schema_json = swagger_password_protect(schema_view.without_ui(cache_timeout=0))

urlpatterns = [
    path('administrateurplusplus/', admin.site.urls),
    path('api/health/', HealthCheckAPIView.as_view(), name='health_check'),

    path('api/accounts/admin/', include('apps.accounts.admin.urls')),
    path('api/auth/', include('apps.accounts.user.urls')),
    
    path('api/formation/', include('apps.formation.urls')),

    path('api/swagger/docs/', protected_swagger, name='schema-swagger-ui'),
    path('api/swagger/redoc/', protected_redoc, name='schema-redoc'),
    re_path(r'^api/swagger/schema(?P<format>\.json|\.yaml)$', protected_schema_json, name='schema-json'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'config.views.custom_404'
