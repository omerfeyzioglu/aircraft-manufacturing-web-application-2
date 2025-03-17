# Baykar Hava Aracı Üretim Takip Sistemi - Teknik Dokümantasyon

Bu dokümantasyon, Baykar Hava Aracı Üretim Takip Sistemi'nin teknik detaylarını, API kullanımını, veri modellerini ve geliştirme rehberini içermektedir. Bu belge, projeye katkıda bulunmak isteyen geliştiriciler için hazırlanmıştır.

## İçindekiler

- [Sistem Mimarisi](#sistem-mimarisi)
- [Veri Modelleri ve İlişkiler](#veri-modelleri-ve-i̇lişkiler)
- [Yetkilendirme ve Güvenlik](#yetkilendirme-ve-güvenlik)
- [API Referansı](#api-referansı)
- [İş Mantığı ve Validasyonlar](#i̇ş-mantığı-ve-validasyonlar)
- [Frontend Yapısı](#frontend-yapısı)
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
4. **PostgreSQL/SQLite**: İlişkisel veritabanı yönetim sistemi

### Frontend Bileşenleri

1. **Django Templates**: Server-side rendering için HTML şablonları
2. **Bootstrap 5**: Responsive tasarım framework'ü
3. **JavaScript/jQuery**: İstemci tarafı etkileşimler
4. **AJAX**: Asenkron veri alışverişi
5. **Chart.js**: Veri görselleştirme
6. **Swiper.js**: Slider ve geçiş efektleri

### Sistem Akışı

1. İstek Django URL yönlendiricisi tarafından karşılanır
2. TeamCheckMiddleware tüm istekleri kontrol eder ve yetkisiz kullanıcıların erişimini engeller
3. İlgili view fonksiyonu veya ViewSet çağrılır
4. View, gerekli modelleri ve verileri işler
5. İşlenen veriler şablona aktarılır veya API yanıtı olarak döndürülür
6. Şablon render edilir veya JSON yanıtı oluşturulur
7. Yanıt istemciye gönderilir

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
```

### Ana Modeller

#### Team (Takım)

```python
class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name='Takım Adı')
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES, verbose_name='Takım Tipi')
    members = models.ManyToManyField(User, related_name='team_members', blank=True, verbose_name='Üyeler')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    
    # Metodlar
    def can_produce_part(self, part):
        """Takımın belirli bir parçayı üretip üretemeyeceğini kontrol eder"""
        if self.team_type == 'ASSEMBLY':
            return False
        return self.team_type == part.team_type
```

#### Part (Parça)

```python
class Part(models.Model):
    name = models.CharField(max_length=100, verbose_name='Parça Adı')
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES, verbose_name='Üretici Takım Tipi')
    aircraft_type = models.CharField(max_length=20, choices=AIRCRAFT_TYPES, verbose_name='Hava Aracı Tipi')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stok Miktarı')
    minimum_stock = models.PositiveIntegerField(default=5, verbose_name='Minimum Stok Miktarı')
    is_low_stock = models.BooleanField(default=False, verbose_name='Düşük Stok')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    
    # Metodlar
    def increase_stock(self, quantity):
        """Stok miktarını artırır"""
        self.stock += quantity
        self.save()
        
    def decrease_stock(self, quantity):
        """Stok miktarını azaltır"""
        if self.stock < quantity:
            raise ValidationError("Stok miktarı yetersiz")
        self.stock -= quantity
        self.save()
```

#### Aircraft (Uçak)

```python
class Aircraft(models.Model):
    aircraft_type = models.CharField(max_length=20, choices=AIRCRAFT_TYPES, verbose_name='Hava Aracı Tipi')
    assembly_team = models.ForeignKey(Team, on_delete=models.PROTECT, limit_choices_to={'team_type': 'ASSEMBLY'}, verbose_name='Montaj Takımı', null=True, blank=True)
    parts = models.ManyToManyField(Part, through='AircraftPart', related_name='aircrafts', verbose_name='Parçalar')
    is_complete = models.BooleanField(default=False, verbose_name='Tamamlandı mı?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tamamlanma Tarihi')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_aircrafts', verbose_name='Oluşturan', null=True, blank=True)
    
    # Metodlar
    def check_completion_status(self):
        """Uçağın tamamlanma durumunu kontrol eder"""
        required_parts = self.get_missing_parts()
        
        # Tüm gerekli parçalar eklenmiş mi kontrol et
        is_all_parts_added = all(count == 0 for count in required_parts.values())
        
        # Eğer tüm parçalar eklenmiş ve uçak henüz tamamlanmamışsa
        if is_all_parts_added and not self.is_complete:
            self.is_complete = True
            self.completed_at = timezone.now()
            self.save()
        
        return is_all_parts_added
```

#### AircraftPart (Uçak Parça İlişkisi)

```python
class AircraftPart(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name='aircraft_parts', verbose_name='Hava Aracı')
    part = models.ForeignKey(Part, on_delete=models.PROTECT, related_name='aircraft_parts', verbose_name='Parça')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Eklenme Tarihi')
    added_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='added_parts', verbose_name='Ekleyen', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Hava Aracı Parçası'
        verbose_name_plural = 'Hava Aracı Parçaları'
        unique_together = ['aircraft', 'part']
```

#### Production (Üretim)

```python
class Production(models.Model):
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='productions', verbose_name='Üretici Takım')
    part = models.ForeignKey(Part, on_delete=models.PROTECT, related_name='productions', verbose_name='Üretilen Parça')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Miktar')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='productions', verbose_name='Oluşturan', null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
```

## Yetkilendirme ve Güvenlik

Sistemin güvenliği, katmanlı bir yaklaşımla sağlanmaktadır:

### CustomLoginView

```python
class CustomLoginView(LoginView):
    """
    Takıma atanmamış kullanıcıların girişini engelleyen özel login view.
    """
    template_name = 'login.html'

    def form_valid(self, form):
        """
        Kullanıcı doğrulandı, giriş yapılmadan önce takım üyeliğini kontrol et.
        Takımı olmayan kullanıcıların girişini engelle.
        """
        user = form.get_user()
        
        # Eğer kullanıcı admin değilse takım kontrolü yap
        if not user.is_superuser:
            # Kullanıcının takımını kontrol et
            if not Team.objects.filter(members=user).exists():
                form.add_error(None, 'Sisteme giriş yapabilmek için bir takıma atanmış olmanız gerekmektedir. '
                                   'Lütfen sistem yöneticisi (admin) ile iletişime geçiniz.')
                return self.form_invalid(form)
        
        # Eğer buraya kadar geldiyse, ya admin ya da takımı olan bir kullanıcı
        return super().form_valid(form)
        
    def get_form(self, form_class=None):
        """Form oluşturulurken kullanıcı kontrolü yap"""
        form = super().get_form(form_class)
        
        # Eğer kullanıcı zaten giriş yapmışsa ve takımı yoksa, giriş yapmasını engelle
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            if not Team.objects.filter(members=self.request.user).exists():
                form.add_error(None, 'Sisteme giriş yapabilmek için bir takıma atanmış olmanız gerekmektedir. '
                                  'Lütfen sistem yöneticisi (admin) ile iletişime geçiniz.')
                return form
        
        return form

    def dispatch(self, request, *args, **kwargs):
        """Her istek öncesi kullanıcı kontrolü yap"""
        # Eğer kullanıcı zaten giriş yapmışsa ve takımı yoksa, çıkış yaptır
        if request.user.is_authenticated and not request.user.is_superuser:
            if not Team.objects.filter(members=request.user).exists():
                from django.contrib.auth import logout
                logout(request)
                messages.error(request, 'Sisteme giriş yapabilmek için bir takıma atanmış olmanız gerekmektedir. '
                                     'Lütfen sistem yöneticisi (admin) ile iletişime geçiniz.')
                return HttpResponseRedirect(self.get_login_url())
        
        return super().dispatch(request, *args, **kwargs)
```

### TeamCheckMiddleware

```python
class TeamCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Giriş yapmış kullanıcılar için takım kontrolü yap
        if request.user.is_authenticated and not request.user.is_superuser:
            # Admin sayfasına erişim için kontrol yapma
            if not request.path.startswith('/admin/'):
                # Kullanıcının bir takımı var mı kontrol et
                user_team = Team.objects.filter(members=request.user).first()
                if not user_team:
                    # Takımı olmayan kullanıcıyı çıkış yaptır
                    from django.contrib.auth import logout
                    from django.contrib import messages
                    logout(request)
                    messages.error(
                        request, 
                        'Sisteme giriş yapabilmek için bir takıma atanmış olmanız gerekmektedir. '
                        'Lütfen sistem yöneticisi (admin) ile iletişime geçiniz.'
                    )
                    # Login sayfasına yönlendir
                    from django.shortcuts import redirect
                    return redirect('login')
        
        response = self.get_response(request)
        return response
```

### View Bazlı Yetkilendirme

```python
@login_required
def aircraft_detail(request, pk):
    """Uçak detay görünümü."""
    # Sadece montaj takımı üyeleri ve süper kullanıcılar erişebilir
    user_team = Team.objects.filter(members=request.user).first()
    
    # Süper kullanıcı değilse ve montaj takımında değilse erişimi engelle
    if not request.user.is_superuser and (not user_team or user_team.team_type != 'ASSEMBLY'):
        messages.error(
            request, 
            '<span style="color: red; font-weight: bold;">Bu sayfaya erişim yetkiniz bulunmamaktadır.</span>'
        )
        return redirect('production:home')
    
    aircraft = get_object_or_404(Aircraft, pk=pk)
    
    # Kullanıcının takımına göre erişimi kontrol et (süper kullanıcı için erişim serbest)
    if (not request.user.is_superuser and 
        user_team and 
        aircraft.assembly_team is not None and 
        aircraft.assembly_team != user_team):
        # Kullanıcı sadece kendi takımının uçaklarını ve atanmamış uçakları görebilir
        return render(request, 'production/access_denied.html')
    
    context = {
        'aircraft': aircraft,
        'parts': AircraftPart.objects.filter(aircraft=aircraft),
        'missing_parts': aircraft.get_missing_parts(),
        'user_team': user_team,
    }
    return render(request, 'production/aircraft_detail.html', context)
```

### API Yetkilendirme

```python
class IsTeamMemberOrReadOnly(permissions.BasePermission):
    """
    Takım üyelerine yazma izni, diğerlerine sadece okuma izni veren özel izin sınıfı.
    """
    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS isteklerine izin ver
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Süper kullanıcıya her zaman izin ver
        if request.user.is_superuser:
            return True
        
        # Kullanıcı giriş yapmış olmalı
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS isteklerine izin ver
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Süper kullanıcıya her zaman izin ver
        if request.user.is_superuser:
            return True
```

## Frontend Yapısı

Sistemin frontend yapısı, aşağıdaki teknoloji ve bileşenlerden oluşmaktadır:

### Kullanıcı Arayüzü

- **Base Template**: Tüm sayfaların temel şablonu (`base.html`)
- **Login Sayfası**: Kullanıcı ve admin girişi için Swiper.js ile kaydırılabilir form (`login.html`)
- **Dashboard**: Üretim ve stok durumunun genel görünümü (`home.html`)
- **Parça Listesi**: Üretilen ve stokta olan parçaların listesi (`part_list.html`)
- **Üretim Listesi**: Gerçekleştirilen üretimlerin listesi (`production_list.html`)
- **Uçak Listesi**: Üretilen ve üretim aşamasındaki uçakların listesi (`aircraft_list.html`)
- **Uçak Detay**: Uçak montaj durumu ve parça bilgileri (`aircraft_detail.html`)

### Arayüz Optimizasyonları

1. **Login Sayfası Optimizasyonları**:
   - Video arka plan için ön yükleme ve otomatik geçiş
   - Düşük bağlantı hızlarında arka plan resmi kullanma
   - GPU hızlandırmalı animasyonlar (`will-change` özelliği)
   - Slider geçişlerinde performans iyileştirmeleri

2. **Dashboard Optimizasyonları**:
   - Grafik ve tabloların lazy loading ile yüklenmesi
   - AJAX ile arka planda veri güncelleme
   - Verilerin client tarafında önbelleklenmesi

## Performans Optimizasyonları

Sistemin performansını artırmak için aşağıdaki stratejiler uygulanmıştır:

### Veritabanı Optimizasyonları

- **İlişkisel Sorgular**: `select_related` ve `prefetch_related` kullanımı
- **Toplu Sorgular**: `bulk_create` ve `bulk_update` kullanımı
- **İndexler**: Sık sorgulanan alanlarda indeks kullanımı

### Frontend Optimizasyonları

- **Video Optimizasyonu**: Login sayfasındaki video için önbellek ve lazy loading
- **CSS Optimizasyonu**: CSS'in kritik olmayan kısmının asenkron yüklenmesi
- **JavaScript Optimizasyonu**: Defer ve async özniteliklerinin kullanımı
- **Görsel Optimizasyonu**: Sıkıştırılmış ve uygun boyutlarda görsel kullanımı

### Middleware Optimizasyonları

- **TeamCheckMiddleware**: Gereksiz veritabanı sorgularının önlenmesi
- **Önbellek Kullanımı**: Yetki kontrollerinin önbelleklenmesi

## Deployment Rehberi

### Docker ile Deployment

1. **Gereksinimler**:
   - Docker
   - Docker Compose

2. **Kurulum Adımları**:
   - Projeyi klonlayın: `git clone https://github.com/kullanici/baykar.git`
   - .env dosyasını oluşturun ve yapılandırın
   - Docker Compose'u başlatın: `docker-compose up -d`
   - Migrasyonları yapın: `docker-compose exec web python manage.py migrate`
   - Superuser oluşturun: `docker-compose exec web python manage.py createsuperuser`
   - Statik dosyaları toplayın: `docker-compose exec web python manage.py collectstatic`

### Manuel Deployment

1. **Gereksinimler**:
   - Python 3.8+
   - PostgreSQL
   - Nginx/Apache

2. **Kurulum Adımları**:
   - Projeyi klonlayın: `git clone https://github.com/kullanici/baykar.git`
   - Sanal ortam oluşturun: `python -m venv venv`
   - Sanal ortamı aktif edin: `source venv/bin/activate`
   - Bağımlılıkları yükleyin: `pip install -r requirements.txt`
   - .env dosyasını oluşturun ve yapılandırın
   - Migrasyonları yapın: `python manage.py migrate`
   - Superuser oluşturun: `python manage.py createsuperuser`
   - Statik dosyaları toplayın: `python manage.py collectstatic`
   - Nginx/Apache'yi yapılandırın
   - Gunicorn veya uWSGI hizmetini başlatın

## Geliştirme Rehberi

### Yeni Bir Özellik Eklemek

1. **Modelin Tanımlanması**:
   - `production/models.py` dosyasında modeli tanımlayın
   - Migrasyonları oluşturun: `python manage.py makemigrations`
   - Migrasyonları uygulayın: `python manage.py migrate`

2. **Görünümün Oluşturulması**:
   - `production/views.py` dosyasında görünümü tanımlayın
   - İlgili şablonu oluşturun
   - URL'yi `production/urls.py` dosyasına ekleyin

3. **API Entegrasyonu (Gerekirse)**:
   - `production/serializers.py` dosyasında serileştiriciyi tanımlayın
   - `production/views.py` dosyasında ViewSet'i tanımlayın
   - URL'yi `baykar/urls.py` dosyasına ekleyin

4. **Frontend Entegrasyonu**:
   - İlgili şablonu oluşturun veya güncelleyin
   - Gerekli CSS ve JavaScript dosyalarını ekleyin

5. **Test Yazımı**:
   - `production/tests.py` dosyasında testleri yazın
   - Testleri çalıştırın: `python manage.py test production`

---

Bu teknik dokümantasyon, Baykar Hava Aracı Üretim Takip Sistemi'nin geliştiriciler için kapsamlı bir referans kaynağıdır. Projeye katkıda bulunmadan önce bu dokümantasyonu incelemeniz önerilir. 