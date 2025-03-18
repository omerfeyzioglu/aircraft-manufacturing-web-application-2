from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F, Sum, Count, Q
from .models import Part, Team, Aircraft, Production, AircraftPart
from .models.constants import TEAM_TYPES, AIRCRAFT_TYPES, REQUIRED_PARTS
from .serializers import (
    PartSerializer, TeamSerializer, AircraftSerializer,
    ProductionSerializer, AircraftPartSerializer, UserSerializer
)
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.functions import TruncDate
import json
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from django.template.response import TemplateResponse
from django.contrib import admin
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate
from django.db import transaction

# Template views
@login_required
def home(request):
    """Home page view with dashboard data."""
    context = {}
    
    if request.user.is_authenticated:
        # Get counts
        context['teams_count'] = Team.objects.count()
        context['parts_count'] = Part.objects.count()
        context['aircraft_count'] = Aircraft.objects.count()
        context['production_count'] = Production.objects.count()
        
        # Get low stock parts
        context['low_stock_parts'] = Part.objects.filter(
            stock__lt=F('minimum_stock')
        ).order_by('stock')[:5]
        
        # Get recent productions
        context['recent_productions'] = Production.objects.select_related(
            'part', 'team'
        ).order_by('-created_at')[:5]
        
        # Get daily production data for chart
        # Get production data for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_production = Production.objects.filter(
            created_at__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Sum('quantity')
        ).order_by('date')
        
        # Create a dictionary with all dates in the last 30 days
        all_dates = {}
        current_date = thirty_days_ago.date()
        today = timezone.now().date()
        
        while current_date <= today:
            all_dates[current_date.strftime('%Y-%m-%d')] = 0
            current_date += timedelta(days=1)
        
        # Fill in the production data
        for item in daily_production:
            date_str = item['date'].strftime('%Y-%m-%d')
            all_dates[date_str] = item['total']
        
        # Convert to list of dicts for JSON serialization
        daily_production_data = []
        for date_str, total in all_dates.items():
            daily_production_data.append({
                'created_at__date': date_str,
                'total': total
            })
        
        # Sort by date
        daily_production_data.sort(key=lambda x: x['created_at__date'])
        
        context['daily_production'] = json.dumps(daily_production_data, cls=DjangoJSONEncoder)
    
    return render(request, 'home.html', context)

@login_required
def profile(request):
    user_team = request.user.team_members.first()
    context = {
        'user_team': user_team,
    }
    
    if user_team:
        if user_team.team_type == 'ASSEMBLY':
            context.update({
                'assembled_aircraft': Aircraft.objects.filter(assembly_team=user_team).order_by('-created_at')[:10],
                'total_assembled': Aircraft.objects.filter(assembly_team=user_team, completed_at__isnull=False).count(),
                'pending_assembly': Aircraft.objects.filter(assembly_team=user_team, completed_at__isnull=True).count(),
            })
        else:
            context.update({
                'recent_productions': Production.objects.filter(team=user_team).order_by('-created_at')[:10],
                'total_production': Production.objects.filter(team=user_team).aggregate(total=Sum('quantity'))['total'] or 0,
                'parts_produced': Production.objects.filter(team=user_team).values('part__name').annotate(total=Sum('quantity')),
            })
    
    return render(request, 'profile.html', context)

@login_required
def parts_list(request):
    parts = Part.objects.all()
    user_team = request.user.team_members.first()
    
    # Filtreleme
    team_type = request.GET.get('team_type')
    aircraft_type = request.GET.get('aircraft_type')
    stock_status = request.GET.get('stock_status')
    
    if team_type:
        parts = parts.filter(team_type=team_type)
    if aircraft_type:
        parts = parts.filter(aircraft_type=aircraft_type)
    if stock_status == 'low':
        parts = parts.filter(stock__lte=F('minimum_stock'))
    elif stock_status == 'out':
        parts = parts.filter(stock=0)
    
    context = {
        'parts': parts,
        'team_types': TEAM_TYPES,
        'aircraft_types': AIRCRAFT_TYPES,
        'user_team': user_team,
    }
    return render(request, 'parts/list.html', context)

@login_required
def teams_list(request):
    teams = Team.objects.annotate(
        members_count=Count('members')
    )
    
    # Filtreleme
    team_type = request.GET.get('team_type')
    if team_type:
        teams = teams.filter(team_type=team_type)
    
    context = {
        'teams': teams,
        'team_types': TEAM_TYPES,
    }
    return render(request, 'teams/list.html', context)

@login_required
def aircraft_list(request):
    # Sadece montaj takımı üyeleri ve süper kullanıcılar erişebilir
    user_team = request.user.team_members.first()
    
    # Süper kullanıcı değilse ve montaj takımında değilse erişimi engelle
    if not request.user.is_superuser and (not user_team or user_team.team_type != 'ASSEMBLY'):
        messages.error(
            request, 
            '<span style="color: red; font-weight: bold;">Bu sayfaya erişim yetkiniz bulunmamaktadır.</span>'
        )
        return redirect('production:home')
    
    aircraft = Aircraft.objects.all()
    
    # Filtreleme
    aircraft_type = request.GET.get('aircraft_type')
    status = request.GET.get('status')
    assembly_team = request.GET.get('assembly_team')
    
    if aircraft_type:
        aircraft = aircraft.filter(aircraft_type=aircraft_type)
    if status == 'complete':
        aircraft = aircraft.filter(completed_at__isnull=False)
    elif status == 'incomplete':
        aircraft = aircraft.filter(completed_at__isnull=True)
    if assembly_team:
        aircraft = aircraft.filter(assembly_team_id=assembly_team)
    
    # Montaj takımı kendi uçaklarını ve henüz bir takıma atanmamış uçakları görebilir
    if user_team and user_team.team_type == 'ASSEMBLY':
        aircraft = aircraft.filter(Q(assembly_team=user_team) | Q(assembly_team__isnull=True))
    
    # Calculate completion percentage for each aircraft
    for a in aircraft:
        required_parts_count = sum(REQUIRED_PARTS[a.aircraft_type].values())
        current_parts_count = a.parts.count()
        a.completion_percentage = int((current_parts_count / required_parts_count) * 100) if required_parts_count > 0 else 0
    
    context = {
        'aircraft': aircraft,
        'aircraft_types': AIRCRAFT_TYPES,
        'team_types': TEAM_TYPES,
        'assembly_teams': Team.objects.filter(team_type='ASSEMBLY'),
        'user_team': user_team,
    }
    return render(request, 'aircraft/list.html', context)

@login_required
def add_production(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    # Süper kullanıcılar için kontrol yapma
    if request.user.is_superuser:
        part_id = request.POST.get('part')
        quantity = request.POST.get('quantity')
        team_id = request.POST.get('team')
        
        try:
            with transaction.atomic():
                part = Part.objects.get(id=part_id)
                team = Team.objects.get(id=team_id)
                quantity = int(quantity)
                
                # Mevcut stok değerini saklayalım
                old_stock = part.stock
                
                if quantity <= 0:
                    return JsonResponse({'error': 'Quantity must be positive'}, status=400)
                
                # Montaj takımları parça üretemez
                if team.team_type == 'ASSEMBLY':
                    return JsonResponse({'error': 'Assembly teams cannot produce parts'}, status=403)
                
                # Check if team has members
                if team.members.count() == 0:
                    return JsonResponse({'error': 'Team has no members. Please add members to the team.'}, status=403)
                
                # Takım tipi ve parça tipinin uyumlu olması gerekir
                if team.team_type != part.team_type:
                    return JsonResponse({'error': f'{team.get_team_type_display()} team cannot produce {part.get_team_type_display()} parts'}, status=403)
                
                # Create production record
                production = Production.objects.create(
                    team=team,
                    part=part,
                    quantity=quantity,
                    created_by=request.user
                )
                
                # Güncel stok değerini al
                part.refresh_from_db()
                
                # Stok değişmediyse direkt SQL ile güncelleyelim
                if part.stock == old_stock:
                    # SQL direkt güncelleme yap
                    from django.db import connection
                    cursor = connection.cursor()
                    cursor.execute(
                        f"UPDATE {part._meta.db_table} SET stock = stock + %s, is_low_stock = CASE WHEN (stock + %s) < minimum_stock THEN True ELSE False END WHERE id = %s",
                        [quantity, quantity, part.id]
                    )
                    part.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully produced {quantity} {part.name}',
                'new_stock': part.stock
            })
            
        except Part.DoesNotExist:
            return JsonResponse({'error': 'Part not found'}, status=404)
        except Team.DoesNotExist:
            return JsonResponse({'error': 'Team not found'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

@login_required
def add_aircraft_part(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    # Süper kullanıcılar için kontrol yapma
    if request.user.is_superuser:
        aircraft_id = request.POST.get('aircraft')
        part_id = request.POST.get('part')
        
        try:
            aircraft = Aircraft.objects.get(id=aircraft_id)
            part = Part.objects.get(id=part_id)
            
            # Add part using the model method which includes validation
            try:
                aircraft_part = aircraft.add_part(part, request.user)
                
                # Check if aircraft is now complete
                is_complete = aircraft.is_complete
                missing_parts = aircraft.get_missing_parts()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully added {part.name} to aircraft',
                    'is_complete': is_complete,
                    'missing_parts': missing_parts
                })
                
            except ValidationError as e:
                return JsonResponse({'error': str(e)}, status=400)
            
        except (Aircraft.DoesNotExist, Part.DoesNotExist) as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # Check if user is in an assembly team
    user_team = request.user.team_members.first()
    if not user_team:
        return JsonResponse({'error': 'User is not assigned to a team'}, status=403)
    
    if user_team.team_type != 'ASSEMBLY':
        return JsonResponse({'error': 'Only assembly teams can add parts to aircraft'}, status=403)
    
    # Check if team has members
    if user_team.members.count() == 0:
        return JsonResponse({'error': 'Assembly team has no members. Please add members to the team.'}, status=403)
    
    aircraft_id = request.POST.get('aircraft')
    part_id = request.POST.get('part')
    
    try:
        # Check if the aircraft belongs to the user's team
        aircraft = Aircraft.objects.get(id=aircraft_id)
        
        if aircraft.assembly_team != user_team:
            return JsonResponse({'error': 'This aircraft is not assigned to your team'}, status=403)
        
        if aircraft.completed_at:
            return JsonResponse({'error': 'Cannot modify completed aircraft'}, status=400)
        
        part = Part.objects.get(id=part_id)
        
        # Add part using the model method which includes validation
        try:
            aircraft_part = aircraft.add_part(part, request.user)
            
            # Check if aircraft is now complete
            is_complete = aircraft.is_complete
            missing_parts = aircraft.get_missing_parts()
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully added {part.name} to aircraft',
                'is_complete': is_complete,
                'missing_parts': missing_parts
            })
            
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
    except (Aircraft.DoesNotExist, Part.DoesNotExist) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def get_required_parts(request, aircraft_id):
    # Sadece montaj takımı üyeleri ve süper kullanıcılar erişebilir
    user_team = request.user.team_members.first()
    
    # Süper kullanıcı değilse ve montaj takımında değilse erişimi engelle
    if not request.user.is_superuser and (not user_team or user_team.team_type != 'ASSEMBLY'):
        return JsonResponse({
            'error': 'Erişim Engellendi: Bu işlem sadece montaj takımı üyeleri ve yöneticiler tarafından gerçekleştirilebilir.',
            'status': 'error',
            'code': 403
        }, status=403)
    
    aircraft = get_object_or_404(Aircraft, id=aircraft_id)
    
    # Kullanıcının takımına göre erişimi kontrol et (süper kullanıcı için erişim serbest)
    if (not request.user.is_superuser and 
        user_team and 
        aircraft.assembly_team is not None and 
        aircraft.assembly_team != user_team):
        return JsonResponse({'error': 'Bu uçağa erişim yetkiniz bulunmamaktadır.'}, status=403)
    
    required = REQUIRED_PARTS[aircraft.aircraft_type]
    
    # Get current parts by team type
    current_parts = {}
    for team_type in required:
        current_parts[team_type] = aircraft.parts.filter(team_type=team_type).count()
    
    # Build required_parts dictionary for the template
    required_parts = {}
    for team_type, required_count in required.items():
        current_count = current_parts.get(team_type, 0)
        required_parts[team_type] = {
            'required': required_count,
            'current': current_count,
            'parts': []
        }
        
        # Add part details if needed
        for part in aircraft.parts.filter(team_type=team_type):
            required_parts[team_type]['parts'].append({
                'id': part.id,
                'name': part.name
            })
    
    # Build parts_info list for backward compatibility
    parts_info = []
    for team_type, required_count in required.items():
        current_count = current_parts.get(team_type, 0)
        parts_info.append({
            'team_type': team_type,
            'team_type_display': dict(TEAM_TYPES)[team_type],
            'required': required_count,
            'current': current_count,
            'remaining': required_count - current_count
        })
    
    # Calculate missing parts
    missing_parts = {}
    for team_type, required_count in required.items():
        current_count = current_parts.get(team_type, 0)
        if current_count < required_count:
            missing_parts[team_type] = required_count - current_count
    
    return JsonResponse({
        'aircraft_type': aircraft.get_aircraft_type_display(),
        'parts_info': parts_info,
        'required_parts': required_parts,
        'missing_parts': missing_parts,
        'is_complete': aircraft.is_complete
    })

# API views
@extend_schema_view(
    list=extend_schema(
        summary="Parça listesi",
        description="Tüm parçaları listeler. Takım tipi, uçak tipi ve stok durumuna göre filtrelenebilir.",
        parameters=[
            OpenApiParameter(name="team_type", description="Takım tipine göre filtrele", required=False, type=str),
            OpenApiParameter(name="aircraft_type", description="Uçak tipine göre filtrele", required=False, type=str),
            OpenApiParameter(name="stock_status", description="Stok durumuna göre filtrele (low, out)", required=False, type=str),
        ]
    ),
    retrieve=extend_schema(
        summary="Parça detayı",
        description="Belirli bir parçanın detaylarını gösterir."
    ),
    create=extend_schema(
        summary="Yeni parça oluştur",
        description="Yeni bir parça oluşturur. Kullanıcının takım tipine uygun parça oluşturulabilir."
    ),
    update=extend_schema(
        summary="Parça güncelle",
        description="Bir parçayı günceller. Sadece stok ve minimum stok değerleri güncellenebilir."
    ),
    destroy=extend_schema(
        summary="Parça sil",
        description="Bir parçayı siler. Sadece kendi takımınızın parçalarını silebilirsiniz."
    ),
)
class PartViewSet(viewsets.ModelViewSet):
    """
    Parça yönetimi için API endpoint'leri.
    
    Parçaların listelenmesi, oluşturulması, güncellenmesi ve silinmesi işlemlerini sağlar.
    Takım tipine, uçak tipine ve stok durumuna göre filtreleme yapılabilir.
    """
    queryset = Part.objects.all().select_related()
    serializer_class = PartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Kullanıcının takımına göre parçaları filtreler.
        Montaj takımı üyeleri tüm parçaları görebilir.
        Diğer takım üyeleri sadece kendi takım tiplerine ait parçaları görebilir.
        Süper kullanıcı tüm parçaları görebilir.
        """
        queryset = self.queryset
        
        # Takım tipine göre filtrele
        team_type = self.request.query_params.get('team_type')
        if team_type:
            queryset = queryset.filter(team_type=team_type)
        
        # Uçak tipine göre filtrele
        aircraft_type = self.request.query_params.get('aircraft_type')
        if aircraft_type:
            queryset = queryset.filter(aircraft_type=aircraft_type)
        
        # Stok durumuna göre filtrele
        stock_status = self.request.query_params.get('stock_status')
        if stock_status == 'low':
            queryset = queryset.filter(is_low_stock=True)
        elif stock_status == 'ok':
            queryset = queryset.filter(is_low_stock=False)
        
        # Süper kullanıcı ise tüm parçaları görebilir
        if self.request.user.is_superuser:
            return queryset
            
        # Kullanıcının takımına göre filtrele
        user_team = Team.objects.filter(members=self.request.user).first()
        if user_team and user_team.team_type != 'ASSEMBLY':
            queryset = queryset.filter(team_type=user_team.team_type)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Parça oluşturma işlemini gerçekleştirir.
        Süper kullanıcılar için takım kontrolü yapmaz.
        """
        # Request verisini değiştirmek için kopyalayalım
        request_data = request.data.copy()
        
        # Süper kullanıcı her türlü parça ekleyebilir
        if request.user.is_superuser:
            # Auto-generate part name based on team type and aircraft type
            team_type = request_data.get('team_type')
            aircraft_type = request_data.get('aircraft_type')
            
            if team_type and aircraft_type:
                # Create a temporary Part instance to get the expected name
                temp_part = Part(team_type=team_type, aircraft_type=aircraft_type)
                request_data['name'] = temp_part.expected_name
            
            serializer = self.get_serializer(data=request_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        # Get user's team
        user_team = request.user.team_members.first()
        
        # Check if user has a team
        if not user_team:
            return Response(
                {'detail': 'Kullanıcı bir takıma atanmamış.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Montaj takımları parça üretemez
        if user_team.team_type == 'ASSEMBLY':
            return Response(
                {'detail': 'Montaj takımları parça üretemez.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Kullanıcı sadece kendi takım tipine uygun parça ekleyebilir
        team_type = request_data.get('team_type')
        if team_type != user_team.team_type:
            return Response(
                {'detail': f'Sadece kendi takım tipiniz ({user_team.get_team_type_display()}) için parça ekleyebilirsiniz.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Auto-generate part name based on team type and aircraft type
        aircraft_type = request_data.get('aircraft_type')
        if team_type and aircraft_type:
            # Create a temporary Part instance to get the expected name
            temp_part = Part(team_type=team_type, aircraft_type=aircraft_type)
            request_data['name'] = temp_part.expected_name
        
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """
        Parça güncelleme işlemini gerçekleştirir.
        Süper kullanıcı için izin kontrolü yapmaz.
        """
        # Request verisini değiştirmek için kopyalayalım
        request_data = request.data.copy()
        
        # Süper kullanıcı için kontrol yapma
        if request.user.is_superuser:
            # Don't allow changing team_type or aircraft_type
            instance = self.get_object()
            if 'team_type' in request_data and request_data['team_type'] != instance.team_type:
                return Response(
                    {'detail': 'Parçanın takım tipini değiştiremezsiniz.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if 'aircraft_type' in request_data and request_data['aircraft_type'] != instance.aircraft_type:
                return Response(
                    {'detail': 'Parçanın uçak tipini değiştiremezsiniz.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Don't allow changing name
            if 'name' in request_data and request_data['name'] != instance.name:
                return Response(
                    {'detail': 'Parçanın adını değiştiremezsiniz.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(instance, data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        
        # Get user's team
        user_team = request.user.team_members.first()
        
        # Check if user has a team
        if not user_team and not request.user.is_staff:
            return Response(
                {'detail': 'Kullanıcı bir takıma atanmamış.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Only staff or team members can update their parts
        instance = self.get_object()
        if not request.user.is_staff and user_team.team_type != instance.team_type:
            return Response(
                {'detail': 'Sadece kendi takımınızın parçalarını güncelleyebilirsiniz.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Don't allow changing team_type or aircraft_type
        if 'team_type' in request_data and request_data['team_type'] != instance.team_type:
            return Response(
                {'detail': 'Parçanın takım tipini değiştiremezsiniz.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if 'aircraft_type' in request_data and request_data['aircraft_type'] != instance.aircraft_type:
            return Response(
                {'detail': 'Parçanın uçak tipini değiştiremezsiniz.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Don't allow changing name
        if 'name' in request_data and request_data['name'] != instance.name:
            return Response(
                {'detail': 'Parçanın adını değiştiremezsiniz.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(instance, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Düşük stoklu parçalar",
        description="Stok miktarı minimum stok seviyesinin altında olan parçaları listeler."
    )
    @action(detail=False)
    def low_stock(self, request):
        """
        Düşük stoklu parçaları listeler.
        
        Stok miktarı minimum stok seviyesinin altında olan parçaları döndürür.
        """
        parts = Part.objects.filter(stock__lt=F('minimum_stock'))
        serializer = self.get_serializer(parts, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Parça kullanım bilgisi",
        description="Bir parçanın hangi uçaklarda kullanıldığını gösterir."
    )
    @action(detail=True, methods=['get'], url_path='usage')
    def usage(self, request, pk=None):
        """
        Parça kullanım bilgisini gösterir.
        
        Bir parçanın hangi uçaklarda kullanıldığını, ne zaman ve kim tarafından eklendiğini gösterir.
        """
        part = self.get_object()
        
        # Get all aircraft that use this part
        aircraft_parts = AircraftPart.objects.filter(part=part).select_related('aircraft', 'added_by')
        
        usage_data = []
        for aircraft_part in aircraft_parts:
            aircraft = aircraft_part.aircraft
            usage_data.append({
                'aircraft_id': aircraft.id,
                'aircraft_type': aircraft.aircraft_type,
                'aircraft_name': dict(AIRCRAFT_TYPES).get(aircraft.aircraft_type, ''),
                'assembly_team': dict(TEAM_TYPES).get(aircraft.assembly_team, ''),
                'status': 'Tamamlandı' if aircraft.completed_at else 'Devam Ediyor',
                'added_at': aircraft_part.added_at.strftime('%Y-%m-%d %H:%M'),
                'added_by': aircraft_part.added_by.get_full_name() if aircraft_part.added_by else 'Sistem'
            })
        
        return Response({
            'part_id': part.id,
            'part_name': part.name,
            'team_type': part.team_type,
            'team_name': dict(TEAM_TYPES).get(part.team_type, ''),
            'aircraft_type': part.aircraft_type,
            'aircraft_name': dict(AIRCRAFT_TYPES).get(part.aircraft_type, ''),
            'stock': part.stock,
            'minimum_stock': part.minimum_stock,
            'usage_count': len(usage_data),
            'usage': usage_data
        })

@extend_schema_view(
    list=extend_schema(
        summary="Takım listesi",
        description="Tüm takımları listeler. Takım tipine göre filtrelenebilir.",
        parameters=[
            OpenApiParameter(name="team_type", description="Takım tipine göre filtrele", required=False, type=str),
        ]
    ),
    retrieve=extend_schema(
        summary="Takım detayı",
        description="Belirli bir takımın detaylarını gösterir."
    ),
    create=extend_schema(
        summary="Yeni takım oluştur",
        description="Yeni bir takım oluşturur."
    ),
    update=extend_schema(
        summary="Takım güncelle",
        description="Bir takımı günceller."
    ),
    destroy=extend_schema(
        summary="Takım sil",
        description="Bir takımı siler."
    ),
)
class TeamViewSet(viewsets.ModelViewSet):
    """
    Takım yönetimi için API endpoint'leri.
    
    Takımların listelenmesi, oluşturulması, güncellenmesi ve silinmesi işlemlerini sağlar.
    Takım tipine göre filtreleme yapılabilir.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    
    def get_queryset(self):
        """
        Takımları filtreler ve ek bilgiler ekler.
        
        Takım tipine göre filtreleme yapar ve her takım için üye sayısı ve toplam üretim miktarı bilgilerini ekler.
        """
        queryset = Team.objects.annotate(
            member_count=Count('members'),
            total_production=Sum('productions__quantity', default=0)
        )
        
        team_type = self.request.query_params.get('team_type')
        if team_type:
            queryset = queryset.filter(team_type=team_type)
            
        return queryset
    
    @extend_schema(
        summary="Takıma üye ekle",
        description="Bir takıma yeni bir üye ekler.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'user': {'type': 'integer', 'description': 'Eklenecek kullanıcının ID\'si'}
                },
                'required': ['user']
            }
        }
    )
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """
        Takıma üye ekler.
        
        Belirtilen kullanıcıyı takıma ekler.
        """
        team = self.get_object()
        user_id = request.data.get('user')
        
        try:
            user = User.objects.get(id=user_id)
            team.members.add(user)
            return Response({'detail': f'Kullanıcı {user.username} takıma eklendi.'})
        except User.DoesNotExist:
            return Response(
                {'detail': 'Kullanıcı bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Takımdan üye çıkar",
        description="Bir takımdan bir üyeyi çıkarır.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'user': {'type': 'integer', 'description': 'Çıkarılacak kullanıcının ID\'si'}
                },
                'required': ['user']
            }
        }
    )
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """
        Takımdan üye çıkarır.
        
        Belirtilen kullanıcıyı takımdan çıkarır.
        """
        team = self.get_object()
        user_id = request.data.get('user')
        
        try:
            user = User.objects.get(id=user_id)
            if user in team.members.all():
                team.members.remove(user)
                return Response({'detail': f'Kullanıcı {user.username} takımdan çıkarıldı.'})
            else:
                return Response(
                    {'detail': 'Kullanıcı bu takımda değil.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {'detail': 'Kullanıcı bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Takım üyeleri",
        description="Bir takımın tüm üyelerini listeler."
    )
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """
        Takım üyelerini listeler.
        
        Bir takımın tüm üyelerini döndürür.
        """
        team = self.get_object()
        members = team.members.all()
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Müsait kullanıcılar",
        description="Herhangi bir takıma atanmamış kullanıcıları listeler."
    )
    @action(detail=False, methods=['get'])
    def available_users(self, request):
        """
        Müsait kullanıcıları listeler.
        
        Herhangi bir takıma atanmamış kullanıcıları döndürür.
        """
        users_in_teams = User.objects.filter(team_members__isnull=False).distinct()
        available_users = User.objects.exclude(id__in=users_in_teams.values_list('id', flat=True))
        serializer = UserSerializer(available_users, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Parça üret",
        description="Takım tarafından parça üretimi yapar.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'part': {'type': 'integer', 'description': 'Üretilecek parçanın ID\'si'},
                    'quantity': {'type': 'integer', 'description': 'Üretilecek miktar'}
                },
                'required': ['part', 'quantity']
            }
        }
    )
    @action(detail=True, methods=['post'])
    def produce_part(self, request, pk=None):
        """
        Parça üretimi yapar.
        
        Takım tarafından belirtilen parçanın üretimini yapar ve stok miktarını artırır.
        """
        team = self.get_object()
        part_id = request.data.get('part')
        quantity = int(request.data.get('quantity', 1))

        # Check if team has members
        if team.members.count() == 0:
            return Response(
                {'detail': 'Takımda üye bulunmamaktadır. Takıma üye ekleyin.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Kullanıcının bu takımda olup olmadığını kontrol et
        if not request.user.is_superuser and not team.members.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'Bu takımda değilsiniz ve bu takım adına üretim yapamazsınız.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            part = Part.objects.get(id=part_id)
            
            # Mevcut stok değerini al (başlangıç değeri)
            old_stock = part.stock
            
            # Check if team can produce this part type
            if not team.can_produce_part(part):
                return Response(
                    {'detail': 'Bu takım bu parçayı üretemez.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create production record
            with transaction.atomic():
                # 1. Üretim kaydı oluştur (stok artışı yapılmadan)
                production = Production.objects.create(
                    team=team,
                    part=part,
                    quantity=quantity,
                    created_by=request.user
                )
                
                # 2. Güncel stok değerini al ve artışı kontrol et
                part.refresh_from_db()
                
                # 3. Eğer stok değişmediyse, direkt SQL ile güncelle
                if part.stock == old_stock:
                    # SQL direkt güncelleme yap
                    from django.db import connection
                    cursor = connection.cursor()
                    table_name = part._meta.db_table
                    
                    # Stok artırıp low stock durumunu güncelleyen SQL sorgusu
                    query = f"""
                        UPDATE {table_name}
                        SET stock = stock + %s,
                            is_low_stock = CASE WHEN (stock + %s) < minimum_stock THEN True ELSE False END
                        WHERE id = %s
                    """
                    cursor.execute(query, [quantity, quantity, part_id])
                    
                    # Parça nesnesini yenile
                    part.refresh_from_db()
            
            return Response({
                'detail': 'Parça başarıyla üretildi.',
                'new_stock': part.stock,
                'old_stock': old_stock,
                'production_id': production.id
            })
            
        except Part.DoesNotExist:
            return Response(
                {'detail': 'Parça bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': f'Bir hata oluştu: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Üretim geçmişi",
        description="Takımın üretim geçmişini listeler."
    )
    @action(detail=True, methods=['get'], url_path='production-history')
    def production_history(self, request, pk=None):
        """
        Üretim geçmişini listeler.
        
        Takımın tüm üretim kayıtlarını döndürür.
        """
        team = self.get_object()
        productions = team.productions.all()
        serializer = ProductionSerializer(productions, many=True)
        return Response(serializer.data)

@extend_schema_view(
    list=extend_schema(
        summary="Uçak listesi",
        description="Tüm uçakları listeler. Uçak tipi, durum ve montaj takımına göre filtrelenebilir.",
        parameters=[
            OpenApiParameter(name="aircraft_type", description="Uçak tipine göre filtrele", required=False, type=str),
            OpenApiParameter(name="status", description="Duruma göre filtrele (in_production, completed)", required=False, type=str),
        ]
    ),
    retrieve=extend_schema(
        summary="Uçak detayı",
        description="Belirli bir uçağın detaylarını gösterir."
    ),
    create=extend_schema(
        summary="Yeni uçak oluştur",
        description="Yeni bir uçak oluşturur. Sadece montaj takımları uçak oluşturabilir."
    ),
    update=extend_schema(
        summary="Uçak güncelle",
        description="Bir uçağı günceller."
    ),
    destroy=extend_schema(
        summary="Uçak sil",
        description="Bir uçağı siler. Sadece montaj takımları uçak silebilir."
    ),
)
class AircraftViewSet(viewsets.ModelViewSet):
    """
    Uçak yönetimi için API endpoint'leri.
    
    Uçakların listelenmesi, oluşturulması, güncellenmesi ve silinmesi işlemlerini sağlar.
    Uçak tipine, duruma ve montaj takımına göre filtreleme yapılabilir.
    """
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    
    def get_permissions(self):
        """
        Sadece montaj takımı üyeleri ve süper kullanıcılar erişebilir.
        """
        permission_classes = [IsAuthenticated]
        
        # Süper kullanıcı değilse, özel izin kontrolü yap
        if not self.request.user.is_superuser:
            permission_classes.append(IsAssemblyTeamMember)
            
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Uçakları filtreler.
        
        Uçak tipi, durum ve montaj takımına göre filtreleme yapar.
        """
        queryset = super().get_queryset()
        
        # Filter by aircraft type
        aircraft_type = self.request.query_params.get('aircraft_type')
        if aircraft_type:
            queryset = queryset.filter(aircraft_type=aircraft_type)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status == 'in_production':
            queryset = queryset.filter(completed_at__isnull=True)
        elif status == 'completed':
            queryset = queryset.filter(completed_at__isnull=False)
            
        # Filter by assembly team
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            user_team = self.request.user.team_members.first()
            if user_team and user_team.team_type == 'ASSEMBLY':
                queryset = queryset.filter(Q(assembly_team=user_team) | Q(assembly_team__isnull=True))
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Uçak oluşturma işlemini gerçekleştirir.
        Süper kullanıcılar için takım kontrolü yapmaz.
        """
        # Süper kullanıcı her türlü uçak ekleyebilir
        if request.user.is_superuser:
            return super().create(request, *args, **kwargs)
            
        # Get user's team
        user_team = request.user.team_members.first()
        
        # Check if user has a team
        if not user_team:
            return Response(
                {'detail': 'Kullanıcı bir takıma atanmamış.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Only assembly teams can create aircraft
        if user_team.team_type != 'ASSEMBLY' and not request.user.is_staff:
            return Response(
                {'detail': 'Sadece montaj takımları uçak oluşturabilir.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if assembly team has members
        if user_team.members.count() == 0:
            return Response(
                {'detail': 'Montaj takımında üye bulunmamaktadır. Takıma üye ekleyin.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Set assembly team to user's team
        request.data['assembly_team'] = user_team.id
        
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        aircraft = self.get_object()
        
        # Get user's team
        user_team = request.user.team_members.first()
        
        # Check if user has a team
        if not user_team and not request.user.is_staff:
            return Response(
                {'detail': 'Kullanıcı bir takıma atanmamış.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Only assembly teams can delete aircraft
        if user_team.team_type != 'ASSEMBLY' and not request.user.is_staff:
            return Response(
                {'detail': 'Sadece montaj takımları uçak silebilir.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if assembly team has members
        if user_team and user_team.members.count() == 0:
            return Response(
                {'detail': 'Montaj takımında üye bulunmamaktadır. Takıma üye ekleyin.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user's team is assigned to this aircraft
        if aircraft.assembly_team != user_team and not request.user.is_staff:
            return Response(
                {'detail': 'Sadece atanmış montaj takımı uçak silebilir.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if aircraft is completed
        if aircraft.completed_at:
            return Response(
                {'detail': 'Tamamlanmış uçaklar silinemez.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete aircraft (this will return parts to stock via the model's delete method)
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Uçağa parça ekle",
        description="Bir uçağa parça ekler.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'part': {'type': 'integer', 'description': 'Eklenecek parçanın ID\'si'}
                },
                'required': ['part']
            }
        }
    )
    @action(detail=True, methods=['post'])
    def add_part(self, request, pk=None):
        """
        Uçağa parça ekler.
        
        Belirtilen parçayı uçağa ekler. Sadece montaj takımları parça ekleyebilir.
        """
        aircraft = self.get_object()
        part_id = request.data.get('part')

        # Get user's team
        user_team = request.user.team_members.first()
        
        # Check if user has a team
        if not user_team:
            return Response(
                {'detail': 'Kullanıcı bir takıma atanmamış.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Only assembly teams can add parts to aircraft
        if user_team.team_type != 'ASSEMBLY' and not request.user.is_staff:
            return Response(
                {'detail': 'Sadece montaj takımları uçağa parça ekleyebilir.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if assembly team has members
        if user_team.members.count() == 0:
            return Response(
                {'detail': 'Montaj takımında üye bulunmamaktadır. Takıma üye ekleyin.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user's team is assigned to this aircraft
        if aircraft.assembly_team != user_team and not request.user.is_staff:
            return Response(
                {'detail': 'Sadece atanmış montaj takımı uçağa parça ekleyebilir.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            part = Part.objects.get(id=part_id)
            
            # Add part using the model method which includes validation
            try:
                aircraft_part = aircraft.add_part(part, request.user)
                
                # Return updated aircraft information
                return Response({
                    'detail': f'{part.name} parçası başarıyla eklendi.',
                    'is_complete': aircraft.is_complete,
                    'missing_parts': aircraft.get_missing_parts()
                })
                
            except ValidationError as e:
                return Response(
                    {'detail': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except Part.DoesNotExist:
            return Response(
                {'detail': 'Parça bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Üretimi tamamla",
        description="Uçak üretimini tamamlar."
    )
    @action(detail=True, methods=['post'])
    def complete_production(self, request, pk=None):
        """
        Üretimi tamamlar.
        
        Uçak üretimini tamamlar. Tüm gerekli parçalar eklenmiş olmalıdır.
        """
        aircraft = self.get_object()
        
        # Get user's team
        user_team = request.user.team_members.first()
        
        # Check if user has a team
        if not user_team:
            return Response(
                {'detail': 'Kullanıcı bir takıma atanmamış.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Only assembly teams can complete aircraft production
        if user_team.team_type != 'ASSEMBLY' and not request.user.is_staff:
            return Response(
                {'detail': 'Sadece montaj takımları üretimi tamamlayabilir.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if assembly team has members
        if user_team.members.count() == 0:
            return Response(
                {'detail': 'Montaj takımında üye bulunmamaktadır. Takıma üye ekleyin.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user's team is assigned to this aircraft
        if aircraft.assembly_team != user_team and not request.user.is_staff:
            return Response(
                {'detail': 'Sadece atanmış montaj takımı üretimi tamamlayabilir.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if all required parts are added
        if not aircraft.is_complete:
            return Response(
                {'detail': 'Tüm gerekli parçalar eklenmeden üretim tamamlanamaz.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Complete production
        aircraft.completed_at = timezone.now()
        aircraft.save()
        
        return Response({'detail': 'Uçak üretimi tamamlandı.'})

    @extend_schema(
        summary="Parça özeti",
        description="Uçağın parça özetini gösterir."
    )
    @action(detail=True, methods=['get'], url_path='parts-summary')
    def parts_summary(self, request, pk=None):
        """
        Parça özetini gösterir.
        
        Uçağın mevcut parçalarını, eksik parçalarını ve tamamlanma durumunu gösterir.
        """
        aircraft = self.get_object()
        
        # Get required parts based on aircraft type
        required_parts = {}
        for team_type, team_name in TEAM_TYPES:
            if team_type != 'ASSEMBLY':  # Assembly team doesn't produce parts
                required_parts[team_type] = {
                    'team': team_name,
                    'required': REQUIRED_PARTS[aircraft.aircraft_type][team_type],
                    'current': 0,
                    'remaining': REQUIRED_PARTS[aircraft.aircraft_type][team_type],
                    'completion': 0
                }
        
        # Get current parts
        current_parts = []
        for aircraft_part in aircraft.aircraft_parts.select_related('part', 'added_by').all():
            part = aircraft_part.part
            team_type = part.team_type
            
            if team_type in required_parts:
                required_parts[team_type]['current'] += 1
                required_parts[team_type]['remaining'] = max(0, required_parts[team_type]['required'] - required_parts[team_type]['current'])
                required_parts[team_type]['completion'] = int((required_parts[team_type]['current'] / required_parts[team_type]['required']) * 100)
            
            current_parts.append({
                'id': part.id,
                'name': part.name,
                'team_type': part.team_type,
                'team_name': dict(TEAM_TYPES).get(part.team_type, ''),
                'added_at': aircraft_part.added_at.strftime('%Y-%m-%d %H:%M'),
                'added_by': aircraft_part.added_by.get_full_name() if aircraft_part.added_by else 'Sistem'
            })
        
        # Check if all required parts are complete
        is_complete = all(part_info['current'] >= part_info['required'] for part_info in required_parts.values())
        
        return Response({
            'required_parts': list(required_parts.values()),
            'current_parts': current_parts,
            'missing_parts': sum(part_info['remaining'] for part_info in required_parts.values()),
            'is_complete': is_complete
        })

    @extend_schema(
        summary="Üretim geçmişi",
        description="Uçağın üretim geçmişini gösterir."
    )
    @action(detail=True, methods=['get'], url_path='production-history')
    def production_history(self, request, pk=None):
        """
        Üretim geçmişini gösterir.
        
        Uçağa eklenen tüm parçaların geçmişini gösterir.
        """
        aircraft = self.get_object()
        
        # Get all parts added to this aircraft with timestamp and user info
        history = []
        for aircraft_part in aircraft.aircraft_parts.select_related('part', 'added_by').order_by('-added_at'):
            part = aircraft_part.part
            history.append({
                'part_id': part.id,
                'part_name': part.name,
                'team_type': part.team_type,
                'team_name': dict(TEAM_TYPES).get(part.team_type, ''),
                'aircraft_type': part.aircraft_type,
                'aircraft_name': dict(AIRCRAFT_TYPES).get(part.aircraft_type, ''),
                'added_at': aircraft_part.added_at.strftime('%Y-%m-%d %H:%M'),
                'added_by': aircraft_part.added_by.get_full_name() if aircraft_part.added_by else 'Sistem',
                'user_id': aircraft_part.added_by.id if aircraft_part.added_by else None
            })
        
        return Response({
            'aircraft_id': aircraft.id,
            'aircraft_type': aircraft.aircraft_type,
            'aircraft_name': dict(AIRCRAFT_TYPES).get(aircraft.aircraft_type, ''),
            'history': history
        })

    @extend_schema(
        summary="Kullanılabilir parçalar",
        description="Uçağa eklenebilecek parçaları listeler."
    )
    @action(detail=True, methods=['get'], url_path='available-parts')
    def available_parts(self, request, pk=None):
        """
        Kullanılabilir parçaları listeler.
        
        Uçağa eklenebilecek, stokta bulunan ve uyumlu parçaları listeler.
        """
        aircraft = self.get_object()
        
        # Get parts that are compatible with this aircraft and have stock
        available_parts = Part.objects.filter(
            aircraft_type=aircraft.aircraft_type,
            stock__gt=0
        )
        
        # Get current parts by team type
        current_parts = {}
        for team_type in REQUIRED_PARTS[aircraft.aircraft_type]:
            current_parts[team_type] = aircraft.parts.filter(team_type=team_type).count()
        
        # Filter out parts that have reached their limit
        filtered_parts = []
        for part in available_parts:
            team_type = part.team_type
            required = REQUIRED_PARTS[aircraft.aircraft_type][team_type]
            current = current_parts.get(team_type, 0)
            
            if current < required:
                filtered_parts.append(part)
        
        serializer = PartSerializer(filtered_parts, many=True)
        return Response({'parts': serializer.data})

@login_required
def dashboard(request):
    """Ana dashboard görünümü."""
    user_team = Team.objects.filter(members=request.user).first()
    
    # Kullanıcı süper kullanıcı değilse ve takıma atanmamışsa uyarı göster
    if not request.user.is_superuser and not user_team:
        messages.warning(
            request, 
            '<div style="color: red; font-weight: bold; font-size: 16px; text-align: center; padding: 10px; border: 2px solid red; border-radius: 5px; background-color: #ffeeee;">'
            '<i class="fas fa-exclamation-triangle"></i> '
            'Herhangi bir takıma üye değilsiniz. Lütfen admin ile iletişime geçiniz.'
            '</div>'
        )
    
    # Kullanıcının takımına göre verileri filtrele
    context = {
        'user_team': user_team,
        'total_parts': Part.objects.count(),
        'total_aircraft': Aircraft.objects.count(),
        'completed_aircraft': Aircraft.objects.filter(is_complete=True).count(),
        'low_stock_parts': Part.objects.filter(is_low_stock=True).count(),
    }
    
    if user_team:
        if user_team.team_type == 'ASSEMBLY':
            # Montaj takımı için uçak verileri
            team_aircraft = Aircraft.objects.filter(assembly_team=user_team)
            unassigned_aircraft = Aircraft.objects.filter(assembly_team__isnull=True)
            
            context.update({
                'team_aircraft': team_aircraft.count(),
                'team_completed_aircraft': team_aircraft.filter(is_complete=True).count(),
                'recent_aircraft': team_aircraft.order_by('-created_at')[:5],
                'unassigned_aircraft_count': unassigned_aircraft.count(),
                'recent_unassigned_aircraft': unassigned_aircraft.order_by('-created_at')[:5],
            })
        else:
            # Üretim takımları için parça verileri
            context.update({
                'team_parts': Part.objects.filter(team_type=user_team.team_type).count(),
                'team_production': Production.objects.filter(team=user_team).aggregate(
                    total=Sum('quantity')
                )['total'] or 0,
                'recent_production': Production.objects.filter(
                    team=user_team
                ).order_by('-created_at')[:5],
            })
    
    return render(request, 'production/dashboard.html', context)

@login_required
def part_list(request):
    """Parça listesi görünümü."""
    # Kullanıcı süper kullanıcı değilse ve takıma atanmamışsa uyarı göster
    user_team = Team.objects.filter(members=request.user).first()
    if not request.user.is_superuser and not user_team:
        messages.warning(
            request, 
            '<div style="color: red; font-weight: bold; font-size: 16px; text-align: center; padding: 10px; border: 2px solid red; border-radius: 5px; background-color: #ffeeee;">'
            '<i class="fas fa-exclamation-triangle"></i> '
            'Herhangi bir takıma üye değilsiniz. Lütfen admin ile iletişime geçiniz.'
            '</div>'
        )
    
    # Kullanıcının takımına göre parçaları filtrele (süper kullanıcı için tüm parçalar)
    if not request.user.is_superuser and user_team and user_team.team_type != 'ASSEMBLY':
        parts = Part.objects.filter(team_type=user_team.team_type)
    else:
        parts = Part.objects.all()
    
    context = {
        'parts': parts,
        'user_team': user_team,
    }
    return render(request, 'production/part_list.html', context)

@login_required
def aircraft_detail(request, pk):
    """Uçak detay görünümü."""
    # Sadece montaj takımı üyeleri ve süper kullanıcılar erişebilir
    user_team = Team.objects.filter(members=request.user).first()
    
    # Süper kullanıcı değilse ve montaj takımında değilse erişimi engelle
    if not request.user.is_superuser and (not user_team or user_team.team_type != 'ASSEMBLY'):
        messages.error(
            request, 
            '<span style="color: red; font-weight: bold;">Bu sayfaya erişim yetkiniz bulunmamaktadır.</span>'
        )
        return redirect('production:home')
    
    aircraft = get_object_or_404(Aircraft, pk=pk)
    
    # Kullanıcının takımına göre erişimi kontrol et (süper kullanıcı için erişim serbest)
    if (not request.user.is_superuser and 
        user_team and 
        aircraft.assembly_team is not None and 
        aircraft.assembly_team != user_team):
        # Kullanıcı sadece kendi takımının uçaklarını ve atanmamış uçakları görebilir
        return render(request, 'production/access_denied.html')
    
    context = {
        'aircraft': aircraft,
        'parts': AircraftPart.objects.filter(aircraft=aircraft),
        'missing_parts': aircraft.get_missing_parts(),
        'user_team': user_team,
    }
    return render(request, 'production/aircraft_detail.html', context)

class IsTeamMemberOrReadOnly(permissions.BasePermission):
    """
    Takım üyelerine yazma izni, diğerlerine sadece okuma izni veren özel izin sınıfı.
    """
    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS isteklerine izin ver
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Süper kullanıcıya her zaman izin ver
        if request.user.is_superuser:
            return True
        
        # Kullanıcının bir takımı var mı kontrol et
        return Team.objects.filter(members=request.user).exists()
    
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS isteklerine izin ver
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Süper kullanıcıya her zaman izin ver
        if request.user.is_superuser:
            return True
        
        # Takım nesnesi için, sadece takım üyeleri değişiklik yapabilir
        if isinstance(obj, Team):
            return obj.members.filter(id=request.user.id).exists()
        
        # Parça nesnesi için, sadece ilgili takım tipindeki takım üyeleri değişiklik yapabilir
        if isinstance(obj, Part):
            user_team = Team.objects.filter(members=request.user).first()
            return user_team and user_team.team_type == obj.team_type
        
        # Uçak nesnesi için, sadece montaj takımı üyeleri değişiklik yapabilir
        if isinstance(obj, Aircraft):
            user_team = Team.objects.filter(members=request.user).first()
            return user_team and user_team.team_type == 'ASSEMBLY' and obj.assembly_team == user_team
        
        # Üretim nesnesi için, sadece ilgili takım üyeleri değişiklik yapabilir
        if isinstance(obj, Production):
            return obj.team.members.filter(id=request.user.id).exists()
        
        # AircraftPart nesnesi için, sadece montaj takımı üyeleri değişiklik yapabilir
        if isinstance(obj, AircraftPart):
            user_team = Team.objects.filter(members=request.user).first()
            return user_team and user_team.team_type == 'ASSEMBLY' and obj.aircraft.assembly_team == user_team
        
        return False 

class IsAssemblyTeamMember(permissions.BasePermission):
    """
    Sadece montaj takımı üyelerine erişim izni veren özel izin sınıfı.
    """
    def has_permission(self, request, view):
        # Süper kullanıcıya her zaman izin ver
        if request.user.is_superuser:
            return True
        
        # Kullanıcının bir takımı var mı kontrol et
        user_team = Team.objects.filter(members=request.user).first()
        
        # Sadece montaj takımı üyelerine izin ver
        return user_team and user_team.team_type == 'ASSEMBLY'
    
    def has_object_permission(self, request, view, obj):
        # Süper kullanıcıya her zaman izin ver
        if request.user.is_superuser:
            return True
        
        # Kullanıcının bir takımı var mı kontrol et
        user_team = Team.objects.filter(members=request.user).first()
        
        # Sadece montaj takımı üyelerine izin ver
        if not user_team or user_team.team_type != 'ASSEMBLY':
            return False
        
        # Uçak nesnesi için, sadece kendi takımının uçaklarını ve atanmamış uçakları görebilir
        if isinstance(obj, Aircraft):
            return obj.assembly_team is None or obj.assembly_team == user_team
        
        return True

# Takım kontrolü için middleware
class TeamCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Giriş yapmış kullanıcılar için takım kontrolü yap
        if request.user.is_authenticated and not request.user.is_superuser:
            # Admin sayfasına erişim için kontrol yapma
            if not request.path.startswith('/admin/'):
                # Kullanıcının bir takımı var mı kontrol et
                user_team = Team.objects.filter(members=request.user).first()
                if not user_team:
                    # Takımı olmayan kullanıcıyı çıkış yaptır
                    from django.contrib.auth import logout
                    from django.contrib import messages
                    logout(request)
                    messages.error(
                        request, 
                        'Sisteme giriş yapabilmek için bir takıma atanmış olmanız gerekmektedir. '
                        'Lütfen sistem yöneticisi (admin) ile iletişime geçiniz.'
                    )
                    # Login sayfasına yönlendir
                    from django.shortcuts import redirect
                    return redirect('login')
        
        response = self.get_response(request)
        return response

class CustomLoginView(LoginView):
    """
    Takıma atanmamış kullanıcıların girişini engelleyen özel login view.
    """
    template_name = 'login.html'

    def form_valid(self, form):
        """
        Kullanıcı doğrulandı, giriş yapılmadan önce takım üyeliğini kontrol et.
        Takımı olmayan kullanıcıların girişini engelle.
        """
        user = form.get_user()
        
        # Eğer kullanıcı admin değilse takım kontrolü yap
        if not user.is_superuser:
            # Kullanıcının takımını kontrol et
            if not Team.objects.filter(members=user).exists():
                form.add_error(None, 'Sisteme giriş yapabilmek için bir takıma atanmış olmanız gerekmektedir. '
                                   'Lütfen sistem yöneticisi (admin) ile iletişime geçiniz.')
                return self.form_invalid(form)
        
        # Eğer buraya kadar geldiyse, ya admin ya da takımı olan bir kullanıcı
        return super().form_valid(form)

    def get_form(self, form_class=None):
        """
        Form oluşturulurken kullanıcı kontrolü yap.
        """
        form = super().get_form(form_class)
        
        # Eğer kullanıcı zaten giriş yapmışsa ve takımı yoksa, giriş yapmasını engelle
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            if not Team.objects.filter(members=self.request.user).exists():
                form.add_error(None, 'Sisteme giriş yapabilmek için bir takıma atanmış olmanız gerekmektedir. '
                                   'Lütfen sistem yöneticisi (admin) ile iletişime geçiniz.')
                return form
        
        return form

    def dispatch(self, request, *args, **kwargs):
        """
        Her istek öncesi kullanıcı kontrolü yap.
        """
        # Eğer kullanıcı zaten giriş yapmışsa ve takımı yoksa, çıkış yaptır
        if request.user.is_authenticated and not request.user.is_superuser:
            if not Team.objects.filter(members=request.user).exists():
                from django.contrib.auth import logout
                logout(request)
                messages.error(request, 'Sisteme giriş yapabilmek için bir takıma atanmış olmanız gerekmektedir. '
                                     'Lütfen sistem yöneticisi (admin) ile iletişime geçiniz.')
                return HttpResponseRedirect(self.get_login_url())
        
        return super().dispatch(request, *args, **kwargs)

@login_required
def claim_aircraft(request, pk):
    """Atanmamış uçağı takıma alma."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    aircraft = get_object_or_404(Aircraft, pk=pk)
    
    # Uçak zaten bir takıma atanmışsa hata ver
    if aircraft.assembly_team is not None:
        return JsonResponse({'error': 'Bu uçak zaten bir takıma atanmış.'}, status=400)
    
    # Kullanıcının takımını kontrol et
    user_team = request.user.team_members.first()
    if not user_team:
        return JsonResponse({'error': 'Kullanıcı bir takıma atanmamış.'}, status=403)
    
    # Sadece montaj takımları uçak alabilir
    if user_team.team_type != 'ASSEMBLY':
        return JsonResponse({'error': 'Sadece montaj takımları uçak alabilir.'}, status=403)
    
    # Takımda üye var mı kontrol et
    if user_team.members.count() == 0:
        return JsonResponse({'error': 'Takımda üye bulunmamaktadır. Takıma üye ekleyin.'}, status=403)
    
    # Uçağı takıma ata
    aircraft.assembly_team = user_team
    aircraft.save()
    
    return JsonResponse({
        'success': True,
        'message': f'{aircraft.get_aircraft_type_display()} uçağı takımınıza başarıyla atandı.'
    })

@login_required
def user_add_production(request):
    """Normal kullanıcılar için üretim kaydı oluşturma fonksiyonu"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    # Süper kullanıcılar bu endpoint'i kullanamaz
    if request.user.is_superuser:
        return JsonResponse({'error': 'Süper kullanıcılar için farklı bir endpoint kullanılmalıdır.'}, status=400)
    
    # Kullanıcının takımını kontrol et
    user_team = request.user.team_members.first()
    if not user_team:
        return JsonResponse({'error': 'User is not assigned to a team'}, status=403)
    
    # Assembly teams cannot produce parts
    if user_team.team_type == 'ASSEMBLY':
        return JsonResponse({'error': 'Assembly teams cannot produce parts'}, status=403)
    
    # Check if team has members
    if user_team.members.count() == 0:
        return JsonResponse({'error': 'Team has no members. Please add members to the team.'}, status=403)
    
    part_id = request.POST.get('part')
    quantity = request.POST.get('quantity')
    
    try:
        with transaction.atomic():
            part = Part.objects.get(id=part_id)
            quantity = int(quantity)
            
            # Mevcut stok değerini saklayalım
            old_stock = part.stock
            
            if quantity <= 0:
                return JsonResponse({'error': 'Quantity must be positive'}, status=400)
            
            # Check if team type matches part team type
            if user_team.team_type != part.team_type:
                return JsonResponse({'error': f'Your team ({user_team.get_team_type_display()}) cannot produce {part.get_team_type_display()} parts'}, status=403)
            
            # Check if part aircraft type is valid
            if part.team_type not in REQUIRED_PARTS[part.aircraft_type]:
                return JsonResponse({'error': 'Invalid part type for this aircraft type'}, status=400)
            
            # Create production record
            production = Production.objects.create(
                team=user_team,
                part=part,
                quantity=quantity,
                created_by=request.user
            )
            
            # Güncel stok değerini al
            part.refresh_from_db()
            
            # Stok değişmediyse direkt SQL ile güncelleyelim
            if part.stock == old_stock:
                # SQL direkt güncelleme yap
                from django.db import connection
                cursor = connection.cursor()
                cursor.execute(
                    f"UPDATE {part._meta.db_table} SET stock = stock + %s, is_low_stock = CASE WHEN (stock + %s) < minimum_stock THEN True ELSE False END WHERE id = %s",
                    [quantity, quantity, part_id]
                )
                part.refresh_from_db()
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully produced {quantity} {part.name}',
            'new_stock': part.stock
        })
        
    except Part.DoesNotExist:
        return JsonResponse({'error': 'Part not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid quantity'}, status=400)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500) 