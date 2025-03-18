from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from .constants import TEAM_TYPES

class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name='Takım Adı')
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES, verbose_name='Takım Tipi')
    members = models.ManyToManyField(User, related_name='team_members', blank=True, verbose_name='Üyeler')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Takım'
        verbose_name_plural = 'Takımlar'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_team_type_display()})"

    def can_produce_part(self, part):
        """Takımın belirli bir parçayı üretip üretemeyeceğini kontrol eder"""
        if self.team_type == 'ASSEMBLY':
            return False
        return self.team_type == part.team_type

    def get_total_production(self):
        """Takımın toplam üretim miktarını döndürür"""
        result = self.productions.aggregate(total=Sum('quantity'))
        return result['total'] or 0

    @property
    def total_production(self):
        return self.get_total_production()

    @property
    def productions(self):
        return self.production_set.all()

    def clean(self):
        # Aynı isimde takım olamaz - sadece isim değiştiğinde kontrol et
        if self.pk:
            original = Team.objects.get(pk=self.pk)
            if original.name != self.name and Team.objects.filter(name=self.name).exclude(pk=self.pk).exists():
                raise ValidationError({'name': 'Bu isimde bir takım zaten var.'})
        else:
            # Yeni takım oluşturulurken
            if Team.objects.filter(name=self.name).exists():
                raise ValidationError({'name': 'Bu isimde bir takım zaten var.'})

    @property
    def member_count(self):
        return self.members.count() 