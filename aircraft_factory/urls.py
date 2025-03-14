from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from production import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('production.urls')),
    path('api-auth/', include('rest_framework.urls')),
    
    # Authentication views
    path('login/', auth_views.LoginView.as_view(template_name='production/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='production/password_change.html',
        success_url='password_change_done'
    ), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='production/password_change_done.html'
    ), name='password_change_done'),
    
    # Template views
    path('', views.home, name='home'),
    path('parts/', views.parts_list, name='parts_list'),
    path('teams/', views.teams_list, name='teams_list'),
    path('aircraft/', views.aircraft_list, name='aircraft_list'),
    path('profile/', views.profile, name='profile'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 