# Baykar Hava Aracı Üretim Takip Sistemi

Bu proje, Baykar'ın İHA (İnsansız Hava Aracı) üretim süreçlerini takip etmek için geliştirilmiş kapsamlı bir web uygulamasıdır. Sistem, parça üretimi, stok yönetimi, montaj süreci ve üretim istatistiklerini takip etmek için tasarlanmıştır.

## 📋 İçindekiler

- [Proje Özellikleri](#-proje-özellikleri)
- [Teknoloji Yığını](#-teknoloji-yığını)
- [Kurulum](#-kurulum)
  - [Gereksinimler](#gereksinimler)
  - [Yerel Kurulum](#yerel-kurulum)
  - [Docker ile Kurulum](#docker-ile-kurulum)
- [Kullanım](#-kullanım)
  - [Kullanıcı Rolleri ve İzinler](#kullanıcı-rolleri-ve-izinler)
  - [Parça Yönetimi](#parça-yönetimi)
  - [Takım Yönetimi](#takım-yönetimi)
  - [Uçak Montaj Süreci](#uçak-montaj-süreci)
  - [Stok Takibi](#stok-takibi)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [Proje Yapısı](#-proje-yapısı)
- [Veri Modeli](#-veri-modeli)
- [Güvenlik Önlemleri](#-güvenlik-önlemleri)
- [Performans Optimizasyonları](#-performans-optimizasyonları)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)

## 🚀 Proje Özellikleri

### Temel Özellikler

- **Kullanıcı Yönetimi**: Kullanıcı kaydı, giriş, çıkış ve profil yönetimi
- **Takım Yönetimi**: Aviyonik, Gövde, Kanat, Kuyruk ve Montaj takımları için yönetim arayüzü
- **Parça Üretimi**: Takımların kendi sorumluluklarındaki parçaları üretmesi
- **Stok Takibi**: Parça stok seviyelerinin izlenmesi ve düşük stok uyarıları
- **Uçak Montajı**: Montaj takımının uyumlu parçaları birleştirerek uçak üretmesi
- **Üretim İstatistikleri**: Üretim süreçlerinin grafikler ve tablolarla görselleştirilmesi
- **Çoklu Dil Desteği**: Türkçe ve İngilizce dil seçenekleri

### Uçak Modelleri

- TB2 (Bayraktar TB2)
- TB3 (Bayraktar TB3)
- AKINCI (Bayraktar AKINCI)
- KIZILELMA (Bayraktar KIZILELMA)

### Parça Tipleri

- Kanat (Wing)
- Gövde (Body)
- Kuyruk (Tail)
- Aviyonik (Avionics)

### Takım Tipleri

- Kanat Takımı (Wing Team)
- Gövde Takımı (Body Team)
- Kuyruk Takımı (Tail Team)
- Aviyonik Takımı (Avionics Team)
- Montaj Takımı (Assembly Team)

## 💻 Kullanılan Teknolojiler

### Backend

- **Python 3.8+**: Ana programlama dili
- **Django 5.0+**: Web framework
- **Django REST Framework**: API geliştirme
- **PostgreSQL**: Veritabanı
- **drf-spectacular**: API dokümantasyonu (Swagger/OpenAPI)

### Frontend

- **HTML5/CSS3**: Sayfa yapısı ve stil
- **JavaScript/jQuery**: İstemci tarafı etkileşimler
- **Bootstrap 5**: Responsive tasarım
- **DataTables**: Veri tabloları
- **Chart.js**: Grafikler ve veri görselleştirme
- **Font Awesome**: İkonlar
- **Toastr.js**: Bildirimler

### DevOps

- **Docker**: Konteynerizasyon
- **Docker Compose**: Çoklu konteyner yönetimi
- **Git**: Versiyon kontrolü

## 🔧 Kurulum

### Gereksinimler

- Python 3.8+
- PostgreSQL 12+
- pip (Python paket yöneticisi)
- virtualenv (isteğe bağlı)

### Yerel Kurulum

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/kullanici/hava-araci-uretim.git
   cd hava-araci-uretim
   ```

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

4. PostgreSQL veritabanı oluşturun:
   ```bash
   createdb aircraft-manifacturing  # PostgreSQL komut satırı aracı
   ```

5. Veritabanı ayarlarını yapılandırın:
   `baykar/settings.py` dosyasında veritabanı bağlantı bilgilerini güncelleyin veya `.env` dosyası oluşturun.

6. Veritabanı migrasyonlarını yapın:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. Superuser oluşturun:
   ```bash
   python manage.py createsuperuser
   ```

8. Geliştirme sunucusunu başlatın:
   ```bash
   python manage.py runserver
   ```

9. Tarayıcınızda `http://127.0.0.1:8000/` adresine giderek uygulamayı görüntüleyin.

### Docker ile Kurulum

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/kullanici/hava-araci-uretim.git
   cd hava-araci-uretim
   ```

2. Docker Compose ile konteynerları başlatın:
   ```bash
   docker-compose up -d
   ```

3. Veritabanı migrasyonlarını yapın:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. Superuser oluşturun:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. Tarayıcınızda `http://localhost:8000/` adresine giderek uygulamayı görüntüleyin.

6. Tarayıcınızda `http://localhost:8000/admin` adresine giderek tüm operasyonları admin olarak görüntüleyebilir ardınıdan kullanıcı oluşturabilirsiniz. Çıkış yaptıktan sonra oluşturduğunuz kullanıcı bilgileri ile tekrardan sisteme giriş yapabilirsiniz.
## 📖 Kullanım

### Kullanıcı Rolleri ve İzinler

Sistem, kullanıcıları takımlara atar ve her takımın kendi sorumluluk alanı vardır:

- **Aviyonik Takımı**: Sadece aviyonik parçaları üretebilir
- **Gövde Takımı**: Sadece gövde parçaları üretebilir
- **Kanat Takımı**: Sadece kanat parçaları üretebilir
- **Kuyruk Takımı**: Sadece kuyruk parçaları üretebilir
- **Montaj Takımı**: Parça üretemez, sadece uçak montajı yapabilir

### Parça Yönetimi

1. **Parça Üretimi**:
   - İlgili takım üyesi olarak giriş yapın
   - "Parçalar" sayfasına gidin
   - "Yeni Parça Üret" butonuna tıklayın
   - Parça tipini, uçak modelini ve miktarı seçin
   - "Üret" butonuna tıklayın

2. **Parça Listesi**:
   - Tüm parçaları görüntüleyin
   - Parça tipi, uçak modeli ve stok durumuna göre filtreleme yapın
   - Düşük stok seviyesindeki parçaları görüntüleyin

### Takım Yönetimi

1. **Takım Oluşturma** (Admin):
   - Admin paneline giriş yapın
   - "Takımlar" bölümüne gidin
   - "Takım Ekle" butonuna tıklayın
   - Takım adı ve tipini belirleyin
   - Takım üyelerini seçin

2. **Takım Listesi**:
   - Tüm takımları görüntüleyin
   - Takım tipine göre filtreleme yapın
   - Takım üyelerini ve üretim istatistiklerini görüntüleyin

### Uçak Montaj Süreci

1. **Yeni Uçak Başlatma** (Montaj Takımı):
   - Montaj takımı üyesi olarak giriş yapın
   - "Uçaklar" sayfasına gidin
   - "Yeni Uçak" butonuna tıklayın
   - Uçak modelini seçin
   - "Başlat" butonuna tıklayın

2. **Parça Ekleme** (Montaj Takımı):
   - Uçak listesinden bir uçak seçin
   - "Parça Ekle" butonuna tıklayın
   - Eklenecek parçayı seçin
   - "Ekle" butonuna tıklayın
   - Tüm gerekli parçalar eklendiğinde uçak otomatik olarak tamamlanır

3. **Uçak Listesi**:
   - Tüm uçakları görüntüleyin
   - Uçak modeli, durum ve montaj takımına göre filtreleme yapın
   - Tamamlanma yüzdesini ve eksik parçaları görüntüleyin

### Stok Takibi

1. **Stok Durumu**:
   - Ana sayfadaki "Düşük Stok Uyarıları" bölümünden kritik stok seviyesindeki parçaları görüntüleyin
   - "Parçalar" sayfasından detaylı stok bilgilerini görüntüleyin

2. **Üretim Geçmişi**:
   - "Parçalar" sayfasından bir parçanın üretim geçmişini görüntüleyin
   - Tarih, miktar ve üreten takım bilgilerini görüntüleyin

## 🔌 API Dokümantasyonu

Sistem, tüm işlevlere programatik erişim sağlayan kapsamlı bir REST API sunar:

- **API Endpoint**: `/api/`
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Şeması**: `/api/schema/`

### Temel API Endpointleri

- `/api/parts/`: Parça yönetimi
- `/api/teams/`: Takım yönetimi
- `/api/aircraft/`: Uçak yönetimi

### Özel API Aksiyonları

- `/api/teams/{id}/produce_part/`: Parça üretimi
- `/api/aircraft/{id}/add_part/`: Uçağa parça ekleme
- `/api/aircraft/{id}/parts_summary/`: Uçak parça özeti

## 📂 Proje Yapısı

```
baykar/
├── baykar/                  # Proje ana dizini
│   ├── settings.py          # Proje ayarları
│   ├── urls.py              # Ana URL yapılandırması
│   ├── wsgi.py              # WSGI yapılandırması
│   └── asgi.py              # ASGI yapılandırması
├── production/              # Üretim uygulaması
│   ├── migrations/          # Veritabanı migrasyonları
│   ├── templates/           # Uygulama şablonları
│   ├── models.py            # Veri modelleri
│   ├── views.py             # Görünümler
│   ├── urls.py              # URL yapılandırması
│   ├── serializers.py       # API serileştiricileri
│   ├── signals.py           # Django sinyalleri
│   └── apps.py              # Uygulama yapılandırması
├── templates/               # Proje şablonları
│   ├── base.html            # Ana şablon
│   ├── home.html            # Ana sayfa
│   ├── registration/        # Kimlik doğrulama şablonları
│   ├── parts/               # Parça şablonları
│   ├── teams/               # Takım şablonları
│   └── aircraft/            # Uçak şablonları
├── static/                  # Statik dosyalar
│   ├── css/                 # CSS dosyaları
│   ├── js/                  # JavaScript dosyaları
│   └── img/                 # Resimler
├── media/                   # Kullanıcı yüklenen dosyalar
├── requirements.txt         # Python bağımlılıkları
├── manage.py                # Django yönetim betiği
├── Dockerfile               # Docker yapılandırması
├── docker-compose.yml       # Docker Compose yapılandırması
└── README.md                # Proje dokümantasyonu
```

## 📊 Veri Modeli

### Temel Modeller

1. **Part (Parça)**
   - name: Parça adı
   - team_type: Üretici takım tipi
   - aircraft_type: Uçak tipi
   - stock: Stok miktarı
   - minimum_stock: Minimum stok seviyesi

2. **Team (Takım)**
   - name: Takım adı
   - team_type: Takım tipi
   - members: Takım üyeleri (User modeli ile ilişki)

3. **Aircraft (Uçak)**
   - aircraft_type: Uçak tipi
   - assembly_team: Montaj takımı (Team modeli ile ilişki)
   - parts: Uçağa eklenen parçalar (Part modeli ile ilişki)
   - created_at: Oluşturulma tarihi
   - completed_at: Tamamlanma tarihi

4. **AircraftPart (Uçak Parçası)**
   - aircraft: Uçak (Aircraft modeli ile ilişki)
   - part: Parça (Part modeli ile ilişki)
   - added_at: Eklenme tarihi
   - added_by: Ekleyen kullanıcı (User modeli ile ilişki)

5. **Production (Üretim)**
   - team: Üretici takım (Team modeli ile ilişki)
   - part: Üretilen parça (Part modeli ile ilişki)
   - quantity: Üretim miktarı
   - created_at: Üretim tarihi
   - created_by: Üreten kullanıcı (User modeli ile ilişki)

### İş Kuralları

- Her takım sadece kendi tipine uygun parçaları üretebilir
- Montaj takımı parça üretemez, sadece uçak montajı yapabilir
- Her parça belirli bir uçak modeline özgüdür ve başka modellerde kullanılamaz
- Her uçak modeli için belirli sayıda ve tipte parça gereklidir
- Bir parça bir uçakta kullanıldığında stoktan düşer
- Stok seviyesi minimum seviyenin altına düştüğünde uyarı verilir

## 🔒 Güvenlik Önlemleri

- Django'nun yerleşik güvenlik özellikleri (CSRF koruması, XSS koruması, vb.)
- Kullanıcı kimlik doğrulama ve yetkilendirme
- Form doğrulama ve veri temizleme
- Güvenli şifre politikaları
- HTTPS desteği (production ortamında)
- API erişim kontrolü

## ⚡ Performans Optimizasyonları

- Veritabanı sorgu optimizasyonları
- Önbellek kullanımı
- Lazy loading
- Sayfalama (pagination)
- Asenkron AJAX istekleri
- Statik dosya sıkıştırma ve CDN desteği

## 🤝 Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## İletişim

Proje Yöneticisi - [@kullanici](https://github.com/omerfeyzioglu)

