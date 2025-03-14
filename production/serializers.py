from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Part, Team, Aircraft, Production, AircraftPart

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ['id', 'name', 'team_type', 'stock', 'created_at', 'updated_at']

class TeamSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'team_type', 'members', 'created_at']

class ProductionSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = Production
        fields = ['id', 'team', 'team_name', 'part', 'part_name', 'quantity', 'created_at']

class AircraftPartSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part.name', read_only=True)
    team_type = serializers.CharField(source='part.team_type', read_only=True)

    class Meta:
        model = AircraftPart
        fields = ['id', 'aircraft', 'part', 'part_name', 'team_type', 'added_at']

class AircraftSerializer(serializers.ModelSerializer):
    parts_summary = serializers.SerializerMethodField()
    is_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = Aircraft
        fields = ['id', 'aircraft_type', 'created_at', 'completed_at', 'is_complete', 'parts_summary']

    def get_parts_summary(self, obj):
        required_parts = {
            'TB2': {'BODY': 1, 'ELECTRONIC': 2, 'ENGINE': 1},
            'TB3': {'BODY': 2, 'ELECTRONIC': 3, 'ENGINE': 2},
            'AKINCI': {'BODY': 3, 'ELECTRONIC': 4, 'ENGINE': 2},
            'KIZILELMA': {'BODY': 2, 'ELECTRONIC': 3, 'ENGINE': 2},
        }

        current_parts = {}
        for part in obj.parts.all():
            current_parts[part.team_type] = current_parts.get(part.team_type, 0) + 1

        summary = []
        for team_type, required in required_parts[obj.aircraft_type].items():
            current = current_parts.get(team_type, 0)
            summary.append({
                'team_type': team_type,
                'team_name': dict(Team.TEAM_TYPES)[team_type],
                'required': required,
                'current': current,
                'is_complete': current >= required
            })

        return summary 