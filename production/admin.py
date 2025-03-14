from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Team, Part, Aircraft, Production, AircraftPart

class TeamMemberInline(admin.TabularInline):
    model = Team.members.through
    extra = 1
    verbose_name = 'Takım Üyesi'
    verbose_name_plural = 'Takım Üyeleri'

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'team_type', 'get_members_count', 'created_at']
    list_filter = ['team_type']
    search_fields = ['name']
    inlines = [TeamMemberInline]
    exclude = ['members']

    def get_members_count(self, obj):
        return obj.members.count()
    get_members_count.short_description = 'Üye Sayısı'

class AircraftPartInline(admin.TabularInline):
    model = AircraftPart
    extra = 1
    autocomplete_fields = ['part']
    readonly_fields = ['added_at', 'added_by']
    can_delete = True
    show_change_link = True
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj is None:
            formset.max_num = 0
            formset.extra = 0
        return formset

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Yeni kayıt
            obj.added_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['name', 'team_type', 'aircraft_type', 'stock', 'is_low_stock', 'created_at']
    list_filter = ['team_type', 'aircraft_type', 'stock']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name', 'team_type', 'aircraft_type']

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Düşük Stok'

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ['aircraft_type', 'assembly_team', 'is_complete', 'created_at', 'completed_at']
    list_filter = ['aircraft_type', 'assembly_team', 'completed_at']
    search_fields = ['aircraft_type']
    readonly_fields = ['created_at', 'completed_at']
    inlines = [AircraftPartInline]
    autocomplete_fields = ['assembly_team']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            team = request.user.team_members.first()
            if team and team.team_type == 'ASSEMBLY':
                return qs.filter(assembly_team=team)
            return qs.none()
        return qs

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            team = request.user.team_members.first()
            return team and team.team_type == 'ASSEMBLY'
        return True

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if isinstance(instance, AircraftPart) and not instance.pk:
                instance.added_by = request.user
            instance.save()
        formset.save_m2m()

@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ['team', 'part', 'quantity', 'created_by', 'created_at']
    list_filter = ['team', 'part', 'created_at']
    search_fields = ['team__name', 'part__name']
    readonly_fields = ['created_at', 'created_by']
    autocomplete_fields = ['team', 'part']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            team = request.user.team_members.first()
            if team:
                return qs.filter(team=team)
            return qs.none()
        return qs

    def has_add_permission(self, request):
        if not request.user.is_superuser:
            team = request.user.team_members.first()
            return team and team.team_type != 'ASSEMBLY'
        return True

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Yeni kayıt
            obj.created_by = request.user
            if not request.user.is_superuser:
                obj.team = request.user.team_members.first()
        super().save_model(request, obj, form, change)

# Özelleştirilmiş User admin'i
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_team']
    list_filter = ['is_staff', 'is_superuser', 'team_members']
    search_fields = ['username', 'first_name', 'last_name', 'email']

    def get_team(self, obj):
        team = obj.team_members.first()
        return team.name if team else '-'
    get_team.short_description = 'Takım'

# Özelleştirilmiş User admin'i kaydet
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin) 