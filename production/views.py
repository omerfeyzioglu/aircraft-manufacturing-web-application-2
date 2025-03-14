from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F, Sum, Count, Q
from .models import Part, Team, Aircraft, Production, AircraftPart
from .serializers import (
    PartSerializer, TeamSerializer, AircraftSerializer,
    ProductionSerializer, AircraftPartSerializer
)
from django.utils import timezone
from datetime import timedelta

# Template views
@login_required
def home(request):
    # Son bir haftadaki üretim istatistikleri
    one_week_ago = timezone.now() - timedelta(days=7)
    total_production = Production.objects.filter(created_at__gte=one_week_ago).aggregate(
        total=Sum('quantity'))['total'] or 0
    completed_aircraft = Aircraft.objects.filter(completed_at__gte=one_week_ago).count()
    
    # Günlük üretim oranları
    daily_production = Production.objects.filter(
        created_at__gte=one_week_ago
    ).values('created_at__date').annotate(
        total=Sum('quantity')
    ).order_by('created_at__date')

    # Stok durumu düşük olan parçalar
    low_stock_parts = Part.objects.filter(stock__lt=5)

    # Son eklenen uçaklar
    recent_aircraft = Aircraft.objects.all()[:5]

    context = {
        'total_production': total_production,
        'completed_aircraft': completed_aircraft,
        'daily_production': daily_production,
        'low_stock_parts': low_stock_parts,
        'recent_aircraft': recent_aircraft,
    }
    return render(request, 'home.html', context)

@login_required
def profile(request):
    user = request.user
    team = Team.objects.filter(members=user).first()
    
    context = {
        'user': user,
        'team': team,
    }
    
    if team:
        # Kullanıcının takımına göre üretim istatistikleri
        total_productions = Production.objects.filter(team=team).aggregate(
            total=Sum('quantity'))['total'] or 0
            
        recent_productions = Production.objects.filter(team=team).order_by('-created_at')[:5]
        
        if team.team_type == 'ASSEMBLY':
            completed_aircraft = Aircraft.objects.filter(completed_at__isnull=False).count()
            context.update({
                'completed_aircraft': completed_aircraft,
            })
        
        context.update({
            'total_productions': total_productions,
            'recent_productions': recent_productions,
        })
    
    return render(request, 'profile.html', context)

@login_required
def parts_list(request):
    parts = Part.objects.all()
    team_types = [
        ('AVIONICS', 'Aviyonik Takımı'),
        ('BODY', 'Gövde Takımı'),
        ('WING', 'Kanat Takımı'),
        ('TAIL', 'Kuyruk Takımı'),
    ]
    
    context = {
        'parts': parts,
        'team_types': team_types,
    }
    return render(request, 'parts/list.html', context)

@login_required
def teams_list(request):
    teams = Team.objects.all()
    team_types = [
        ('AVIONICS', 'Aviyonik Takımı'),
        ('BODY', 'Gövde Takımı'),
        ('WING', 'Kanat Takımı'),
        ('TAIL', 'Kuyruk Takımı'),
        ('ASSEMBLY', 'Montaj Takımı'),
    ]
    
    context = {
        'teams': teams,
        'team_types': team_types,
    }
    return render(request, 'teams/list.html', context)

@login_required
def aircraft_list(request):
    aircraft = Aircraft.objects.all()
    aircraft_types = Aircraft.AIRCRAFT_TYPES
    
    context = {
        'aircraft': aircraft,
        'aircraft_types': aircraft_types,
    }
    return render(request, 'aircraft/list.html', context)

# API views
class PartViewSet(viewsets.ModelViewSet):
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    
    @action(detail=False)
    def low_stock(self, request):
        parts = Part.objects.filter(stock__lt=5)
        serializer = self.get_serializer(parts, many=True)
        return Response(serializer.data)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    
    @action(detail=True, methods=['post'])
    def produce_part(self, request, pk=None):
        team = self.get_object()
        part_id = request.data.get('part')
        quantity = int(request.data.get('quantity', 1))

        try:
            part = Part.objects.get(id=part_id)
            
            # Check if team can produce this part type
            if not team.can_produce_part(part):
                return Response(
                    {'detail': 'Bu takım bu parçayı üretemez.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create production record
            production = Production.objects.create(
                team=team,
                part=part,
                quantity=quantity
            )
            
            # Update stock
            part.stock += quantity
            part.save()
            
            return Response({'detail': 'Parça başarıyla üretildi.'})
            
        except Part.DoesNotExist:
            return Response(
                {'detail': 'Parça bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True)
    def production_history(self, request, pk=None):
        team = self.get_object()
        productions = team.productions.all()
        serializer = ProductionSerializer(productions, many=True)
        return Response(serializer.data)

class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status', None)
        
        if status == 'in_production':
            queryset = queryset.filter(completed_at__isnull=True)
        elif status == 'completed':
            queryset = queryset.filter(completed_at__isnull=False)
            
        return queryset

    @action(detail=True, methods=['post'])
    def add_part(self, request, pk=None):
        aircraft = self.get_object()
        part_id = request.data.get('part')

        try:
            part = Part.objects.get(id=part_id)
            
            # Check if part is compatible
            if part.aircraft_type != aircraft.aircraft_type:
                return Response(
                    {'detail': 'Bu parça bu uçak tipi ile uyumlu değil.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if part is in stock
            if part.stock <= 0:
                return Response(
                    {'detail': 'Bu parça stokta yok.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add part to aircraft
            aircraft.parts.add(part)
            
            # Decrease stock
            part.stock -= 1
            part.save()
            
            return Response({'detail': 'Parça başarıyla eklendi.'})
            
        except Part.DoesNotExist:
            return Response(
                {'detail': 'Parça bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def complete_production(self, request, pk=None):
        aircraft = self.get_object()
        
        # Check if all required parts are added
        if not aircraft.is_complete:
            return Response(
                {'detail': 'Tüm gerekli parçalar eklenmeden üretim tamamlanamaz.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Complete production
        aircraft.complete_production()
        
        return Response({'detail': 'Uçak üretimi tamamlandı.'})

    @action(detail=True)
    def parts_summary(self, request, pk=None):
        aircraft = self.get_object()
        required_parts = Part.objects.filter(aircraft_type=aircraft.aircraft_type)
        
        parts_data = []
        for part in required_parts:
            parts_data.append({
                'id': part.id,
                'name': part.name,
                'is_available': aircraft.parts.filter(id=part.id).exists()
            })
        
        return Response({'parts': parts_data}) 