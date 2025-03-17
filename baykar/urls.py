from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.decorators.http import require_http_methods
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from production.views import PartViewSet, TeamViewSet, AircraftViewSet, CustomLoginView
from production.urls import router as production_router
from django.conf import settings
from django.conf.urls.static import static

# API router
router = DefaultRouter()
router.register(r'parts', PartViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'aircraft', AircraftViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('production.urls')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login', http_method_names=['get', 'post']), name='logout'),
    path('aircraft/', include('aircraft_factory.urls')),
    
    # API URLs
    path('api/', include((router.urls, 'api'))),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Static ve media dosyalarını development ortamında servis etmek için
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 