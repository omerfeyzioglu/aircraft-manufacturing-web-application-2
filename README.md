# Baykar Hava Aracı Üretim Takip Sistemi

Bu proje, hava aracı üretim süreçlerini izlemek ve yönetmek için geliştirilmiş bir web tabanlı sistemdir. Üretim takımları, parça üretimi, stok kontrolü ve montaj süreçlerini tek bir platformda yönetmeyi sağlar.

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
- [Güvenlik Özellikleri](#-güvenlik-özellikleri)
- [Performans Optimizasyonları](#-performans-optimizasyonları)
- [Lisans](#-lisans)

## 🚀 Proje Özellikleri

### Temel Özellikler

- **Kullanıcı Yönetimi**: Takıma dayalı yetkilendirme, login/logout, admin ve kullanıcı girişi
- **Takım Yönetimi**: Aviyonik, Gövde, Kanat, Kuyruk ve Montaj takımları için yönetim arayüzü
- **Parça Üretimi**: Takımların kendi sorumluluklarındaki parçaları üretmesi
- **Stok Takibi**: Parça stok seviyelerinin izlenmesi ve düşük stok uyarıları
- **Uçak Montajı**: Montaj takımının uyumlu parçaları birleştirerek uçak üretmesi
- **Üretim İstatistikleri**: Dashboard üzerinde görsel grafikler ve tablolarla üretim takibi

### Desteklenen Uçak Modelleri

- TB2 (Bayraktar TB2)
- TB3 (Bayraktar TB3)
- AKINCI (Bayraktar AKINCI)
- KIZILELMA (Bayraktar KIZILELMA)


## 💻 Teknoloji Yığını
=======
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
- **PostgreSQL**: Veritabanı (ayrıca SQLite test ortamı için)
- **drf-spectacular**: API dokümantasyonu (Swagger/OpenAPI)

### Frontend

- **HTML5/CSS3**: Sayfa yapısı ve stil
- **JavaScript/jQuery**: İstemci tarafı etkileşimler
- **Bootstrap 5**: Responsive tasarım
- **Swiper.js**: Slider ve geçiş efektleri
- **Chart.js**: Grafikler ve veri görselleştirme
- **Font Awesome**: İkonlar

### DevOps

- **Docker**: Konteynerizasyon
- **Docker Compose**: Çoklu konteyner yönetimi
- **Git**: Versiyon kontrolü

## 🔧 Kurulum

### Gereksinimler

- Python 3.8+
- PostgreSQL 12+ (veya SQLite)
- pip (Python paket yöneticisi)
- virtualenv (isteğe bağlı)

### Yerel Kurulum

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/kullanici/baykar.git
   cd baykar
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

4. Veritabanı ayarlarını yapılandırın:
   `baykar/settings.py` dosyasında veritabanı bağlantı bilgilerini güncelleyin veya `.env` dosyası oluşturun.

5. Veritabanı migrasyonlarını yapın:
   ```bash
   python manage.py migrate
   ```

6. Superuser oluşturun:
   ```bash
   python manage.py createsuperuser
   ```

7. Geliştirme sunucusunu başlatın:
   ```bash
   python manage.py runserver
   ```

8. Tarayıcınızda `http://127.0.0.1:8000/` adresine giderek uygulamayı görüntüleyin.

### Docker ile Kurulum

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/kullanici/baykar.git
   cd baykar
   ```

2. Docker Compose ile konteynerları başlatın:
   ```bash
   docker-compose up -d
   ```

3. Tarayıcınızda `http://localhost:8000/` adresine giderek uygulamayı görüntüleyin.

6. Tarayıcınızda `http://localhost:8000/admin` adresine giderek tüm operasyonları admin olarak görüntüleyebilir ardınıdan kullanıcı oluşturabilirsiniz. Çıkış yaptıktan sonra oluşturduğunuz kullanıcı bilgileri ile tekrardan sisteme giriş yapabilirsiniz.
## 📖 Kullanım

### Kullanıcı Rolleri ve İzinler

Sistem, kullanıcıları takımlara atar ve her takımın kendi sorumluluk alanı vardır:

- **Aviyonik Takımı**: Sadece aviyonik parçaları üretebilir
- **Gövde Takımı**: Sadece gövde parçaları üretebilir
- **Kanat Takımı**: Sadece kanat parçaları üretebilir
- **Kuyruk Takımı**: Sadece kuyruk parçaları üretebilir
- **Montaj Takımı**: Parça üretemez, sadece uçak montajı yapabilir

**ÖNEMLİ:** Takımı olmayan kullanıcılar sisteme giriş yapamaz ve admin ile iletişime geçmeleri istenir.

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

## 🔌 API Dokümantasyonu

Sistem, tüm işlevlere programatik erişim sağlayan kapsamlı bir REST API sunar:

- **API Endpoint**: `/api/`
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Şeması**: `/api/schema/`

Detaylı API dokümantasyonu için `/docs/api_documentation.md` dosyasını inceleyebilirsiniz.

## 📁 Proje Yapısı

```
baykar/
│
├── baykar/                  # Ana proje klasörü
│   ├── settings.py          # Proje ayarları
│   ├── urls.py              # Ana URL konfigürasyonu
│   └── wsgi.py              # WSGI konfigürasyonu
│
├── production/              # Ana uygulama
│   ├── models.py            # Veri modelleri
│   ├── views.py             # Görünümler
│   ├── urls.py              # URL yönlendirmeleri
│   ├── serializers.py       # API serileştiricileri
│   ├── admin.py             # Admin panel konfigürasyonu
│   ├── signals.py           # Signal handlers
│   └── tests.py             # Test dosyaları
│
├── templates/               # HTML şablonları
│   ├── base.html            # Ana şablon
│   ├── login.html           # Giriş sayfası
│   └── production/          # Üretim şablonları
│
├── static/                  # Statik dosyalar (CSS, JS, resimler)
│
├── media/                   # Kullanıcı yüklenen dosyalar
│
├── docs/                    # Dokümantasyon
│   ├── api_documentation.md # API dokümantasyonu
│   └── technical_documentation.md # Teknik dokümantasyon
│
├── requirements.txt         # Python bağımlılıkları
├── manage.py                # Django yönetim komutu
├── Dockerfile               # Docker konfigürasyonu
└── docker-compose.yml       # Docker Compose konfigürasyonu
```

## 📊 Veri Modeli

### Temel Modeller

- **Team**: Takımlar (Aviyonik, Gövde, Kanat, Kuyruk, Montaj)
- **Part**: Uçak parçaları (Aviyonik, Gövde, Kanat, Kuyruk)
- **Aircraft**: Üretilen uçaklar
- **AircraftPart**: Uçak-Parça ilişkisi
- **Production**: Üretim kayıtları

### İlişkiler

- Her takımın birden fazla üyesi olabilir (User)
- Her parça belirli bir takım tipi tarafından üretilir
- Her uçağın bir montaj takımı ve birden fazla parçası vardır
- Her üretim kaydı bir takım ve bir parça ile ilişkilidir

## 🔒 Güvenlik Özellikleri

- **Takım Bazlı Yetkilendirme**: Kullanıcılar sadece kendi takımlarının yetkileri dahilinde işlem yapabilir
- **Middleware Kontrolleri**: `TeamCheckMiddleware` ile takımı olmayan kullanıcılar sistemden çıkarılır
- **CustomLoginView**: Takımı olmayan kullanıcıların girişini engeller
- **Django Permission Framework**: Nesne seviyesinde yetkilendirme kontrolleri

## 🚀 Performans Optimizasyonları

- **Video ve Görsel Optimizasyonu**: Login sayfasındaki video ve görseller optimizasyonu
- **GPU Hızlandırma**: CSS `will-change` özelliği ile animasyonlarda daha akıcı performans
- **Lazy Loading**: Kaynakların gerektiğinde yüklenmesi

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---

## İletişim

Proje Yöneticisi - [@kullanici](https://github.com/omerfeyzioglu)


Proje Linki: [https://github.com/kullanici/baykar](https://github.com/kullanici/baykar) 
=======

