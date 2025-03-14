# Baykar Hava Aracı Üretim Takip Sistemi - API Dokümantasyonu

Bu dokümantasyon, Baykar Hava Aracı Üretim Takip Sistemi'nin API'sini açıklamaktadır. API, Django REST Framework kullanılarak geliştirilmiştir ve OpenAPI (Swagger) standardına uygundur.

## İçindekiler

- [Genel Bilgiler](#genel-bilgiler)
- [Kimlik Doğrulama](#kimlik-doğrulama)
- [Parça API](#parça-api)
- [Takım API](#takım-api)
- [Uçak API](#uçak-api)
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

#### Yeni Parça Oluştur

**Endpoint**: `POST /api/parts/`

**Açıklama**: Yeni bir parça oluşturur.

**İstek Gövdesi**:
```json
{
  "team_type": "AVIONICS",
  "aircraft_type": "TB2",
  "stock": 10,
  "minimum_stock": 5
}
```

**Örnek Yanıt**:
```json
{
  "id": 2,
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

#### Parça Güncelle

**Endpoint**: `PUT /api/parts/{id}/`

**Açıklama**: Bir parçayı günceller.

**İstek Gövdesi**:
```json
{
  "stock": 20,
  "minimum_stock": 10
}
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
  "stock": 20,
  "minimum_stock": 10,
  "is_low_stock": false
}
```

#### Parça Sil

**Endpoint**: `DELETE /api/parts/{id}/`

**Açıklama**: Bir parçayı siler.

**Örnek İstek**:
```
DELETE /api/parts/1/
```

**Örnek Yanıt**:
```
204 No Content
```

#### Düşük Stoklu Parçalar

**Endpoint**: `GET /api/parts/low_stock/`

**Açıklama**: Stok miktarı minimum stok seviyesinin altında olan parçaları listeler.

**Örnek İstek**:
```
GET /api/parts/low_stock/
```

**Örnek Yanıt**:
```json
[
  {
    "id": 1,
    "name": "TB2 Avionics",
    "team_type": "AVIONICS",
    "get_team_type_display": "Aviyonik",
    "aircraft_type": "TB2",
    "get_aircraft_type_display": "TB2",
    "stock": 3,
    "minimum_stock": 5,
    "is_low_stock": true
  }
]
```

#### Parça Kullanım Bilgisi

**Endpoint**: `GET /api/parts/{id}/usage/`

**Açıklama**: Bir parçanın hangi uçaklarda kullanıldığını gösterir.

**Örnek İstek**:
```
GET /api/parts/1/usage/
```

**Örnek Yanıt**:
```json
{
  "part_id": 1,
  "part_name": "TB2 Avionics",
  "team_type": "AVIONICS",
  "team_name": "Aviyonik",
  "aircraft_type": "TB2",
  "aircraft_name": "TB2",
  "stock": 3,
  "minimum_stock": 5,
  "usage_count": 1,
  "usage": [
    {
      "aircraft_id": 1,
      "aircraft_type": "TB2",
      "aircraft_name": "TB2",
      "assembly_team": "Montaj",
      "status": "Devam Ediyor",
      "added_at": "2023-03-14 15:30",
      "added_by": "Test User"
    }
  ]
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
GET /api/teams/?team_type=AVIONICS
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
      "name": "Avionics Team",
      "team_type": "AVIONICS",
      "member_count": 2,
      "total_production": 15,
      "created_at": "2023-03-14T15:30:00Z"
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
  "name": "Avionics Team",
  "team_type": "AVIONICS",
  "member_count": 2,
  "total_production": 15,
  "created_at": "2023-03-14T15:30:00Z"
}
```

#### Yeni Takım Oluştur

**Endpoint**: `POST /api/teams/`

**Açıklama**: Yeni bir takım oluşturur.

**İstek Gövdesi**:
```json
{
  "name": "New Avionics Team",
  "team_type": "AVIONICS",
  "members": [1, 2]
}
```

**Örnek Yanıt**:
```json
{
  "id": 2,
  "name": "New Avionics Team",
  "team_type": "AVIONICS",
  "member_count": 2,
  "total_production": 0,
  "created_at": "2023-03-14T16:30:00Z"
}
```

#### Takım Güncelle

**Endpoint**: `PUT /api/teams/{id}/`

**Açıklama**: Bir takımı günceller.

**İstek Gövdesi**:
```json
{
  "name": "Updated Avionics Team"
}
```

**Örnek Yanıt**:
```json
{
  "id": 1,
  "name": "Updated Avionics Team",
  "team_type": "AVIONICS",
  "member_count": 2,
  "total_production": 15,
  "created_at": "2023-03-14T15:30:00Z"
}
```

#### Takım Sil

**Endpoint**: `DELETE /api/teams/{id}/`

**Açıklama**: Bir takımı siler.

**Örnek İstek**:
```
DELETE /api/teams/1/
```

**Örnek Yanıt**:
```
204 No Content
```

#### Takıma Üye Ekle

**Endpoint**: `POST /api/teams/{id}/add_member/`

**Açıklama**: Bir takıma yeni bir üye ekler.

**İstek Gövdesi**:
```json
{
  "user": 3
}
```

**Örnek Yanıt**:
```json
{
  "detail": "Kullanıcı testuser takıma eklendi."
}
```

#### Takımdan Üye Çıkar

**Endpoint**: `POST /api/teams/{id}/remove_member/`

**Açıklama**: Bir takımdan bir üyeyi çıkarır.

**İstek Gövdesi**:
```json
{
  "user": 3
}
```

**Örnek Yanıt**:
```json
{
  "detail": "Kullanıcı testuser takımdan çıkarıldı."
}
```

#### Takım Üyeleri

**Endpoint**: `GET /api/teams/{id}/members/`

**Açıklama**: Bir takımın tüm üyelerini listeler.

**Örnek İstek**:
```
GET /api/teams/1/members/
```

**Örnek Yanıt**:
```json
[
  {
    "id": 1,
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com"
  },
  {
    "id": 2,
    "username": "anotheruser",
    "first_name": "Another",
    "last_name": "User",
    "email": "another@example.com"
  }
]
```

#### Müsait Kullanıcılar

**Endpoint**: `GET /api/teams/available_users/`

**Açıklama**: Herhangi bir takıma atanmamış kullanıcıları listeler.

**Örnek İstek**:
```
GET /api/teams/available_users/
```

**Örnek Yanıt**:
```json
[
  {
    "id": 3,
    "username": "availableuser",
    "first_name": "Available",
    "last_name": "User",
    "email": "available@example.com"
  }
]
```

#### Parça Üret

**Endpoint**: `POST /api/teams/{id}/produce_part/`

**Açıklama**: Takım tarafından parça üretimi yapar.

**İstek Gövdesi**:
```json
{
  "part": 1,
  "quantity": 5
}
```

**Örnek Yanıt**:
```json
{
  "detail": "Parça başarıyla üretildi.",
  "new_stock": 15
}
```

#### Üretim Geçmişi

**Endpoint**: `GET /api/teams/{id}/production-history/`

**Açıklama**: Takımın üretim geçmişini listeler.

**Örnek İstek**:
```
GET /api/teams/1/production-history/
```

**Örnek Yanıt**:
```json
[
  {
    "id": 1,
    "team": 1,
    "team_name": "Avionics Team",
    "part": 1,
    "part_name": "TB2 Avionics",
    "quantity": 5,
    "created_by": 1,
    "created_by_username": "testuser",
    "created_at": "2023-03-14T15:30:00Z"
  }
]
```

## Uçak API

Uçak API'si, uçakların yönetimi için kullanılır.

### Endpoint'ler

#### Uçak Listesi

**Endpoint**: `GET /api/aircraft/`

**Açıklama**: Tüm uçakları listeler.

**Parametreler**:
- `aircraft_type` (isteğe bağlı): Uçak tipine göre filtrele (TB2, TB3, AKINCI, KIZILELMA)
- `status` (isteğe bağlı): Duruma göre filtrele (in_production, completed)

**Örnek İstek**:
```
GET /api/aircraft/?aircraft_type=TB2&status=in_production
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
      "assembly_team": 5,
      "assembly_team_name": "Assembly Team",
      "is_complete": false,
      "created_at": "2023-03-14T15:30:00Z",
      "completed_at": null
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
  "assembly_team": 5,
  "assembly_team_name": "Assembly Team",
  "is_complete": false,
  "created_at": "2023-03-14T15:30:00Z",
  "completed_at": null
}
```

#### Yeni Uçak Oluştur

**Endpoint**: `POST /api/aircraft/`

**Açıklama**: Yeni bir uçak oluşturur.

**İstek Gövdesi**:
```json
{
  "aircraft_type": "TB2"
}
```

**Örnek Yanıt**:
```json
{
  "id": 2,
  "aircraft_type": "TB2",
  "get_aircraft_type_display": "TB2",
  "assembly_team": 5,
  "assembly_team_name": "Assembly Team",
  "is_complete": false,
  "created_at": "2023-03-14T16:30:00Z",
  "completed_at": null
}
```

#### Uçak Güncelle

**Endpoint**: `PUT /api/aircraft/{id}/`

**Açıklama**: Bir uçağı günceller.

**İstek Gövdesi**:
```json
{
  "assembly_team": 6
}
```

**Örnek Yanıt**:
```json
{
  "id": 1,
  "aircraft_type": "TB2",
  "get_aircraft_type_display": "TB2",
  "assembly_team": 6,
  "assembly_team_name": "New Assembly Team",
  "is_complete": false,
  "created_at": "2023-03-14T15:30:00Z",
  "completed_at": null
}
```

#### Uçak Sil

**Endpoint**: `DELETE /api/aircraft/{id}/`

**Açıklama**: Bir uçağı siler.

**Örnek İstek**:
```
DELETE /api/aircraft/1/
```

**Örnek Yanıt**:
```
204 No Content
```

#### Uçağa Parça Ekle

**Endpoint**: `POST /api/aircraft/{id}/add_part/`

**Açıklama**: Bir uçağa parça ekler.

**İstek Gövdesi**:
```json
{
  "part": 1
}
```

**Örnek Yanıt**:
```json
{
  "detail": "TB2 Avionics parçası başarıyla eklendi.",
  "is_complete": false,
  "missing_parts": {
    "AVIONICS": 4,
    "BODY": 10,
    "WING": 4,
    "TAIL": 2
  }
}
```

#### Üretimi Tamamla

**Endpoint**: `POST /api/aircraft/{id}/complete_production/`

**Açıklama**: Uçak üretimini tamamlar.

**Örnek İstek**:
```
POST /api/aircraft/1/complete_production/
```

**Örnek Yanıt**:
```json
{
  "detail": "Uçak üretimi tamamlandı."
}
```

#### Parça Özeti

**Endpoint**: `GET /api/aircraft/{id}/parts-summary/`

**Açıklama**: Uçağın parça özetini gösterir.

**Örnek İstek**:
```
GET /api/aircraft/1/parts-summary/
```

**Örnek Yanıt**:
```json
{
  "required_parts": [
    {
      "team": "Aviyonik",
      "required": 5,
      "current": 1,
      "remaining": 4,
      "completion": 20
    },
    {
      "team": "Gövde",
      "required": 10,
      "current": 0,
      "remaining": 10,
      "completion": 0
    },
    {
      "team": "Kanat",
      "required": 4,
      "current": 0,
      "remaining": 4,
      "completion": 0
    },
    {
      "team": "Kuyruk",
      "required": 2,
      "current": 0,
      "remaining": 2,
      "completion": 0
    }
  ],
  "current_parts": [
    {
      "id": 1,
      "name": "TB2 Avionics",
      "team_type": "AVIONICS",
      "team_name": "Aviyonik",
      "added_at": "2023-03-14 15:30",
      "added_by": "Test User"
    }
  ],
  "missing_parts": 20,
  "is_complete": false
}
```

#### Üretim Geçmişi

**Endpoint**: `GET /api/aircraft/{id}/production-history/`

**Açıklama**: Uçağın üretim geçmişini gösterir.

**Örnek İstek**:
```
GET /api/aircraft/1/production-history/
```

**Örnek Yanıt**:
```json
{
  "aircraft_id": 1,
  "aircraft_type": "TB2",
  "aircraft_name": "TB2",
  "history": [
    {
      "part_id": 1,
      "part_name": "TB2 Avionics",
      "team_type": "AVIONICS",
      "team_name": "Aviyonik",
      "aircraft_type": "TB2",
      "aircraft_name": "TB2",
      "added_at": "2023-03-14 15:30",
      "added_by": "Test User",
      "user_id": 1
    }
  ]
}
```

#### Kullanılabilir Parçalar

**Endpoint**: `GET /api/aircraft/{id}/available-parts/`

**Açıklama**: Uçağa eklenebilecek parçaları listeler.

**Örnek İstek**:
```
GET /api/aircraft/1/available-parts/
```

**Örnek Yanıt**:
```json
{
  "parts": [
    {
      "id": 1,
      "name": "TB2 Avionics",
      "team_type": "AVIONICS",
      "get_team_type_display": "Aviyonik",
      "aircraft_type": "TB2",
      "get_aircraft_type_display": "TB2",
      "stock": 9,
      "minimum_stock": 5,
      "is_low_stock": false
    },
    {
      "id": 2,
      "name": "TB2 Body",
      "team_type": "BODY",
      "get_team_type_display": "Gövde",
      "aircraft_type": "TB2",
      "get_aircraft_type_display": "TB2",
      "stock": 15,
      "minimum_stock": 5,
      "is_low_stock": false
    }
  ]
}
```

## Hata Kodları

API, aşağıdaki HTTP durum kodlarını kullanır:

- `200 OK`: İstek başarılı
- `201 Created`: Kaynak başarıyla oluşturuldu
- `204 No Content`: İstek başarılı, ancak içerik yok (genellikle silme işlemlerinde)
- `400 Bad Request`: İstek geçersiz
- `401 Unauthorized`: Kimlik doğrulama gerekli
- `403 Forbidden`: Yetkilendirme hatası
- `404 Not Found`: Kaynak bulunamadı
- `500 Internal Server Error`: Sunucu hatası

## Örnek Kullanım Senaryoları

### Senaryo 1: Parça Üretimi ve Stok Kontrolü

1. Takım listesini al:
   ```
   GET /api/teams/
   ```

2. Parça listesini al:
   ```
   GET /api/parts/
   ```

3. Parça üret:
   ```
   POST /api/teams/1/produce_part/
   {
     "part": 1,
     "quantity": 5
   }
   ```

4. Düşük stoklu parçaları kontrol et:
   ```
   GET /api/parts/low_stock/
   ```

### Senaryo 2: Uçak Üretimi

1. Yeni uçak oluştur:
   ```
   POST /api/aircraft/
   {
     "aircraft_type": "TB2"
   }
   ```

2. Uçağa parça ekle:
   ```
   POST /api/aircraft/1/add_part/
   {
     "part": 1
   }
   ```

3. Parça özetini kontrol et:
   ```
   GET /api/aircraft/1/parts-summary/
   ```

4. Üretimi tamamla:
   ```
   POST /api/aircraft/1/complete_production/
   ```

5. Üretim geçmişini kontrol et:
   ```
   GET /api/aircraft/1/production-history/
   ```