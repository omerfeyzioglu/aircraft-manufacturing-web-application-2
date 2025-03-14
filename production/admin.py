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

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['name', 'team_type', 'stock', 'is_low_stock', 'created_at']
    list_filter = ['team_type', 'stock']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Düşük Stok'

class AircraftPartInline(admin.TabularInline):
    model = AircraftPart
    extra = 1
    verbose_name = 'Uçak Parçası'
    verbose_name_plural = 'Uçak Parçaları'

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ['aircraft_type', 'is_complete', 'created_at', 'completed_at']
    list_filter = ['aircraft_type', 'completed_at']
    search_fields = ['aircraft_type']
    readonly_fields = ['created_at', 'completed_at']
    inlines = [AircraftPartInline]

@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ['team', 'part', 'quantity', 'created_at']
    list_filter = ['team', 'part', 'created_at']
    search_fields = ['team__name', 'part__name']
    readonly_fields = ['created_at']

# User modelini özelleştir
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