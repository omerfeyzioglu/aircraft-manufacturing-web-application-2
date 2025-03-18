"""
Veritabanını sıfırlama scripti

Bu script, aşağıdaki işlemleri gerçekleştirir:
1. Tüm üretim kayıtlarını siler
2. Tüm uçak-parça ilişkilerini siler 
3. Tüm uçakları siler
4. Tüm parçaları siler
5. Tüm takım-üye ilişkilerini siler
6. Tüm takımları siler

Ayrıca isteğe bağlı olarak:
7. Süper kullanıcı hariç tüm kullanıcıları siler
8. Admin kullanıcısını resetler

Author: System
"""

import os
import sys
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baykar.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connection, transaction
from production.models import Production, Aircraft, AircraftPart, Part, Team

def confirm(message, auto_confirm=False):
    """Kullanıcıdan onay iste"""
    if auto_confirm:
        print(f"{message} -> Otomatik onaylandı")
        return True
    response = input(f"{message} (e/h): ").lower()
    return response == 'e'

def reset_database(auto_confirm=False):
    """Veritabanını sıfırla"""
    print("Veritabanı sıfırlama işlemi başlatılıyor...")
    
    # Admin kullanıcı kontrolü
    if not auto_confirm and not confirm("Bu işlem tüm proje verilerinizi silecektir. Devam etmek istiyor musunuz?"):
        print("İşlem iptal edildi.")
        return
    
    try:
        with transaction.atomic():
            # 1. Üretim kayıtlarını sil
            production_count = Production.objects.count()
            Production.objects.all().delete()
            print(f"{production_count} üretim kaydı silindi.")
            
            # 2. Uçak-parça ilişkilerini sil
            aircraft_part_count = AircraftPart.objects.count()
            AircraftPart.objects.all().delete()
            print(f"{aircraft_part_count} uçak-parça ilişkisi silindi.")
            
            # 3. Uçakları sil
            aircraft_count = Aircraft.objects.count()
            Aircraft.objects.all().delete()
            print(f"{aircraft_count} uçak silindi.")
            
            # 4. Parçaları sil - stok değerlerini resetleme
            part_count = Part.objects.count()
            if auto_confirm or confirm("Tüm parçaları silmek yerine stok değerlerini sıfırlamak ister misiniz?", auto_confirm):
                # SQL ile direkt güncelleme yapalım (ORM kullanmadan)
                cursor = connection.cursor()
                cursor.execute("UPDATE production_part SET stock = 0, is_low_stock = TRUE")
                print(f"{part_count} parçanın stok değerleri sıfırlandı.")
            else:
                Part.objects.all().delete()
                print(f"{part_count} parça silindi.")
            
            # 5. Takım-üye ilişkilerini sil
            if auto_confirm or confirm("Takım üyeliklerini sıfırlamak ister misiniz?", auto_confirm):
                # SQL ile daha hızlı temizleme
                cursor = connection.cursor()
                cursor.execute("DELETE FROM production_team_members")
                print("Tüm takım üyelikleri silindi.")
            
            # 6. Takımları sil
            if not auto_confirm and confirm("Tüm takımları silmek ister misiniz?", auto_confirm):
                team_count = Team.objects.count()
                Team.objects.all().delete()
                print(f"{team_count} takım silindi.")
            
            # 7. Kullanıcıları sil
            if not auto_confirm and confirm("Admin kullanıcısı hariç tüm kullanıcıları silmek ister misiniz?", auto_confirm):
                user_count = User.objects.filter(is_superuser=False).count()
                User.objects.filter(is_superuser=False).delete()
                print(f"{user_count} kullanıcı silindi.")
            
            # 8. Admin kullanıcısını resetle
            if auto_confirm or confirm("Admin kullanıcısının şifresini 'admin' olarak değiştirmek ister misiniz?", auto_confirm):
                admin = User.objects.filter(is_superuser=True).first()
                if admin:
                    admin.set_password('admin')
                    admin.save()
                    print(f"Admin kullanıcısının şifresi 'admin' olarak değiştirildi.")
    
        print("\nVeritabanı sıfırlama işlemi tamamlandı.")
        print("\nYeni kullanıcı ve takım oluşturmak için admin sayfasına gidin: http://localhost:8000/admin/")
    except Exception as e:
        print(f"Hata oluştu: {e}")
        print("İşlem iptal edildi.")

if __name__ == "__main__":
    # Otomatik onay için parametre kontrolü
    auto_confirm = "--auto" in sys.argv or "-a" in sys.argv
    reset_database(auto_confirm) 