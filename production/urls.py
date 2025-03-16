from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'production'

router = DefaultRouter()
router.register(r'teams', views.TeamViewSet)
router.register(r'parts', views.PartViewSet)
router.register(r'aircraft', views.AircraftViewSet)

# No need for register_action as DRF automatically registers actions defined with @action decorator

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('parts/', views.parts_list, name='parts_list'),
    path('teams/', views.teams_list, name='teams_list'),
    path('aircraft/', views.aircraft_list, name='aircraft_list'),
    path('add-production/', views.add_production, name='add_production'),
    path('aircraft/<int:aircraft_id>/required-parts/', views.get_required_parts, name='get_required_parts'),
    path('add-aircraft-part/', views.add_aircraft_part, name='add_aircraft_part'),
    path('aircraft/<int:pk>/claim/', views.claim_aircraft, name='claim_aircraft'),
] 