# Baykar Üretim Takip Sistemi

Bu proje, Baykar'ın İHA üretim süreçlerini takip etmek için geliştirilmiş bir web uygulamasıdır.

## Özellikler

- Takım yönetimi (Aviyonik, Gövde, Kanat, Kuyruk, Montaj)
- Parça üretim takibi
- Stok yönetimi
- İHA montaj takibi
- Üretim istatistikleri
- Kullanıcı profilleri

## Kurulum

1. Python 3.8+ yüklü olmalıdır.

2. Sanal ortam oluşturun ve aktif edin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanı migrasyonlarını yapın:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Superuser oluşturun:
```bash
python manage.py createsuperuser
```

6. Geliştirme sunucusunu başlatın:
```bash
python manage.py runserver
```

## Kullanım

1. Admin paneline giriş yapın: `http://127.0.0.1:8000/admin/`
2. Takımları oluşturun
3. Parçaları tanımlayın
4. Kullanıcıları takımlara atayın
5. Üretim süreçlerini takip edin

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim

Proje Yöneticisi - [@kullanici](https://github.com/kullanici)

Proje Linki: [https://github.com/kullanici/hava-araci-uretim](https://github.com/kullanici/hava-araci-uretim) 