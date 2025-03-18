from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .team import Team
from .part import Part

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
        indexes = [
            models.Index(fields=['team']),
            models.Index(fields=['part']),
            models.Index(fields=['created_at']),
        ]

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
        
        # Üretim kaydını kaydet
        super().save(*args, **kwargs)
        
        # Yeni kayıtsa stok artırma işlemi yap (sadece bir kez!)
        if is_new:
            # Django ORM yerine direkt SQL sorgusu kullanarak stok artışını sağla
            from django.db import connection
            cursor = connection.cursor()
            
            # Tablo adını doğrudan belirt
            table_name = "production_part"
            
            # Stok artırıp low stock durumunu güncelleyen SQL sorgusu
            query = f"""
                UPDATE {table_name}
                SET stock = stock + %s,
                    is_low_stock = CASE WHEN (stock + %s) < minimum_stock THEN True ELSE False END
                WHERE id = %s
            """
            cursor.execute(query, [self.quantity, self.quantity, self.part_id])
            connection.commit()
            
            # Parça nesnesini yenile
            if hasattr(self, 'part') and self.part:
                # Nesneyi veritabanından yeniden yükle
                self.part.refresh_from_db() 