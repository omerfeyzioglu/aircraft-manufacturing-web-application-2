# Baykar Hava Aracı Üretim Takip Sistemi - API Dokümantasyonu

Bu dokümantasyon, Baykar Hava Aracı Üretim Takip Sistemi'nin API'sini açıklamaktadır. API, Django REST Framework kullanılarak geliştirilmiştir ve OpenAPI (Swagger) standardına uygundur.

## İçindekiler

- [Genel Bilgiler](#genel-bilgiler)
- [Kimlik Doğrulama](#kimlik-doğrulama)
- [Yetkilendirme](#yetkilendirme)
- [Parça API](#parça-api)
- [Takım API](#takım-api)
- [Uçak API](#uçak-api)
- [Kullanıcı API](#kullanıcı-api)
- [Hata Kodları](#hata-kodları)
- [Örnek Kullanım Senaryoları](#örnek-kullanım-senaryoları)

## Genel Bilgiler

API, aşağıdaki temel URL'ler üzerinden erişilebilir:

- **API Kök URL**: `/api/`
- **API Şeması**: `/api/schema/`
- **Swagger UI**: `/api/docs/`
- **ReDoc UI**: `/api/redoc/`

API, JSON formatında veri alışverişi yapar. İsteklerde ve yanıtlarda `Content-Type: application/json` kullanılır.

## Kimlik Doğrulama

API, oturum tabanlı kimlik doğrulama kullanmaktadır. API isteklerinde CSRF token gerekmektedir. Kullanıcılar, web arayüzü üzerinden giriş yaptıktan sonra API'yi kullanabilirler.

**ÖNEMLİ**: Takımı olmayan kullanıcılar sisteme giriş yapamaz ve API'ye erişemezler. Bu kontrol `TeamCheckMiddleware` tarafından sağlanmaktadır.

## Yetkilendirme

API, rol tabanlı yetkilendirme kullanmaktadır. Kullanıcılar, takım rollerine göre belirli API endpointlerine erişebilirler:

- **Süper Kullanıcı (Admin)**: Tüm API endpointlerine erişebilir
- **Takım Üyeleri**: Sadece kendi takımlarının sorumluluğundaki kaynaklara erişebilir

API'de özel izin sınıfları kullanılmaktadır:

- **IsTeamMemberOrReadOnly**: Takım üyelerine yazma izni, diğerlerine sadece okuma izni verir
- **IsAssemblyTeamMember**: Sadece montaj takımı üyelerine erişim izni verir
- **IsPartTeamMember**: Sadece ilgili parça tipindeki takım üyelerine erişim izni verir

## Parça API

Parça API'si, parçaların yönetimi için kullanılır.

### Endpoint'ler

#### Parça Listesi

**Endpoint**: `GET /api/parts/`

**Açıklama**: Tüm parçaları listeler.

**Parametreler**:
- `team_type` (isteğe bağlı): Takım tipine göre filtrele (AVIONICS, BODY, WING, TAIL)
- `aircraft_type` (isteğe bağlı): Uçak tipine göre filtrele (TB2, TB3, AKINCI, KIZILELMA)
- `stock_status` (isteğe bağlı): Stok durumuna göre filtrele (low, out)

**Örnek İstek**:
```
GET /api/parts/?team_type=AVIONICS&aircraft_type=TB2
```

**Örnek Yanıt**:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "TB2 Avionics",
      "team_type": "AVIONICS",
      "get_team_type_display": "Aviyonik",
      "aircraft_type": "TB2",
      "get_aircraft_type_display": "TB2",
      "stock": 10,
      "minimum_stock": 5,
      "is_low_stock": false
    }
  ]
}
```

#### Parça Detayı

**Endpoint**: `GET /api/parts/{id}/`

**Açıklama**: Belirli bir parçanın detaylarını gösterir.

**Örnek İstek**:
```
GET /api/parts/1/
```

**Örnek Yanıt**:
```json
{
  "id": 1,
  "name": "TB2 Avionics",
  "team_type": "AVIONICS",
  "get_team_type_display": "Aviyonik",
  "aircraft_type": "TB2",
  "get_aircraft_type_display": "TB2",
  "stock": 10,
  "minimum_stock": 5,
  "is_low_stock": false
}
```

#### Parça Stok Artırma

**Endpoint**: `POST /api/parts/{id}/increase_stock/`

**Açıklama**: Belirli bir parçanın stok miktarını artırır.

**İstek Gövdesi**:
```json
{
  "quantity": 5
}
```

**Örnek Yanıt**:
```json
{
  "id": 1,
  "name": "TB2 Avionics",
  "stock": 15,
  "message": "Stok başarıyla artırıldı."
}
```

## Takım API

Takım API'si, takımların yönetimi için kullanılır.

### Endpoint'ler

#### Takım Listesi

**Endpoint**: `GET /api/teams/`

**Açıklama**: Tüm takımları listeler.

**Parametreler**:
- `team_type` (isteğe bağlı): Takım tipine göre filtrele (AVIONICS, BODY, WING, TAIL, ASSEMBLY)

**Örnek İstek**:
```
GET /api/teams/?team_type=ASSEMBLY
```

**Örnek Yanıt**:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Montaj Takımı A",
      "team_type": "ASSEMBLY",
      "get_team_type_display": "Montaj",
      "member_count": 3,
      "members": [
        {
          "id": 2,
          "username": "montaj_uzman1"
        },
        {
          "id": 3,
          "username": "montaj_uzman2"
        },
        {
          "id": 4,
          "username": "montaj_teknisyen1"
        }
      ]
    }
  ]
}
```

#### Takım Detayı

**Endpoint**: `GET /api/teams/{id}/`

**Açıklama**: Belirli bir takımın detaylarını gösterir.

**Örnek İstek**:
```
GET /api/teams/1/
```

**Örnek Yanıt**:
```json
{
  "id": 1,
  "name": "Montaj Takımı A",
  "team_type": "ASSEMBLY",
  "get_team_type_display": "Montaj",
  "member_count": 3,
  "members": [
    {
      "id": 2,
      "username": "montaj_uzman1"
    },
    {
      "id": 3,
      "username": "montaj_uzman2"
    },
    {
      "id": 4,
      "username": "montaj_teknisyen1"
    }
  ]
}
```

#### Parça Üretimi

**Endpoint**: `POST /api/teams/{id}/produce_part/`

**Açıklama**: Belirli bir takımın parça üretmesini sağlar. Sadece ilgili takım üyeleri tarafından kullanılabilir.

**İstek Gövdesi**:
```json
{
  "part_id": 1,
  "quantity": 5
}
```

**Örnek Yanıt**:
```json
{
  "message": "5 adet TB2 Avionics başarıyla üretildi.",
  "part": {
    "id": 1,
    "name": "TB2 Avionics",
    "stock": 15
  }
}
```

## Uçak API

Uçak API'si, uçakların yönetimi için kullanılır.

### Endpoint'ler

#### Uçak Listesi

**Endpoint**: `GET /api/aircraft/`

**Açıklama**: Tüm uçakları listeler.

**Parametreler**:
- `aircraft_type` (isteğe bağlı): Uçak tipine göre filtrele (TB2, TB3, AKINCI, KIZILELMA)
- `assembly_team` (isteğe bağlı): Montaj takımına göre filtrele
- `is_complete` (isteğe bağlı): Tamamlanma durumuna göre filtrele (true, false)

**Örnek İstek**:
```
GET /api/aircraft/?aircraft_type=TB2&is_complete=false
```

**Örnek Yanıt**:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "aircraft_type": "TB2",
      "get_aircraft_type_display": "TB2",
      "assembly_team": {
        "id": 1,
        "name": "Montaj Takımı A"
      },
      "is_complete": false,
      "created_at": "2023-06-01T10:00:00Z",
      "completed_at": null,
      "missing_parts": {
        "AVIONICS": 1,
        "BODY": 1,
        "WING": 1,
        "TAIL": 1
      }
    }
  ]
}
```

#### Uçak Detayı

**Endpoint**: `GET /api/aircraft/{id}/`

**Açıklama**: Belirli bir uçağın detaylarını gösterir.

**Örnek İstek**:
```
GET /api/aircraft/1/
```

**Örnek Yanıt**:
```json
{
  "id": 1,
  "aircraft_type": "TB2",
  "get_aircraft_type_display": "TB2",
  "assembly_team": {
    "id": 1,
    "name": "Montaj Takımı A"
  },
  "is_complete": false,
  "created_at": "2023-06-01T10:00:00Z",
  "completed_at": null,
  "parts": [
    {
      "id": 1,
      "part": {
        "id": 1,
        "name": "TB2 Avionics"
      },
      "added_at": "2023-06-01T11:00:00Z",
      "added_by": {
        "id": 2,
        "username": "montaj_uzman1"
      }
    }
  ],
  "missing_parts": {
    "AVIONICS": 0,
    "BODY": 1,
    "WING": 1,
    "TAIL": 1
  }
}
```

#### Parça Ekleme

**Endpoint**: `POST /api/aircraft/{id}/add_part/`

**Açıklama**: Belirli bir uçağa parça ekler. Sadece montaj takımı üyeleri tarafından kullanılabilir.

**İstek Gövdesi**:
```json
{
  "part_id": 2
}
```

**Örnek Yanıt**:
```json
{
  "message": "TB2 Body başarıyla eklendi.",
  "is_complete": false,
  "missing_parts": {
    "AVIONICS": 0,
    "BODY": 0,
    "WING": 1,
    "TAIL": 1
  }
}
```

## Kullanıcı API

Kullanıcı API'si, kullanıcı bilgilerini almak için kullanılır.

### Endpoint'ler

#### Mevcut Kullanıcı

**Endpoint**: `GET /api/users/me/`

**Açıklama**: Giriş yapmış kullanıcının bilgilerini gösterir.

**Örnek İstek**:
```
GET /api/users/me/
```

**Örnek Yanıt**:
```json
{
  "id": 2,
  "username": "montaj_uzman1",
  "email": "montaj_uzman1@example.com",
  "first_name": "Ahmet",
  "last_name": "Yılmaz",
  "is_superuser": false,
  "teams": [
    {
      "id": 1,
      "name": "Montaj Takımı A",
      "team_type": "ASSEMBLY",
      "get_team_type_display": "Montaj"
    }
  ]
}
```

## Hata Kodları

API, aşağıdaki hata kodlarını döndürebilir:

| Kod | Açıklama |
|-----|----------|
| 400 | Bad Request - İstek parametreleri hatalı |
| 401 | Unauthorized - Kimlik doğrulama gerekli |
| 403 | Forbidden - Yetkilendirme hatası (takım yetkisi yok) |
| 404 | Not Found - Kaynak bulunamadı |
| 405 | Method Not Allowed - HTTP metodu desteklenmiyor |
| 500 | Internal Server Error - Sunucu hatası |

### Örnek Hata Yanıtı

```json
{
  "detail": "Bu işlem için yetkiniz bulunmamaktadır."
}
```

```json
{
  "non_field_errors": ["Bu parça stokta mevcut değil."]
}
```

```json
{
  "part_id": ["Bu alan gereklidir."]
}
```

## Örnek Kullanım Senaryoları

### Aviyonik Takımı - Parça Üretimi

```javascript
// Aviyonik parçası üretimi için AJAX isteği
$.ajax({
    url: '/api/teams/2/produce_part/',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        part_id: 1,  // TB2 Avionics
        quantity: 5
    }),
    success: function(response) {
        console.log('Parça başarıyla üretildi:', response.message);
        console.log('Yeni stok:', response.part.stock);
    },
    error: function(xhr) {
        console.error('Hata:', xhr.responseJSON.detail);
    }
});
```

### Montaj Takımı - Uçak Oluşturma ve Parça Ekleme

```javascript
// Yeni uçak oluşturma
$.ajax({
    url: '/api/aircraft/',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        aircraft_type: 'TB2',
        assembly_team_id: 1
    }),
    success: function(response) {
        console.log('Uçak başarıyla oluşturuldu:', response);
        
        // Oluşturulan uçağa parça ekleme
        $.ajax({
            url: '/api/aircraft/' + response.id + '/add_part/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                part_id: 1  // TB2 Avionics
            }),
            success: function(addResponse) {
                console.log('Parça başarıyla eklendi:', addResponse.message);
                console.log('Eksik parçalar:', addResponse.missing_parts);
            },
            error: function(xhr) {
                console.error('Parça ekleme hatası:', xhr.responseJSON.detail);
            }
        });
    },
    error: function(xhr) {
        console.error('Uçak oluşturma hatası:', xhr.responseJSON.detail);
    }
});
```