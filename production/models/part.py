from django.db import models
from django.core.exceptions import ValidationError
from .constants import TEAM_TYPES, AIRCRAFT_TYPES, REQUIRED_PARTS

class Part(models.Model):
    name = models.CharField(max_length=100, verbose_name='Parça Adı')
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES, verbose_name='Üretici Takım Tipi')
    aircraft_type = models.CharField(max_length=20, choices=AIRCRAFT_TYPES, verbose_name='Hava Aracı Tipi')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stok Miktarı')
    minimum_stock = models.PositiveIntegerField(default=5, verbose_name='Minimum Stok Miktarı')
    is_low_stock = models.BooleanField(default=False, verbose_name='Düşük Stok')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Parça'
        verbose_name_plural = 'Parçalar'
        ordering = ['name']

    def __str__(self):
        return f"{self.get_aircraft_type_display()} {self.get_team_type_display()}"

    def clean(self):
        # Stok miktarı negatif olamaz
        if self.stock < 0:
            raise ValidationError({'stock': 'Stok miktarı negatif olamaz.'})
        
        # Minimum stok miktarı negatif olamaz
        if self.minimum_stock < 0:
            raise ValidationError({'minimum_stock': 'Minimum stok miktarı negatif olamaz.'})
        
        # Montaj takımları parça üretemez
        if self.team_type == 'ASSEMBLY':
            raise ValidationError('Montaj takımları parça üretemez.')
        
        # Parça tipi ve uçak tipi kombinasyonu geçerli olmalı
        if self.team_type not in REQUIRED_PARTS[self.aircraft_type]:
            raise ValidationError('Geçersiz takım tipi ve uçak tipi kombinasyonu.')
        
        # Parça adı otomatik oluşturulacak
        self.name = self.expected_name

    def save(self, *args, **kwargs):
        # Stok durumunu kontrol et ve güncelle
        if hasattr(self, 'stock') and hasattr(self, 'minimum_stock'):
            self.is_low_stock = self.stock < self.minimum_stock
        
        # Parça adını otomatik oluştur
        if hasattr(self, 'team_type') and hasattr(self, 'aircraft_type'):
            self.name = self.expected_name
            
        super().save(*args, **kwargs)
        
    def increase_stock(self, quantity):
        """Parça stoğunu artır"""
        if quantity <= 0:
            raise ValidationError("Artırılacak miktar pozitif olmalıdır.")
        
        # UYARI: Bu metod Production.save() tarafından otomatik çağrılmamalıdır!
        # Üretim kaydı oluştururken, Production.save() metodu direkt SQL sorgusu ile stok artırır
        # Bu metod sadece manuel stok artırımı için kullanılmalıdır
        
        self.stock += quantity
        self.save()

    def decrease_stock(self, quantity):
        """Parça stoğunu azalt"""
        if quantity <= 0:
            raise ValidationError("Azaltılacak miktar pozitif olmalıdır.")
        if self.stock < quantity:
            raise ValidationError(f"Stokta yeterli {self.name} parçası yok. Mevcut: {self.stock}, İstenen: {quantity}")
        self.stock -= quantity
        self.save()

    def get_required_quantity(self):
        """Bu parça tipinin uçak tipinde gereken miktarını döndürür"""
        return REQUIRED_PARTS[self.aircraft_type][self.team_type]

    def is_compatible_with_aircraft(self, aircraft):
        """Bu parçanın verilen uçakla uyumlu olup olmadığını kontrol eder"""
        return self.aircraft_type == aircraft.aircraft_type

    @property
    def expected_name(self):
        """Takım tipi ve uçak tipine göre beklenen parça adını döndürür"""
        aircraft_name = dict(AIRCRAFT_TYPES).get(self.aircraft_type, '')
        team_name = dict(TEAM_TYPES).get(self.team_type, '')
        return f"{aircraft_name} {team_name}" 