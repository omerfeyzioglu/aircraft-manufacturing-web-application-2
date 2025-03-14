from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Team(models.Model):
    TEAM_TYPES = [
        ('AVIONICS', 'Aviyonik Takımı'),
        ('BODY', 'Gövde Takımı'),
        ('WING', 'Kanat Takımı'),
        ('TAIL', 'Kuyruk Takımı'),
        ('ASSEMBLY', 'Montaj Takımı'),
    ]

    name = models.CharField(max_length=100, verbose_name='Takım Adı')
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES, verbose_name='Takım Tipi')
    members = models.ManyToManyField(User, related_name='team_members', verbose_name='Üyeler')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')

    class Meta:
        verbose_name = 'Takım'
        verbose_name_plural = 'Takımlar'
        ordering = ['name']

    def __str__(self):
        return self.name

    def can_produce_part(self, part):
        return self.team_type == part.team_type

class Part(models.Model):
    name = models.CharField(max_length=100, verbose_name='Parça Adı')
    team_type = models.CharField(max_length=20, choices=Team.TEAM_TYPES[:-1], verbose_name='Üretici Takım')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stok')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Parça'
        verbose_name_plural = 'Parçalar'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.stock < 5

class Aircraft(models.Model):
    AIRCRAFT_TYPES = [
        ('TB2', 'Bayraktar TB2'),
        ('TB3', 'Bayraktar TB3'),
        ('AKINCI', 'Bayraktar AKINCI'),
        ('KIZILELMA', 'Bayraktar KIZILELMA'),
    ]

    aircraft_type = models.CharField(max_length=20, choices=AIRCRAFT_TYPES, verbose_name='Uçak Tipi')
    parts = models.ManyToManyField(Part, through='AircraftPart', verbose_name='Parçalar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Başlangıç Tarihi')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tamamlanma Tarihi')

    class Meta:
        verbose_name = 'Uçak'
        verbose_name_plural = 'Uçaklar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_aircraft_type_display()} ({self.created_at.strftime('%d.%m.%Y')})"

    @property
    def is_complete(self):
        required_parts = {
            'TB2': {'AVIONICS': 2, 'BODY': 1, 'WING': 2, 'TAIL': 1},
            'TB3': {'AVIONICS': 3, 'BODY': 2, 'WING': 2, 'TAIL': 1},
            'AKINCI': {'AVIONICS': 4, 'BODY': 3, 'WING': 2, 'TAIL': 2},
            'KIZILELMA': {'AVIONICS': 3, 'BODY': 2, 'WING': 2, 'TAIL': 1},
        }

        current_parts = {}
        for part in self.parts.all():
            current_parts[part.team_type] = current_parts.get(part.team_type, 0) + 1

        for team_type, count in required_parts[self.aircraft_type].items():
            if current_parts.get(team_type, 0) < count:
                return False
        return True

    def complete_production(self):
        if not self.is_complete:
            raise ValidationError('Uçak üretimi için gerekli tüm parçalar mevcut değil.')
        self.completed_at = timezone.now()
        self.save()

class AircraftPart(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, verbose_name='Uçak')
    part = models.ForeignKey(Part, on_delete=models.PROTECT, verbose_name='Parça')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Eklenme Tarihi')

    class Meta:
        verbose_name = 'Uçak Parçası'
        verbose_name_plural = 'Uçak Parçaları'
        ordering = ['added_at']
        unique_together = ['aircraft', 'part']

    def __str__(self):
        return f"{self.aircraft} - {self.part}"

    def clean(self):
        if self.part.stock <= 0:
            raise ValidationError('Bu parçanın stokta yeterli miktarı yok.')

    def save(self, *args, **kwargs):
        if not self.pk:  # Yeni kayıt
            self.part.stock -= 1
            self.part.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.part.stock += 1
        self.part.save()
        super().delete(*args, **kwargs)

class Production(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='Takım')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, verbose_name='Parça')
    quantity = models.PositiveIntegerField(verbose_name='Miktar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Üretim Tarihi')

    class Meta:
        verbose_name = 'Üretim'
        verbose_name_plural = 'Üretimler'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.team} - {self.part} ({self.quantity})"

    def clean(self):
        if not self.team.can_produce_part(self.part):
            raise ValidationError('Bu takım bu parçayı üretemez.')

    def save(self, *args, **kwargs):
        if not self.pk:  # Yeni kayıt
            self.part.stock += self.quantity
            self.part.save()
        super().save(*args, **kwargs) 