"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# ---------------------------------------------------------------------------------
# Schema view for API documentation using drf-yasg (Swagger & ReDoc)
# ---------------------------------------------------------------------------------
schema_view = get_schema_view(
    openapi.Info(
        title="Appoint",              # API title
        default_version='v1',             # Default API version
        description="API Documentation for Appoint",  # Brief API description
    ),
    public=True,                         # Make the docs publicly accessible
    permission_classes=[permissions.AllowAny],  # Allow any user (authenticated or not) to view docs
)


urlpatterns = [
    path('admin/', admin.site.urls),                 # Django admin panel
    path('api/', include('main_app.api.urls')),     # Main application API routes
    path('api/account/', include('account_app.api.urls')),  # Account related API routes

    # Swagger UI route for interactive API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # ReDoc UI route for alternative API documentation style
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


