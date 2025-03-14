# Baykar Hava Aracı Üretim Takip Sistemi - Teknik Dokümantasyon

Bu dokümantasyon, Baykar Hava Aracı Üretim Takip Sistemi'nin teknik detaylarını, API kullanımını, veri modellerini ve geliştirme rehberini içermektedir. Bu belge, projeye katkıda bulunmak isteyen geliştiriciler için hazırlanmıştır.

## İçindekiler

- [Sistem Mimarisi](#sistem-mimarisi)
- [Veri Modelleri ve İlişkiler](#veri-modelleri-ve-i̇lişkiler)
- [API Referansı](#api-referansı)
- [İş Mantığı ve Validasyonlar](#i̇ş-mantığı-ve-validasyonlar)
- [Frontend Yapısı](#frontend-yapısı)
- [Çoklu Dil Desteği](#çoklu-dil-desteği)
- [Güvenlik Uygulamaları](#güvenlik-uygulamaları)
- [Performans Optimizasyonları](#performans-optimizasyonları)
- [Test Stratejisi](#test-stratejisi)
- [Deployment Rehberi](#deployment-rehberi)
- [Geliştirme Rehberi](#geliştirme-rehberi)

## Sistem Mimarisi

Baykar Hava Aracı Üretim Takip Sistemi, Django web framework'ü üzerine inşa edilmiş bir MVC (Model-View-Controller) mimarisini kullanmaktadır. Sistem, aşağıdaki ana bileşenlerden oluşmaktadır:

### Backend Bileşenleri

1. **Django Core**: Temel web framework, URL yönlendirme, şablon işleme
2. **Django ORM**: Veritabanı etkileşimi ve model yönetimi
3. **Django REST Framework**: API geliştirme ve dokümantasyon
4. **PostgreSQL**: İlişkisel veritabanı yönetim sistemi

### Frontend Bileşenleri

1. **Django Templates**: Server-side rendering için HTML şablonları
2. **Bootstrap 5**: Responsive tasarım framework'ü
3. **JavaScript/jQuery**: İstemci tarafı etkileşimler
4. **AJAX**: Asenkron veri alışverişi
5. **DataTables**: Veri tabloları ve filtreleme
6. **Chart.js**: Veri görselleştirme

### Sistem Akışı

1. İstek Django URL yönlendiricisi tarafından karşılanır
2. İlgili view fonksiyonu veya ViewSet çağrılır
3. View, gerekli modelleri ve verileri işler
4. İşlenen veriler şablona aktarılır veya API yanıtı olarak döndürülür
5. Şablon render edilir veya JSON yanıtı oluşturulur
6. Yanıt istemciye gönderilir

## Veri Modelleri ve İlişkiler

### Temel Sabitler

```python
# Uçak tipleri
AIRCRAFT_TYPES = [
    ('TB2', 'TB2'),
    ('TB3', 'TB3'),
    ('AKINCI', 'AKINCI'),
    ('KIZILELMA', 'KIZILELMA'),
]

# Takım tipleri
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
```

### Model Tanımları

#### Team (Takım)

```python
class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name='Takım Adı')
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES, verbose_name='Takım Tipi')
    members = models.ManyToManyField(User, related_name='team_members', verbose_name='Üyeler')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    
    # Metodlar
    def can_produce_part(self, part):
        """Takımın belirli bir parçayı üretip üretemeyeceğini kontrol eder."""
        if self.team_type == 'ASSEMBLY':
            return False
        return self.team_type == part.team_type
```

#### Part (Parça)

```python
class Part(models.Model):
    name = models.CharField(max_length=100, verbose_name='Parça Adı')
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES, verbose_name='Üretici Takım')
    aircraft_type = models.CharField(max_length=10, choices=AIRCRAFT_TYPES, verbose_name='Uçak Tipi')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stok')
    minimum_stock = models.PositiveIntegerField(default=5, verbose_name='Minimum Stok')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    
    # Metodlar
    def increase_stock(self, quantity):
        """Stok miktarını artırır."""
        self.stock += quantity
        self.save()
        
    def decrease_stock(self, quantity):
        """Stok miktarını azaltır."""
        if self.stock < quantity:
            raise ValidationError('Yetersiz stok.')
        self.stock -= quantity
        self.save()
```

#### Aircraft (Uçak)

```python
class Aircraft(models.Model):
    aircraft_type = models.CharField(max_length=10, choices=AIRCRAFT_TYPES, verbose_name='Uçak Tipi')
    assembly_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, 
                                    limit_choices_to={'team_type': 'ASSEMBLY'}, 
                                    related_name='assembled_aircrafts',
                                    verbose_name='Montaj Takımı')
    parts = models.ManyToManyField(Part, through='AircraftPart', verbose_name='Parçalar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tamamlanma Tarihi')
    
    # Metodlar
    def get_missing_parts(self):
        """Eksik parçaları takım tipine göre döndürür."""
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
```

#### AircraftPart (Uçak Parçası)

```python
class AircraftPart(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, verbose_name='Uçak')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, verbose_name='Parça')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Eklenme Tarihi')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Ekleyen')
    
    # Metodlar
    def clean(self):
        """Parça ekleme validasyonları."""
        if self.part.aircraft_type != self.aircraft.aircraft_type:
            raise ValidationError('Bu parça bu uçak tipi için uygun değil.')
        if self.part.stock <= 0:
            raise ValidationError('Bu parçanın stokta yeterli miktarı yok.')
```

#### Production (Üretim)

```python
class Production(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='productions', verbose_name='Üretici Takım')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, verbose_name='Üretilen Parça')
    quantity = models.PositiveIntegerField(verbose_name='Miktar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Üretim Tarihi')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Üreten')
    
    # Metodlar
    def clean(self):
        """Üretim validasyonları."""
        if not self.team.can_produce_part(self.part):
            raise ValidationError('Bu takım bu parçayı üretemez.')
        if self.quantity <= 0:
            raise ValidationError('Üretim miktarı pozitif olmalıdır.')
```

### Veri İlişkileri

1. **User - Team**: Çoktan-çoğa ilişki (ManyToMany). Bir kullanıcı birden fazla takımda olabilir, bir takımda birden fazla kullanıcı olabilir.
2. **Team - Production**: Birden-çoğa ilişki (ForeignKey). Bir takım birden fazla üretim yapabilir.
3. **Part - Production**: Birden-çoğa ilişki (ForeignKey). Bir parça birden fazla üretimde kullanılabilir.
4. **Aircraft - Part**: Çoktan-çoğa ilişki (ManyToMany), AircraftPart ara tablosu üzerinden. Bir uçakta birden fazla parça olabilir, bir parça birden fazla uçakta kullanılabilir (farklı stok birimleri).
5. **Team - Aircraft**: Birden-çoğa ilişki (ForeignKey). Bir montaj takımı birden fazla uçak montajı yapabilir.

## API Referansı

### Kimlik Doğrulama

API, oturum tabanlı kimlik doğrulama kullanmaktadır. API isteklerinde CSRF token gerekmektedir.

### Endpoint'ler

#### Parça API

**Endpoint**: `/api/parts/`

| Metod | Endpoint | Açıklama | Parametreler |
|-------|----------|----------|--------------|
| GET | `/api/parts/` | Parça listesi | `team_type`, `aircraft_type`, `stock_status` |
| POST | `/api/parts/` | Yeni parça oluştur | `name`, `team_type`, `aircraft_type`, `stock`, `minimum_stock` |
| GET | `/api/parts/{id}/` | Parça detayı | - |
| PUT | `/api/parts/{id}/` | Parça güncelle | `stock`, `minimum_stock` |
| DELETE | `/api/parts/{id}/` | Parça sil | - |

#### Takım API

**Endpoint**: `/api/teams/`

| Metod | Endpoint | Açıklama | Parametreler |
|-------|----------|----------|--------------|
| GET | `/api/teams/` | Takım listesi | `team_type` |
| POST | `/api/teams/` | Yeni takım oluştur | `name`, `team_type`, `members` |
| GET | `/api/teams/{id}/` | Takım detayı | - |
| PUT | `/api/teams/{id}/` | Takım güncelle | `name`, `members` |
| DELETE | `/api/teams/{id}/` | Takım sil | - |
| POST | `/api/teams/{id}/produce_part/` | Parça üret | `part`, `quantity` |
| GET | `/api/teams/{id}/members/` | Takım üyeleri | - |
| POST | `/api/teams/{id}/add_member/` | Üye ekle | `user` |
| POST | `/api/teams/{id}/remove_member/` | Üye çıkar | `user` |

#### Uçak API

**Endpoint**: `/api/aircraft/`

| Metod | Endpoint | Açıklama | Parametreler |
|-------|----------|----------|--------------|
| GET | `/api/aircraft/` | Uçak listesi | `aircraft_type`, `status`, `assembly_team` |
| POST | `/api/aircraft/` | Yeni uçak oluştur | `aircraft_type`, `assembly_team` |
| GET | `/api/aircraft/{id}/` | Uçak detayı | - |
| PUT | `/api/aircraft/{id}/` | Uçak güncelle | `assembly_team` |
| DELETE | `/api/aircraft/{id}/` | Uçak sil | - |
| POST | `/api/aircraft/{id}/add_part/` | Parça ekle | `part` |
| GET | `/api/aircraft/{id}/parts_summary/` | Parça özeti | - |

### Örnek API Kullanımı

#### Parça Üretimi

```javascript
// Parça üretimi için AJAX isteği
$.ajax({
    url: '/api/teams/1/produce_part/',
    type: 'POST',
    data: {
        part: 5,
        quantity: 10
    },
    success: function(response) {
        console.log('Parça başarıyla üretildi.');
        console.log('Yeni stok: ' + response.new_stock);
    },
    error: function(xhr) {
        console.error('Hata: ' + xhr.responseJSON.detail);
    }
});
```

#### Uçağa Parça Ekleme

```javascript
// Uçağa parça ekleme için AJAX isteği
$.ajax({
    url: '/api/aircraft/3/add_part/',
    type: 'POST',
    data: {
        part: 8
    },
    success: function(response) {
        console.log('Parça başarıyla eklendi.');
        console.log('Tamamlanma durumu: ' + (response.is_complete ? 'Tamamlandı' : 'Devam ediyor'));
        console.log('Eksik parçalar: ', response.missing_parts);
    },
    error: function(xhr) {
        console.error('Hata: ' + xhr.responseJSON.detail);
    }
});
```

## İş Mantığı ve Validasyonlar

### Parça Üretimi

1. Sadece ilgili takım tipi kendi parçalarını üretebilir (Aviyonik takımı sadece aviyonik parçaları üretebilir)
2. Montaj takımı parça üretemez
3. Üretim miktarı pozitif olmalıdır
4. Parça adı, takım tipi ve uçak tipine göre otomatik oluşturulur (örn. "TB2 Kanat")

### Uçak Montajı

1. Sadece montaj takımı uçak oluşturabilir
2. Her uçak modeli için belirli sayıda ve tipte parça gereklidir
3. Parçalar sadece uyumlu uçak modellerine eklenebilir (TB2 parçası sadece TB2 uçağına eklenebilir)
4. Bir parça eklendiğinde stoktan düşer
5. Tüm gerekli parçalar eklendiğinde uçak otomatik olarak tamamlanır

### Stok Yönetimi

1. Parça stoku minimum seviyenin altına düştüğünde uyarı verilir
2. Stok yetersizse parça eklenemez
3. Parça silindiğinde ilişkili üretim kayıtları da silinir

## Frontend Yapısı

### Şablon Hiyerarşisi

```
templates/
├── base.html                # Ana şablon
├── home.html                # Ana sayfa
├── registration/            # Kimlik doğrulama şablonları
│   ├── login.html           # Giriş sayfası
│   └── password_change.html # Şifre değiştirme
├── parts/                   # Parça şablonları
│   └── list.html            # Parça listesi
├── teams/                   # Takım şablonları
│   └── list.html            # Takım listesi
└── aircraft/                # Uçak şablonları
    └── list.html            # Uçak listesi
```

### JavaScript Bileşenleri

1. **DataTables**: Tablo görüntüleme, sıralama ve filtreleme
2. **Chart.js**: Üretim istatistikleri ve stok durumu grafikleri
3. **AJAX İstekleri**: Asenkron veri alışverişi
4. **Form Validasyonu**: İstemci tarafı form doğrulama
5. **Toastr**: Bildirimler ve uyarılar
6. **Dil Değiştirme**: Çoklu dil desteği için JavaScript fonksiyonları

### CSS Yapısı

1. **Bootstrap 5**: Temel stil ve grid sistemi
2. **Custom CSS**: Özel stil tanımlamaları
3. **Responsive Tasarım**: Farklı ekran boyutlarına uyum

## Çoklu Dil Desteği

Sistem, Türkçe ve İngilizce dil desteği sunmaktadır. Dil değiştirme işlemi JavaScript ile gerçekleştirilmektedir.

### Dil Değiştirme Mekanizması

1. Dil seçimi localStorage'da saklanır
2. Sayfa yüklendiğinde mevcut dil ayarı kontrol edilir
3. Dil değiştirme butonu tıklandığında tüm metin içerikleri güncellenir
4. Dil değişikliği bildirim olarak gösterilir

### Çeviri Sözlüğü

```javascript
const translations = {
    'tr': {
        // Navbar
        'home': 'Ana Sayfa',
        'teams': 'Takımlar',
        'parts': 'Parçalar',
        'aircraft': 'Uçaklar',
        // ... diğer çeviriler
    },
    'en': {
        // Navbar
        'home': 'Home',
        'teams': 'Teams',
        'parts': 'Parts',
        'aircraft': 'Aircraft',
        // ... diğer çeviriler
    }
};
```

## Güvenlik Uygulamaları

### Kimlik Doğrulama ve Yetkilendirme

1. **Django Authentication**: Kullanıcı kimlik doğrulama
2. **Oturum Yönetimi**: Güvenli oturum işlemleri
3. **Rol Tabanlı Erişim Kontrolü**: Takım tipine göre yetkilendirme
4. **CSRF Koruması**: Cross-Site Request Forgery koruması

### Veri Validasyonu

1. **Form Validasyonu**: Sunucu tarafı form doğrulama
2. **Model Validasyonu**: Model seviyesinde veri doğrulama
3. **API Validasyonu**: API isteklerinde veri doğrulama

### Güvenli Kodlama Pratikleri

1. **SQL Injection Koruması**: ORM kullanımı
2. **XSS Koruması**: HTML escape ve güvenli şablon işleme
3. **HTTPS Desteği**: Güvenli veri iletimi

## Performans Optimizasyonları

### Veritabanı Optimizasyonları

1. **İndeksleme**: Sık sorgulanan alanlarda indeks kullanımı
2. **Select Related**: İlişkili verileri tek sorguda çekme
3. **Prefetch Related**: İlişkili verileri önceden yükleme
4. **Bulk Operations**: Toplu veri işlemleri

### Frontend Optimizasyonları

1. **Lazy Loading**: Gerektiğinde veri yükleme
2. **Pagination**: Büyük veri setlerinde sayfalama
3. **Minification**: JS ve CSS dosyalarını küçültme
4. **Caching**: Statik dosyaları önbellekleme

## Test Stratejisi

### Birim Testleri

1. **Model Testleri**: Model metodlarının testi
2. **View Testleri**: View fonksiyonlarının testi
3. **Form Testleri**: Form validasyonlarının testi
4. **API Testleri**: API endpointlerinin testi

### Entegrasyon Testleri

1. **İş Akışı Testleri**: Uçtan uca iş akışlarının testi
2. **Kullanıcı Senaryoları**: Gerçek kullanım senaryolarının testi

### Test Araçları

1. **Django TestCase**: Django'nun test framework'ü
2. **Coverage.py**: Test kapsamı ölçümü
3. **Factory Boy**: Test verisi oluşturma

## Deployment Rehberi

### Gereksinimler

1. **Python 3.8+**
2. **PostgreSQL 12+**
3. **Nginx** (web sunucusu)
4. **Gunicorn** (WSGI sunucusu)
5. **Docker** (isteğe bağlı)

### Docker ile Deployment

1. Docker Compose dosyasını yapılandırın
2. Ortam değişkenlerini `.env` dosyasında ayarlayın
3. Docker Compose ile konteynerları başlatın:
   ```bash
   docker-compose up -d
   ```
4. Veritabanı migrasyonlarını yapın:
   ```bash
   docker-compose exec web python manage.py migrate
   ```
5. Statik dosyaları toplayın:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### Manuel Deployment

1. Sanal ortam oluşturun ve bağımlılıkları yükleyin
2. PostgreSQL veritabanı oluşturun
3. Ortam değişkenlerini ayarlayın
4. Veritabanı migrasyonlarını yapın
5. Statik dosyaları toplayın
6. Gunicorn servisini yapılandırın
7. Nginx'i yapılandırın ve başlatın

## Geliştirme Rehberi

### Geliştirme Ortamı Kurulumu

1. Projeyi klonlayın
2. Sanal ortam oluşturun ve bağımlılıkları yükleyin
3. Veritabanı migrasyonlarını yapın
4. Geliştirme sunucusunu başlatın

### Kod Standartları

1. **PEP 8**: Python kod stili
2. **Django Coding Style**: Django'nun kod standartları
3. **JavaScript Style Guide**: JavaScript kod stili
4. **HTML/CSS Best Practices**: HTML ve CSS en iyi uygulamaları

### Geliştirme İş Akışı

1. Yeni bir branch oluşturun
2. Değişiklikleri yapın ve testleri yazın
3. Testleri çalıştırın
4. Değişiklikleri commit edin
5. Pull request açın
6. Code review sonrası merge edin

### Sürüm Yönetimi

1. **Semantic Versioning**: X.Y.Z (Major.Minor.Patch)
2. **Release Notes**: Her sürüm için değişiklik notları
3. **Git Tags**: Sürümleri etiketleme

---

Bu teknik dokümantasyon, Baykar Hava Aracı Üretim Takip Sistemi'nin geliştiriciler için kapsamlı bir referans kaynağıdır. Projeye katkıda bulunmadan önce bu dokümantasyonu incelemeniz önerilir. 