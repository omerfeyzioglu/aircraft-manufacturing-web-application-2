from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Count, Sum, Q
from .models import Team, Part, Aircraft, Production, AircraftPart, TEAM_TYPES

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_team')
    list_filter = ('is_staff', 'is_superuser', 'team_members')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_team(self, obj):
        team = Team.objects.filter(members=obj).first()
        if team:
            return team.name
        return '-'
    get_team.short_description = 'Takım'

# Mevcut UserAdmin'i kaldır ve özelleştirilmiş versiyonu kaydet
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class TeamMemberInline(admin.TabularInline):
    model = Team.members.through
    extra = 1
    verbose_name = "Takım Üyesi"
    verbose_name_plural = "Takım Üyeleri"
    autocomplete_fields = ['user']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_type', 'get_member_count', 'get_total_production')
    list_filter = ('team_type',)
    search_fields = ('name',)
    inlines = [TeamMemberInline]
    exclude = ('members',)
    
    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Üye Sayısı'
    
    def get_total_production(self, obj):
        total = Production.objects.filter(team=obj).aggregate(Sum('quantity'))
        return total['quantity__sum'] or 0
    get_total_production.short_description = 'Toplam Üretim'

class LowStockPartFilter(admin.SimpleListFilter):
    title = 'Stok Durumu'
    parameter_name = 'stock_status'
    
    def lookups(self, request, model_admin):
        return (
            ('low', 'Düşük Stok'),
            ('ok', 'Yeterli Stok'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(is_low_stock=True)
        if self.value() == 'ok':
            return queryset.filter(is_low_stock=False)
        return queryset

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'team_type', 'aircraft_type', 'stock', 'minimum_stock', 'get_stock_status')
    list_filter = ('team_type', 'aircraft_type', LowStockPartFilter)
    search_fields = ('name',)
    readonly_fields = ('name', 'is_low_stock')
    fieldsets = (
        ('Parça Bilgileri', {
            'fields': ('team_type', 'aircraft_type', 'name'),
            'description': 'Parça adı, takım tipi ve uçak tipine göre otomatik olarak oluşturulur. Takım tipi, parçayı üretecek takımın tipini belirtir (örn: "Gövde" parçası için "Gövde" takım tipi).'
        }),
        ('Stok Bilgileri', {
            'fields': ('stock', 'minimum_stock', 'is_low_stock')
        }),
    )
    
    def get_stock_status(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: red; font-weight: bold;">Düşük Stok</span>')
        return format_html('<span style="color: green;">Yeterli Stok</span>')
    get_stock_status.short_description = 'Stok Durumu'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Düzenleme durumunda
            return self.readonly_fields + ('team_type', 'aircraft_type')
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yeni kayıt
            # Parça adı otomatik oluşturulacak
            obj.name = obj.expected_name
        super().save_model(request, obj, form, change)
        
    def has_add_permission(self, request):
        # Süper kullanıcı her zaman ekleyebilir
        if request.user.is_superuser:
            return True
            
        # Kullanıcının bir takımı var mı kontrol et
        user_team = Team.objects.filter(members=request.user).first()
        if not user_team:
            return False
            
        # Montaj takımları parça üretemez
        return user_team.team_type != 'ASSEMBLY'

class AircraftPartInline(admin.TabularInline):
    model = AircraftPart
    extra = 1
    autocomplete_fields = ['part']
    can_delete = True
    show_change_link = True
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj is None:  # Yeni bir uçak oluşturulurken
            return formset  # Yeni bir uçak oluşturulduğunda da parça eklenebilmeli
        else:
            # Parça seçimini uçak tipine göre filtrele
            formset.form.base_fields['part'].queryset = Part.objects.filter(
                aircraft_type=obj.aircraft_type,
                stock__gt=0
            )
        return formset

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('id', 'aircraft_type', 'assembly_team', 'get_completion_status', 'created_at', 'completed_at')
    list_filter = ('aircraft_type', 'assembly_team', 'is_complete')
    search_fields = ('id',)
    readonly_fields = ('completed_at', 'is_complete', 'get_missing_parts_display')
    inlines = [AircraftPartInline]
    autocomplete_fields = ['assembly_team']
    fieldsets = (
        ('Uçak Bilgileri', {
            'fields': ('aircraft_type', 'assembly_team', 'created_by')
        }),
        ('Durum Bilgileri', {
            'fields': ('is_complete', 'completed_at', 'get_missing_parts_display')
        }),
    )
    
    def get_completion_status(self, obj):
        if obj.is_complete:
            return format_html('<span style="color: green; font-weight: bold;">Tamamlandı</span>')
        return format_html('<span style="color: red;">Tamamlanmadı</span>')
    get_completion_status.short_description = 'Durum'
    
    def get_missing_parts_display(self, obj):
        if obj.is_complete:
            return format_html('<span style="color: green;">Tüm parçalar tamamlandı</span>')
        
        missing_parts = obj.get_missing_parts()
        if not missing_parts:
            return format_html('<span style="color: green;">Tüm parçalar tamamlandı</span>')
        
        html = '<ul style="color: red;">'
        for team_type, count in missing_parts.items():
            part_type = dict(TEAM_TYPES).get(team_type)
            html += f'<li><strong>{part_type}:</strong> {count} adet eksik</li>'
        html += '</ul>'
        return format_html(html)
    get_missing_parts_display.short_description = 'Eksik Parçalar'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yeni bir uçak oluşturulurken
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, AircraftPart):
                instance.added_by = request.user
            instance.save()
        formset.save_m2m()
        
    def has_add_permission(self, request):
        # Süper kullanıcı her zaman ekleyebilir
        if request.user.is_superuser:
            return True
            
        # Kullanıcının bir takımı var mı kontrol et
        user_team = Team.objects.filter(members=request.user).first()
        if not user_team:
            return False
            
        # Sadece montaj takımları uçak ekleyebilir
        return user_team.team_type == 'ASSEMBLY'

@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ('team', 'part', 'quantity', 'created_by', 'created_at')
    list_filter = ('team', 'part__aircraft_type', 'created_at')
    search_fields = ('team__name', 'part__name')
    autocomplete_fields = ['team', 'part']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Takım seçimini kullanıcının takımıyla sınırla
        if not request.user.is_superuser:
            user_team = Team.objects.filter(members=request.user).first()
            if user_team:
                form.base_fields['team'].initial = user_team
                form.base_fields['team'].queryset = Team.objects.filter(id=user_team.id)
        
        # Parça seçimini takım tipine göre filtrele
        if 'team' in form.base_fields:
            team_field = form.base_fields['team']
            part_field = form.base_fields['part']
            
            # Montaj takımlarını üretim formundan çıkar
            team_field.queryset = team_field.queryset.exclude(team_type='ASSEMBLY')
            
            if obj and obj.team:
                # Düzenleme durumunda, takım tipine göre parçaları filtrele
                part_field.queryset = Part.objects.filter(team_type=obj.team.team_type)
            elif request.user.is_superuser:
                # Süper kullanıcı için tüm parçaları göster
                part_field.queryset = Part.objects.all()
            else:
                # Normal kullanıcı için takımına uygun parçaları göster
                user_team = Team.objects.filter(members=request.user).first()
                if user_team and user_team.team_type != 'ASSEMBLY':
                    part_field.queryset = Part.objects.filter(team_type=user_team.team_type)
                else:
                    part_field.queryset = Part.objects.none()
        
        return form
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yeni bir üretim kaydı oluşturulurken
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        # Montaj takımı üyeleri parça üretemez
        if not request.user.is_superuser:
            user_team = Team.objects.filter(members=request.user).first()
            if user_team and user_team.team_type == 'ASSEMBLY':
                return False
        return super().has_add_permission(request)

@admin.register(AircraftPart)
class AircraftPartAdmin(admin.ModelAdmin):
    list_display = ('aircraft', 'part', 'added_by', 'added_at')
    list_filter = ('aircraft__aircraft_type', 'part__team_type')
    search_fields = ('aircraft__id', 'part__name')
    autocomplete_fields = ['aircraft', 'part']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Parça seçimini uçak tipine göre filtrele
        if 'aircraft' in form.base_fields and 'part' in form.base_fields:
            aircraft_field = form.base_fields['aircraft']
            part_field = form.base_fields['part']
            
            if obj and obj.aircraft:
                # Düzenleme durumunda, uçak tipine göre parçaları filtrele
                part_field.queryset = Part.objects.filter(
                    aircraft_type=obj.aircraft.aircraft_type,
                    stock__gt=0
                )
            else:
                # Yeni kayıt durumunda, stokta olan parçaları göster
                part_field.queryset = Part.objects.filter(stock__gt=0)
        
        return form
    
    def has_add_permission(self, request):
        # Montaj takımı üyeleri dışındakiler parça ekleyemez
        if not request.user.is_superuser:
            user_team = Team.objects.filter(members=request.user).first()
            if not user_team or user_team.team_type != 'ASSEMBLY':
                return False
        return super().has_add_permission(request) 