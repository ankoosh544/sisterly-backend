from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('superuser/', admin.site.urls),
    path('admin/', include('admin_app.urls')),
    path('client/', include('client_app.urls.client')),
    path('product/', include('client_app.urls.product')),
    path('password_reset_complete',
         auth_views.PasswordResetCompleteView.as_view(template_name='client/password_reset_complete.html'),
         name='password_reset_complete'),

    path('schema/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    #path('docs/', include_docs_urls(title="Sisterly API")),
   # path('schema/', get_schema_view(title="Sisterly Api", description="API for Sisterly Services", version="1.0.0"), name='openapi-schema'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
