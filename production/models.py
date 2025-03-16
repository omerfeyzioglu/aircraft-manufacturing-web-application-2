from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Sabit değerler
AIRCRAFT_TYPES = [
    ('TB2', 'TB2'),
    ('TB3', 'TB3'),
    ('AKINCI', 'AKINCI'),
    ('KIZILELMA', 'KIZILELMA'),
]

TEAM_TYPES = [
    ('BODY', 'Gövde'),
    ('WING', 'Kanat'),
    ('TAIL', 'Kuyruk'),
    ('AVIONICS', 'Aviyonik'),
    ('ASSEMBLY', 'Montaj'),
]

# Her uçak tipi için gerekli parça sayıları
REQUIRED_PARTS = {
    'TB2': {'AVIONICS': 1, 'BODY': 1, 'WING': 1, 'TAIL': 1},
    'TB3': {'AVIONICS': 1, 'BODY': 1, 'WING': 1, 'TAIL': 1},
    'AKINCI': {'AVIONICS': 1, 'BODY': 1, 'WING': 1, 'TAIL': 1},
    'KIZILELMA': {'AVIONICS': 1, 'BODY': 1, 'WING': 1, 'TAIL': 1},
}

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
        # Stok durumunu kontrol et
        self.is_low_stock = self.stock < self.minimum_stock
        
        # Parça adını otomatik oluştur
        self.name = self.expected_name
            
        super().save(*args, **kwargs)
        
    def increase_stock(self, quantity):
        """Parça stoğunu artır"""
        if quantity <= 0:
            raise ValidationError("Artırılacak miktar pozitif olmalıdır.")
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

class Aircraft(models.Model):
    aircraft_type = models.CharField(max_length=20, choices=AIRCRAFT_TYPES, verbose_name='Hava Aracı Tipi')
    assembly_team = models.ForeignKey(Team, on_delete=models.PROTECT, limit_choices_to={'team_type': 'ASSEMBLY'}, verbose_name='Montaj Takımı', null=True, blank=True)
    parts = models.ManyToManyField(Part, through='AircraftPart', related_name='aircrafts', verbose_name='Parçalar')
    is_complete = models.BooleanField(default=False, verbose_name='Tamamlandı mı?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tamamlanma Tarihi')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_aircrafts', verbose_name='Oluşturan', null=True, blank=True)

    class Meta:
        verbose_name = 'Hava Aracı'
        verbose_name_plural = 'Hava Araçları'
        ordering = ['-created_at']

    def __str__(self):
        created_at_str = self.created_at.strftime('%d.%m.%Y') if self.created_at else "Tarih Yok"
        return f"{self.get_aircraft_type_display()} - {created_at_str}"

    def clean(self):
        # Montaj takımının tipini kontrol et
        if self.assembly_team and self.assembly_team.team_type != 'ASSEMBLY':
            raise ValidationError({'assembly_team': 'Seçilen takım bir montaj takımı değil.'})

    def save(self, *args, **kwargs):
        # Yeni kayıt mı kontrol et
        is_new = self.pk is None
        
        # Tamamlanma durumunu kontrol et
        self.is_complete = self.check_completion_status()
        
        # Önce kaydet
        super().save(*args, **kwargs)
        
        # Tamamlanma durumunu kontrol et ve completed_at alanını güncelle
        if self.is_complete and not self.completed_at:
            self.completed_at = timezone.now()
            super().save(update_fields=['completed_at'])
        elif not self.is_complete and self.completed_at:
            self.completed_at = None
            super().save(update_fields=['completed_at'])

    def check_completion_status(self):
        """Tüm gerekli parçalar eklenmiş mi kontrol et"""
        if not self.pk:  # Yeni kayıt ise henüz parçalar eklenmemiş
            return False
        
        # Her parça tipi için gereken sayıda parça var mı kontrol et
        required_parts = REQUIRED_PARTS[self.aircraft_type]
        
        for team_type, required_count in required_parts.items():
            current_count = self.parts.filter(team_type=team_type).count()
            if current_count < required_count:
                return False
        
        return True

    @property
    def required_parts(self):
        """Bu hava aracı tipi için gerekli parçaları döndür"""
        return Part.objects.filter(aircraft_type=self.aircraft_type)
    
    @property
    def missing_parts(self):
        """Eksik parçaları döndür"""
        missing = []
        required_parts = REQUIRED_PARTS[self.aircraft_type]
        
        for team_type, required_count in required_parts.items():
            current_count = self.parts.filter(team_type=team_type).count()
            if current_count < required_count:
                missing_count = required_count - current_count
                part_type = dict(TEAM_TYPES).get(team_type)
                missing.append({
                    'team_type': team_type,
                    'part_type': part_type,
                    'missing_count': missing_count
                })
        
        return missing

    def get_missing_parts(self):
        # Eğer aircraft_type boş ise veya sözlükte yoksa boş bir sözlük döndür\n        if not self.aircraft_type or self.aircraft_type not in REQUIRED_PARTS:\n            return {}
        if not self.aircraft_type or self.aircraft_type not in REQUIRED_PARTS:
            return {}
        
        """Eksik parçaların takım tipine göre sözlüğünü döndür"""
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

    def can_add_part(self, part):
        """Bir parçanın bu uçağa eklenip eklenemeyeceğini kontrol eder"""
        # Parça uçak tipiyle uyumlu mu?
        if not part.is_compatible_with_aircraft(self):
            return False, f'Bu parça {self.get_aircraft_type_display()} tipi ile uyumlu değil.'
        
        # Parçanın stoku var mı?
        if part.stock <= 0:
            return False, f'Bu parçanın stokta yeterli miktarı yok.'
        
        # Bu tipte daha fazla parça eklenebilir mi?
        required = REQUIRED_PARTS[self.aircraft_type][part.team_type]
        current = self.parts.filter(team_type=part.team_type).count()
        
        if current >= required:
            return False, f'Bu uçak için yeterli sayıda {part.get_team_type_display()} parçası zaten eklenmiş.'
        
        return True, None

    def add_part(self, part, added_by):
        """Validasyon ile uçağa parça ekler"""
        can_add, error = self.can_add_part(part)
        if not can_add:
            raise ValidationError(error)
        
        # Uçak parçası oluştur ve stoktan düş
        aircraft_part = AircraftPart.objects.create(
            aircraft=self,
            part=part,
            added_by=added_by
        )
        
        # Uçağın tamamlanma durumunu kontrol et
        self.is_complete = self.check_completion_status()
        if self.is_complete and not self.completed_at:
            self.completed_at = timezone.now()
            self.save()
        
        return aircraft_part

    def delete(self, *args, **kwargs):
        # Silmeden önce tüm parçaları stoğa geri döndür
        for aircraft_part in self.aircraft_parts.all():
            # AircraftPart.delete metodu parçayı stoğa geri döndürecek
            aircraft_part.delete()
        super().delete(*args, **kwargs)

class AircraftPart(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name='aircraft_parts', verbose_name='Hava Aracı')
    part = models.ForeignKey(Part, on_delete=models.PROTECT, related_name='aircraft_parts', verbose_name='Parça')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Eklenme Tarihi')
    added_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='added_parts', verbose_name='Ekleyen', null=True, blank=True)

    class Meta:
        verbose_name = 'Hava Aracı Parçası'
        verbose_name_plural = 'Hava Aracı Parçaları'
        unique_together = ['aircraft', 'part']
        ordering = ['added_at']

    def __str__(self):
        return f"{self.aircraft} - {self.part}"

    def clean(self):
        # Parça ve uçak tipinin uyumlu olup olmadığını kontrol et
        if self.part and self.aircraft and self.part.aircraft_type != self.aircraft.aircraft_type:
            raise ValidationError({'part': f'Bu parça {self.aircraft.get_aircraft_type_display()} tipi için uygun değil.'})
        
        # Stok kontrolü
        if self.part and self.part.stock <= 0:
            raise ValidationError({'part': f'{self.part.name} parçasının stokta yeterli miktarı yok.'})

    def save(self, *args, **kwargs):
        # Yeni kayıt mı kontrol et
        is_new = self.pk is None
        
        # Kaydet
        super().save(*args, **kwargs)
        
        # Yeni kayıtsa stoktan düş
        if is_new:
            try:
                self.part.decrease_stock(1)
            except ValidationError as e:
                # Stok hatası durumunda kaydı sil ve hatayı yeniden yükselt
                self.delete()
                raise e

    def delete(self, *args, **kwargs):
        # Parça silindiğinde stoğu artır
        self.part.increase_stock(1)
        super().delete(*args, **kwargs)

class Production(models.Model):
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='productions', verbose_name='Üretici Takım')
    part = models.ForeignKey(Part, on_delete=models.PROTECT, related_name='productions', verbose_name='Üretilen Parça')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Miktar')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='productions', verbose_name='Oluşturan', null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')

    class Meta:
        verbose_name = 'Üretim'
        verbose_name_plural = 'Üretimler'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.team.name} - {self.part.name} ({self.quantity})"

    def clean(self):
        # Takım tipinin parça tipiyle uyumlu olup olmadığını kontrol et
        if self.team and self.part and self.team.team_type != self.part.team_type:
            raise ValidationError({'part': f'Bu parça {self.team.get_team_type_display()} takımı tarafından üretilemez.'})
        
        # Montaj takımları parça üretemez
        if self.team and self.team.team_type == 'ASSEMBLY':
            raise ValidationError({'team': 'Montaj takımları parça üretemez.'})
        
        # Miktar pozitif olmalı
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Üretim miktarı pozitif olmalıdır.'})

    def save(self, *args, **kwargs):
        # Yeni kayıt mı kontrol et
        is_new = self.pk is None
        
        # Kaydet
        super().save(*args, **kwargs)
        
        # Yeni kayıtsa stok artır
        if is_new:
            # Direkt olarak veritabanında güncelleme yap, increase_stock metodunu çağırmadan
            # Bu şekilde Part.save() metodu çağrılmayacak ve stok sadece bir kez artacak
            Part.objects.filter(id=self.part.id).update(stock=models.F('stock') + self.quantity)
            # Parça nesnesini yenile
            self.part.refresh_from_db()

# Sinyal alıcıları
@receiver(post_save, sender=AircraftPart)
def update_aircraft_completion(sender, instance, created, **kwargs):
    """Bir parça eklendiğinde veya çıkarıldığında uçağın tamamlanma durumunu güncelle"""
    if instance.aircraft:
        # Tamamlanma durumunu kontrol et ve kaydet
        instance.aircraft.is_complete = instance.aircraft.check_completion_status()
        instance.aircraft.save()

@receiver(pre_save, sender=Part)
def check_stock_status(sender, instance, **kwargs):
    """Parça kaydedilmeden önce stok durumunu kontrol et"""
    instance.is_low_stock = instance.stock < instance.minimum_stock 