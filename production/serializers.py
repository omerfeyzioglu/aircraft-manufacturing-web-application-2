from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team, Part, Aircraft, AircraftPart, Production
from drf_spectacular.utils import extend_schema_field

class UserSerializer(serializers.ModelSerializer):
    """
    Kullanıcı bilgilerini serileştiren serializer.
    
    Kullanıcının temel bilgilerini içerir.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        extra_kwargs = {
            'username': {'help_text': 'Kullanıcı adı'},
            'first_name': {'help_text': 'Kullanıcının adı'},
            'last_name': {'help_text': 'Kullanıcının soyadı'},
            'email': {'help_text': 'Kullanıcının e-posta adresi'},
        }

class TeamSerializer(serializers.ModelSerializer):
    """
    Takım bilgilerini serileştiren serializer.
    
    Takımın temel bilgilerini, üye sayısını ve toplam üretim miktarını içerir.
    """
    member_count = serializers.IntegerField(read_only=True, help_text='Takımdaki üye sayısı')
    total_production = serializers.IntegerField(read_only=True, help_text='Takımın toplam üretim miktarı')
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'team_type', 'member_count', 'total_production', 'created_at']
        extra_kwargs = {
            'name': {'help_text': 'Takım adı'},
            'team_type': {'help_text': 'Takım tipi (AVIONICS, BODY, WING, TAIL, ASSEMBLY)'},
            'created_at': {'help_text': 'Takımın oluşturulma tarihi'},
        }

class PartSerializer(serializers.ModelSerializer):
    """
    Parça bilgilerini serileştiren serializer.
    
    Parçanın temel bilgilerini, takım tipini, uçak tipini ve stok durumunu içerir.
    """
    get_team_type_display = serializers.CharField(read_only=True, help_text='Takım tipinin görüntülenen adı')
    get_aircraft_type_display = serializers.CharField(read_only=True, help_text='Uçak tipinin görüntülenen adı')
    
    class Meta:
        model = Part
        fields = ['id', 'name', 'team_type', 'get_team_type_display', 
                 'aircraft_type', 'get_aircraft_type_display',
                 'stock', 'minimum_stock', 'is_low_stock']
        extra_kwargs = {
            'name': {'help_text': 'Parça adı'},
            'team_type': {'help_text': 'Üretici takım tipi (AVIONICS, BODY, WING, TAIL)'},
            'aircraft_type': {'help_text': 'Uyumlu uçak tipi (TB2, TB3, AKINCI, KIZILELMA)'},
            'stock': {'help_text': 'Mevcut stok miktarı'},
            'minimum_stock': {'help_text': 'Minimum stok seviyesi'},
            'is_low_stock': {'help_text': 'Stok miktarı minimum seviyenin altında mı?'},
        }

class AircraftSerializer(serializers.ModelSerializer):
    """
    Uçak bilgilerini serileştiren serializer.
    
    Uçağın temel bilgilerini, tipini, montaj takımını ve tamamlanma durumunu içerir.
    """
    get_aircraft_type_display = serializers.CharField(read_only=True, help_text='Uçak tipinin görüntülenen adı')
    assembly_team_name = serializers.CharField(source='assembly_team.name', read_only=True, help_text='Montaj takımının adı')
    
    class Meta:
        model = Aircraft
        fields = ['id', 'aircraft_type', 'get_aircraft_type_display',
                 'assembly_team', 'assembly_team_name',
                 'is_complete', 'created_at', 'completed_at']
        extra_kwargs = {
            'aircraft_type': {'help_text': 'Uçak tipi (TB2, TB3, AKINCI, KIZILELMA)'},
            'assembly_team': {'help_text': 'Montaj takımı ID\'si'},
            'is_complete': {'help_text': 'Uçak tamamlandı mı?'},
            'created_at': {'help_text': 'Uçağın oluşturulma tarihi'},
            'completed_at': {'help_text': 'Uçağın tamamlanma tarihi'},
        }

class ProductionSerializer(serializers.ModelSerializer):
    """
    Üretim bilgilerini serileştiren serializer.
    
    Üretimin temel bilgilerini, takımı, parçayı, miktarı ve üretim tarihini içerir.
    """
    team_name = serializers.CharField(source='team.name', read_only=True, help_text='Üretici takımın adı')
    part_name = serializers.CharField(source='part.name', read_only=True, help_text='Üretilen parçanın adı')
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, help_text='Üreten kullanıcının adı')
    
    class Meta:
        model = Production
        fields = ['id', 'team', 'team_name', 'part', 'part_name',
                 'quantity', 'created_by', 'created_by_username', 'created_at']
        extra_kwargs = {
            'team': {'help_text': 'Üretici takım ID\'si'},
            'part': {'help_text': 'Üretilen parça ID\'si'},
            'quantity': {'help_text': 'Üretim miktarı'},
            'created_by': {'help_text': 'Üreten kullanıcı ID\'si'},
            'created_at': {'help_text': 'Üretim tarihi'},
        }

class AircraftPartSerializer(serializers.ModelSerializer):
    """
    Uçak parçası ilişkisini serileştiren serializer.
    
    Uçak ve parça arasındaki ilişkiyi, parçanın eklenme tarihini ve ekleyen kullanıcıyı içerir.
    """
    part_name = serializers.CharField(source='part.name', read_only=True, help_text='Parçanın adı')
    team_type = serializers.CharField(source='part.team_type', read_only=True, help_text='Parçanın takım tipi')
    added_by_name = serializers.CharField(source='added_by.get_full_name', read_only=True, help_text='Parçayı ekleyen kullanıcının adı')

    class Meta:
        model = AircraftPart
        fields = ['id', 'aircraft', 'part', 'part_name', 'team_type', 'added_at', 'added_by', 'added_by_name']
        extra_kwargs = {
            'aircraft': {'help_text': 'Uçak ID\'si'},
            'part': {'help_text': 'Parça ID\'si'},
            'added_at': {'help_text': 'Parçanın eklenme tarihi'},
            'added_by': {'help_text': 'Parçayı ekleyen kullanıcı ID\'si'},
        } 