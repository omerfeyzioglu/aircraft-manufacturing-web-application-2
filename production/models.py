from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum

# Sabit değerler
AIRCRAFT_TYPES = [
    ('TB2', 'TB2'),
    ('TB3', 'TB3'),
    ('AKINCI', 'AKINCI'),
    ('KIZILELMA', 'KIZILELMA'),
]

TEAM_TYPES = [
    ('AVIONICS', 'Aviyonik'),
    ('BODY', 'Gövde'),
    ('WING', 'Kanat'),
    ('TAIL', 'Kuyruk'),
    ('ASSEMBLY', 'Montaj'),
]

# Her uçak tipi için gerekli parça sayıları
REQUIRED_PARTS = {
    'TB2': {'AVIONICS': 5, 'BODY': 10, 'WING': 4, 'TAIL': 2},
    'TB3': {'AVIONICS': 8, 'BODY': 15, 'WING': 6, 'TAIL': 3},
    'AKINCI': {'AVIONICS': 12, 'BODY': 20, 'WING': 8, 'TAIL': 4},
    'KIZILELMA': {'AVIONICS': 15, 'BODY': 25, 'WING': 10, 'TAIL': 5},
}

class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name='Takım Adı')
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES, verbose_name='Takım Tipi')
    members = models.ManyToManyField(User, related_name='team_members', verbose_name='Üyeler')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Takım'
        verbose_name_plural = 'Takımlar'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_team_type_display()})"

    def can_produce_part(self, part):
        if self.team_type == 'ASSEMBLY':
            return False
        return self.team_type == part.team_type

    def get_total_production(self):
        result = self.productions.aggregate(total=Sum('quantity'))
        return result['total'] or 0

    @property
    def total_production(self):
        return self.get_total_production()

    @property
    def productions(self):
        return self.production_set.all()

class Part(models.Model):
    name = models.CharField(max_length=100, verbose_name='Parça Adı')
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES, verbose_name='Üretici Takım')
    aircraft_type = models.CharField(max_length=10, choices=AIRCRAFT_TYPES, verbose_name='Uçak Tipi')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stok')
    minimum_stock = models.PositiveIntegerField(default=5, verbose_name='Minimum Stok')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Parça'
        verbose_name_plural = 'Parçalar'
        ordering = ['name']
        unique_together = ['name', 'team_type', 'aircraft_type']

    def __str__(self):
        return f"{self.name} ({self.get_team_type_display()} - {self.get_aircraft_type_display()})"

    @property
    def is_low_stock(self):
        return self.stock <= self.minimum_stock
        
    @property
    def expected_name(self):
        """Get the expected name for this part based on team type and aircraft type."""
        aircraft_name = dict(AIRCRAFT_TYPES).get(self.aircraft_type, '')
        
        expected_names = {
            'WING': f"{aircraft_name} Kanat",
            'BODY': f"{aircraft_name} Gövde",
            'TAIL': f"{aircraft_name} Kuyruk",
            'AVIONICS': f"{aircraft_name} Aviyonik"
        }
        
        return expected_names.get(self.team_type, '')

    def clean(self):
        # Montaj takımları parça üretemez
        if self.team_type == 'ASSEMBLY':
            raise ValidationError('Montaj takımları parça üretemez.')
        
        # Parça tipi ve uçak tipi kombinasyonu geçerli olmalı
        if self.team_type not in REQUIRED_PARTS[self.aircraft_type]:
            raise ValidationError('Geçersiz takım tipi ve uçak tipi kombinasyonu.')
        
        # Parça adı, takım tipine uygun olmalı
        if self.name != self.expected_name:
            raise ValidationError(f'Parça adı "{self.expected_name}" olmalıdır.')
        
    def save(self, *args, **kwargs):
        # Auto-generate name if not set
        if not self.name:
            self.name = self.expected_name
            
        super().save(*args, **kwargs)
        
    def increase_stock(self, quantity):
        """Increase stock by the given quantity."""
        if quantity <= 0:
            raise ValidationError('Miktar pozitif olmalıdır.')
        self.stock += quantity
        self.save()

    def decrease_stock(self, quantity):
        """Decrease stock by the given quantity."""
        if quantity <= 0:
            raise ValidationError('Miktar pozitif olmalıdır.')
        if self.stock < quantity:
            raise ValidationError('Yetersiz stok.')
        self.stock -= quantity
        self.save()

    def get_required_quantity(self):
        """Get required quantity for this part type in its aircraft type."""
        return REQUIRED_PARTS[self.aircraft_type][self.team_type]

    def is_compatible_with_aircraft(self, aircraft):
        """Check if this part is compatible with the given aircraft."""
        return self.aircraft_type == aircraft.aircraft_type

class Aircraft(models.Model):
    aircraft_type = models.CharField(max_length=10, choices=AIRCRAFT_TYPES, verbose_name='Uçak Tipi')
    assembly_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, 
                                    limit_choices_to={'team_type': 'ASSEMBLY'}, 
                                    related_name='assembled_aircrafts',
                                    verbose_name='Montaj Takımı')
    parts = models.ManyToManyField(Part, through='AircraftPart', verbose_name='Parçalar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tamamlanma Tarihi')

    class Meta:
        verbose_name = 'Uçak'
        verbose_name_plural = 'Uçaklar'
        ordering = ['-created_at']

    def __str__(self):
        if self.created_at:
            return f"{self.get_aircraft_type_display()} ({self.created_at.strftime('%Y-%m-%d')})"
        return f"{self.get_aircraft_type_display()} (Yeni)"

    def get_missing_parts(self):
        """Get a dictionary of missing parts by team type."""
        required = REQUIRED_PARTS[self.aircraft_type]
        current = {team_type: 0 for team_type in required}
        
        for part in self.parts.all():
            if part.team_type in current:
                current[part.team_type] += 1
        
        missing = {}
        for team_type, required_count in required.items():
            current_count = current[team_type]
            if current_count < required_count:
                missing[team_type] = required_count - current_count
        
        return missing

    @property
    def is_complete(self):
        return len(self.get_missing_parts()) == 0

    def can_add_part(self, part):
        """Check if a part can be added to this aircraft."""
        if not part.is_compatible_with_aircraft(self):
            return False, 'Bu parça bu uçak tipi ile uyumlu değil.'
        
        if part.stock <= 0:
            return False, 'Bu parçanın stokta yeterli miktarı yok.'
        
        required = REQUIRED_PARTS[self.aircraft_type][part.team_type]
        current = self.parts.filter(team_type=part.team_type).count()
        
        if current >= required:
            return False, f'Bu uçak için yeterli sayıda {part.get_team_type_display()} parçası zaten eklenmiş.'
        
        return True, None

    def add_part(self, part, added_by):
        """Add a part to the aircraft with validation."""
        can_add, error = self.can_add_part(part)
        if not can_add:
            raise ValidationError(error)
        
        # Create aircraft part and decrease stock
        aircraft_part = AircraftPart.objects.create(
            aircraft=self,
            part=part,
            added_by=added_by
        )
        
        # Check if aircraft is complete after adding part
        if self.is_complete and not self.completed_at:
            self.completed_at = timezone.now()
            self.save()
        
        return aircraft_part

    def save(self, *args, **kwargs):
        # Önce nesneyi kaydet, sonra is_complete kontrolü yap
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Yeni kayıt değilse ve veritabanına kaydedildiyse is_complete kontrolü yap
        if not is_new:
            if self.is_complete and not self.completed_at:
                self.completed_at = timezone.now()
                # Tekrar kaydet, ama sonsuz döngüye girmemek için is_complete kontrolünü atla
                super().save(update_fields=['completed_at'])
            elif not self.is_complete and self.completed_at:
                self.completed_at = None
                super().save(update_fields=['completed_at'])
        
    def delete(self, *args, **kwargs):
        # Return all parts to stock before deleting
        for aircraft_part in self.aircraftpart_set.all():
            # The AircraftPart.delete method will handle returning the part to stock
            aircraft_part.delete()
        super().delete(*args, **kwargs)

class AircraftPart(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, verbose_name='Uçak')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, verbose_name='Parça')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Eklenme Tarihi')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Ekleyen')

    class Meta:
        verbose_name = 'Uçak Parçası'
        verbose_name_plural = 'Uçak Parçaları'
        unique_together = ['aircraft', 'part']

    def __str__(self):
        return f"{self.aircraft} - {self.part}"

    def clean(self):
        # Check if aircraft and part are set
        if not self.aircraft or not self.part:
            return
            
        if self.part.aircraft_type != self.aircraft.aircraft_type:
            raise ValidationError('Bu parça bu uçak tipi için uygun değil.')
        if self.part.stock <= 0:
            raise ValidationError('Bu parçanın stokta yeterli miktarı yok.')
        
        # Check if we already have enough parts of this type
        required = REQUIRED_PARTS[self.aircraft.aircraft_type][self.part.team_type]
        current = self.aircraft.parts.filter(team_type=self.part.team_type).count()
        if current >= required:
            raise ValidationError(f'Bu uçak için yeterli sayıda {self.part.get_team_type_display()} parçası zaten eklenmiş.')

    def save(self, *args, **kwargs):
        if not self.pk:  # Yeni kayıt
            # Decrease stock
            self.part.decrease_stock(1)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Increase stock when part is removed
        self.part.increase_stock(1)
        super().delete(*args, **kwargs)

class Production(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='productions', verbose_name='Üretici Takım')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, verbose_name='Üretilen Parça')
    quantity = models.PositiveIntegerField(verbose_name='Miktar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Üretim Tarihi')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Üreten')

    class Meta:
        verbose_name = 'Üretim'
        verbose_name_plural = 'Üretimler'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.team} - {self.part} ({self.quantity})"

    def clean(self):
        if not self.team.can_produce_part(self.part):
            raise ValidationError('Bu takım bu parçayı üretemez.')
        if self.quantity <= 0:
            raise ValidationError('Üretim miktarı pozitif olmalıdır.')

    def save(self, *args, **kwargs):
        if not self.pk:  # Yeni kayıt
            # Validate team can produce this part
            if not self.team.can_produce_part(self.part):
                raise ValidationError('Bu takım bu parçayı üretemez.')
            
            # Update stock
            self.part.increase_stock(self.quantity)
            
        super().save(*args, **kwargs) 