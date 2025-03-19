# Baykar Hava Aracı Üretim Takip Sistemi

## 📁 Project Documentation & Screenshots

### English
- 📊 **Diagrams:** [docs/diagrams/](docs/diagrams/) - System architecture, ER diagrams, and application flow charts
- 📷 **Screenshots:** [docs/images/](docs/images/) - User interface screenshots and usage examples
  - ℹ️ **Usage Notes:** [docs/images/README.txt](docs/images/readme.txt) - Important information about system functionality
- 📘 **Technical Documentation:** [docs/technical_documentation.md](docs/technical_documentation.md) - Detailed technical design and implementation
- 📗 **API Documentation:** [docs/api_documentation.md](docs/api_documentation.md) - API endpoints and usage examples

### Türkçe
- 📊 **Diyagramlar:** [docs/diagrams/](docs/diagrams/) - Sistem mimarisi, ER diyagramları ve uygulama akışları
- 📷 **Ekran Görüntüleri:** [docs/images/](docs/images/) - Arayüz ve kullanım örneklerinin ekran görüntüleri
  - ℹ️ **Kullanım Notları:** [docs/images/README.txt](docs/images/README.txt) - Sistem özellikleri hakkında önemli bilgiler
- 📘 **Teknik Dokümantasyon:** [docs/technical_documentation.md](docs/technical_documentation.md) - Detaylı teknik tasarım ve işleyiş
- 📗 **API Dokümantasyonu:** [docs/api_documentation.md](docs/api_documentation.md) - API endpoint'leri ve kullanım örnekleri

---

[English](#english) | [Türkçe](#türkçe)

## English

### Project Overview
Baykar Aircraft Production Tracking System is a comprehensive web application developed to track Baykar's UAV (Unmanned Aerial Vehicle) production processes. The system is designed to monitor part production, inventory management, assembly process, and production statistics.

### Table of Contents
- [Project Features](#project-features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
  - [Requirements](#requirements)
  - [Local Installation](#local-installation)
  - [Docker Installation](#docker-installation)
- [Usage](#usage)
  - [User Roles and Permissions](#user-roles-and-permissions)
  - [Part Management](#part-management)
  - [Team Management](#team-management)
  - [Aircraft Assembly Process](#aircraft-assembly-process)
  - [Stock Tracking](#stock-tracking)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Data Model](#data-model)
- [Security Measures](#security-measures)
- [Performance Optimizations](#performance-optimizations)
- [Contributing](#contributing)
- [License](#license)

### Project Features

#### Core Features
- **User Management**: User registration, login, logout, and profile management
- **Team Management**: Management interface for Avionics, Body, Wing, Tail, and Assembly teams
- **Part Production**: Teams can produce parts within their responsibilities
- **Stock Tracking**: Monitoring part stock levels and low stock alerts
- **Aircraft Assembly**: Assembly team combines compatible parts to produce aircraft
- **Production Statistics**: Visualization of production processes with graphs and tables
- **Multi-language Support**: Turkish and English language options
- **REST API**: Complete RESTful API for all system functionality

#### Key Highlights
- **Team-Based Production System**: Each team can only produce parts within their domain of expertise
- **Part-Team Type Validation**: System validates that teams can only produce their designated part types
- **Part Compatibility Checking**: Parts are aircraft-specific and cannot be used across different aircraft models
- **Stock Management**: Automatic updates of inventory when parts are produced or used in aircraft assembly
- **Production Tracking**: Each stock increase is recorded as a production event and attributed to the team
- **Low Stock Alerts**: System warns when stock levels fall below the minimum threshold
- **Complete CRUD Operations**: Full Create, Read, Update, Delete functionality for all resources

#### Aircraft Models
- TB2 (Bayraktar TB2)
- TB3 (Bayraktar TB3)
- AKINCI (Bayraktar AKINCI)
- KIZILELMA (Bayraktar KIZILELMA)

#### Part Types
- Wing
- Body
- Tail
- Avionics

#### Team Types
- Wing Team
- Body Team
- Tail Team
- Avionics Team
- Assembly Team

### Technology Stack

#### Backend
- **Python 3.8+**: Main programming language
- **Django 5.0+**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Database
- **drf-spectacular**: API documentation (Swagger/OpenAPI)

#### Frontend
- **HTML5/CSS3**: Page structure and styling
- **JavaScript/jQuery**: Client-side interactions
- **Bootstrap 5**: Responsive design
- **DataTables**: Data tables
- **Chart.js**: Graphs and data visualization
- **Font Awesome**: Icons
- **Toastr.js**: Notifications

#### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container management
- **Git**: Version control

### Installation

#### Requirements
- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)
- virtualenv (optional)

#### Local Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/omerfeyzioglu/aircraft-manufacturing-web-application.git
   cd aircraft-manufacturing-web-application
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create PostgreSQL database:
   ```bash
   createdb aircraft-manufacturing  # PostgreSQL command line tool
   ```

5. Configure database settings:
   Update database connection information in `baykar/settings.py` or create `.env` file.

6. Run database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Start development server:
   ```bash
   python manage.py runserver
   ```

9. Visit `http://127.0.0.1:8000/` in your browser to view the application.

#### Docker Installation
The easiest way to get started is using Docker:

```bash
# Clone the repository
git clone https://github.com/yourusername/baykar-production.git
cd baykar-production

# Start the Docker containers
docker-compose up -d

# The application will be available at:
# http://localhost:8000
# API documentation: http://localhost:8000/api/schema/swagger/
```

### Usage

#### User Roles and Permissions
The system assigns users to teams, and each team has its own area of responsibility:

- **Avionics Team**: Can only produce avionics parts
- **Body Team**: Can only produce body parts
- **Wing Team**: Can only produce wing parts
- **Tail Team**: Can only produce tail parts
- **Assembly Team**: Cannot produce parts, can only assemble aircraft

#### Part Management
1. **Part Production**:
   - Login as relevant team member
   - Go to "Parts" page
   - Click "New Part Production"
   - Select part type, aircraft model, and quantity
   - Click "Produce"

2. **Part List**:
   - View all parts
   - Filter by part type, aircraft model, and stock status
   - View parts with low stock levels

#### Team Management
1. **Team Creation** (Admin):
   - Login to admin panel
   - Go to "Teams" section
   - Click "Add Team"
   - Set team name and type
   - Select team members

2. **Team List**:
   - View all teams
   - Filter by team type
   - View team members and production statistics

#### Aircraft Assembly Process
1. **New Aircraft Start** (Assembly Team):
   - Login as assembly team member
   - Go to "Aircraft" page
   - Click "New Aircraft"
   - Select aircraft model
   - Click "Start"

2. **Part Addition** (Assembly Team):
   - Select an aircraft from the list
   - Click "Add Part"
   - Select part to add
   - Click "Add"
   - Aircraft is automatically completed when all required parts are added

3. **Aircraft List**:
   - View all aircraft
   - Filter by aircraft model, status, and assembly team
   - View completion percentage and missing parts

#### Stock Tracking
1. **Stock Status**:
   - View parts with critical stock levels from "Low Stock Alerts" section on main page
   - View detailed stock information from "Parts" page

2. **Production History**:
   - View production history of a part from "Parts" page
   - View date, quantity, and producing team information

### API Documentation
The system provides a comprehensive REST API for programmatic access to all functions:

- **API Endpoint**: `/api/`
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

#### Basic API Endpoints
- `/api/parts/`: Part management
- `/api/teams/`: Team management
- `/api/aircraft/`: Aircraft management

#### Special API Actions
- `/api/teams/{id}/produce_part/`: Part production
- `/api/aircraft/{id}/add_part/`: Adding part to aircraft
- `/api/aircraft/{id}/parts_summary/`: Aircraft parts summary

### Project Structure
```
baykar/
├── baykar/                  # Project main directory
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── production/              # Production application
│   ├── migrations/          # Database migrations
│   ├── templates/           # Application templates
│   ├── models.py            # Data models
│   ├── views.py             # Views
│   ├── urls.py              # URL configuration
│   ├── serializers.py       # API serializers
│   ├── signals.py           # Django signals
│   └── apps.py              # Application configuration
├── templates/               # Project templates
│   ├── base.html            # Base template
│   ├── home.html            # Home page
│   ├── registration/        # Authentication templates
│   ├── parts/               # Parts templates
│   ├── teams/               # Teams templates
│   └── aircraft/            # Aircraft templates
├── static/                  # Static files
│   ├── css/                 # CSS files
│   ├── js/                  # JavaScript files
│   └── img/                 # Images
├── media/                   # User uploaded files
├── requirements.txt         # Python dependencies
├── manage.py                # Django management script
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
└── README.md                # Project documentation
```

### Data Model

#### Core Models
1. **Part**
   - name: Part name
   - team_type: Producing team type
   - aircraft_type: Aircraft type
   - stock: Stock quantity
   - minimum_stock: Minimum stock level

2. **Team**
   - name: Team name
   - team_type: Team type
   - members: Team members (relation with User model)

3. **Aircraft**
   - aircraft_type: Aircraft type
   - assembly_team: Assembly team (relation with Team model)
   - parts: Parts added to aircraft (relation with Part model)
   - created_at: Creation date
   - completed_at: Completion date

4. **AircraftPart**
   - aircraft: Aircraft (relation with Aircraft model)
   - part: Part (relation with Part model)
   - added_at: Addition date
   - added_by: User who added (relation with User model)

5. **Production**
   - team: Producing team (relation with Team model)
   - part: Produced part (relation with Part model)
   - quantity: Production quantity
   - created_at: Production date
   - created_by: User who produced (relation with User model)

#### Business Rules
- Each team can only produce parts suitable for their type
- Assembly team cannot produce parts, can only assemble aircraft
- Each part is specific to a certain aircraft model and cannot be used in other models
- Each aircraft model requires a specific number and type of parts
- When a part is used in an aircraft, it is deducted from stock
- Alert is given when stock level falls below minimum level

#### Database Relationship Diagram

![Database Relationship Diagram](docs/diagrams/database_diagram.png)

*Figure 1: Database Entity Relationship Diagram showing the relationships between all database models*

#### Aircraft Production State Diagram

![Aircraft Production State Diagram](docs/diagrams/state_diagram.png)

*Figure 2: State Diagram showing the various states an aircraft goes through during manufacturing*

#### Assembly Process Activity Diagram

![Assembly Process Activity Diagram](docs/diagrams/activity_diagram.png)

*Figure 3: Activity Diagram illustrating the workflow of aircraft assembly process*

### Security Measures
- Django's built-in security features (CSRF protection, XSS protection, etc.)
- User authentication and authorization
- Form validation and data sanitization
- Secure password policies
- HTTPS support (in production environment)
- API access control

### Performance Optimizations
- Database query optimizations
- Cache usage
- Lazy loading
- Pagination
- Asynchronous AJAX requests
- Static file compression and CDN support

### Contributing
1. Fork the project
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add some amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### License
This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

### Docker Usage and Troubleshooting

#### Docker Setup
To run the project with Docker, follow these steps:

1. **Install Docker and Docker Compose**: Make sure Docker and Docker Compose are installed on your system.

2. **Navigate to the Project Directory**: In the terminal or command prompt, navigate to the project directory.

3. **Start Containers**:
   ```bash
   docker-compose up -d
   ```

4. **Apply Database Migrations**:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create Superuser**:
   For Windows users:
   ```bash
   winpty docker-compose exec web python manage.py createsuperuser
   ```
   For other operating systems:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Collect Static Files**:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

7. **Check the Application**: Go to `http://localhost:8000/` in your browser.

#### Common Issues

##### 1. TTY Error
- **Error Message**: "Superuser creation skipped due to not running in a TTY."
- **Solution**: For Windows users, use the `winpty` command to create a superuser:
  ```bash
  winpty docker-compose exec web python manage.py createsuperuser
  ```

##### 2. Docker Compose Version Warning
- **Error Message**: "version is obsolete"
- **Solution**: This is a warning and does not affect the system. You can continue using the current version of Docker Compose.

##### 3. URL Namespace Warnings
- **Error Message**: "URL namespace 'admin' isn't unique."
- **Description**: This warning shows URL conflicts but does not affect the operation of the application.
- **Solution**: Can be ignored as it doesn't prevent the application from working. If desired, you can optimize the URL structure in later stages of the project.

##### 4. Windows MINGW64 Terminal Issues
- **Issue**: When using Windows Git Bash or MINGW64 terminal, you may experience TTY or interactive shell problems.
- **Solution**:
   * Use Windows CMD or PowerShell
   * Or use the `winpty` prefix:
   ```bash
   winpty docker-compose exec web bash
   winpty docker-compose exec web python manage.py createsuperuser
   ```

#### Additional Information
- To check container status: `docker-compose ps`
- To view container logs: `docker-compose logs -f web`
- To restart containers if there's an issue: `docker-compose down && docker-compose up -d`
- When working with Docker, always check error messages in the terminal or command prompt.

## Türkçe

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
- **REST API**: Tüm sistem işlevselliği için eksiksiz RESTful API

#### Önemli Özellikler
- **Takım Tabanlı Üretim Sistemi**: Her takım yalnızca kendi uzmanlık alanındaki parçaları üretebilir
- **Parça-Takım Tipi Doğrulama**: Sistem, takımların yalnızca belirlenmiş parça tiplerini üretebilmesini doğrular
- **Parça Uyumluluk Kontrolü**: Parçalar hava aracına özeldir ve farklı hava aracı modelleri arasında kullanılamaz
- **Stok Yönetimi**: Parçalar üretildiğinde veya hava aracı montajında kullanıldığında envanterin otomatik güncellenmesi
- **Üretim İzleme**: Her stok artışı bir üretim olayı olarak kaydedilir ve takıma atfedilir
- **Düşük Stok Uyarıları**: Stok seviyeleri minimum eşiğin altına düştüğünde sistem uyarı verir
- **Tam CRUD İşlemleri**: Tüm kaynaklar için eksiksiz Oluşturma, Okuma, Güncelleme, Silme işlevselliği

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

## 💻 Teknoloji Yığını

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
   git clone https://github.com/omerfeyzioglu/aircraft-manufacturing-web-application.git
   cd aircraft-manufacturing-web-application
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
Başlamanın en kolay yolu Docker kullanmaktır:

```bash
# Depoyu klonlayın
git clone https://github.com/kullaniciadi/baykar-production.git
cd baykar-production

# Docker konteynerlerini başlatın
docker-compose up -d

# Uygulama şu adreste kullanılabilir olacaktır:
# http://localhost:8000
# API dokümantasyonu: http://localhost:8000/api/schema/swagger/
```

### REST API
Sistem, tüm işlemler için kapsamlı bir RESTful API sağlar:

- `/api/parts/`: Parçaları yönetin (GET, POST, PUT, DELETE)
- `/api/teams/`: Takımları yönetin (GET, POST, PUT, DELETE)
- `/api/teams/{id}/produce_part/`: Belirli bir takım için parça üretin
- `/api/teams/{id}/add_member/`: Bir takıma üye ekleyin
- `/api/teams/{id}/remove_member/`: Bir takımdan üye çıkarın
- `/api/aircraft/`: Hava araçlarını yönetin (GET, POST, PUT, DELETE)
- `/api/aircraft/{id}/complete_production/`: Hava aracı üretimini tamamlayın
- `/api/users/`: Kullanıcıları yönetin (GET, POST, PUT)

Uygulamayı başlattıktan sonra API dokümantasyonuna `/api/schema/swagger/` adresinden erişilebilir.

### Common Issues

#### 1. TTY Error
- **Error Message**: "Superuser creation skipped due to not running in a TTY."
- **Solution**: For Windows users, use the `winpty` command to create a superuser:
```bash
winpty docker-compose exec web python manage.py createsuperuser
```

#### 2. Docker Compose Version Warning
- **Error Message**: "version is obsolete"
- **Solution**: This is a warning and does not affect the system. You can continue using the current version of Docker Compose.

#### 3. URL Namespace Warnings
- **Error Message**: "URL namespace 'admin' isn't unique."
- **Description**: This warning shows URL conflicts but does not affect the operation of the application.
- **Solution**: Can be ignored as it doesn't prevent the application from working. If desired, you can optimize the URL structure in later stages of the project.

#### 4. Windows MINGW64 Terminal Issues
- **Issue**: When using Windows Git Bash or MINGW64 terminal, you may experience TTY or interactive shell problems.
- **Solution**:
   * Use Windows CMD or PowerShell
   * Or use the `winpty` prefix:
```bash
winpty docker-compose exec web bash
winpty docker-compose exec web python manage.py createsuperuser
```

#### Additional Information
- To check container status: `docker-compose ps`
- To view container logs: `docker-compose logs -f web`
- To restart containers if there's an issue: `docker-compose down && docker-compose up -d`
- When working with Docker, always check error messages in the terminal or command prompt.

### Docker Kurulumu
Başlamanın en kolay yolu Docker kullanmaktır:

```bash
# Depoyu klonlayın
git clone https://github.com/kullaniciadi/baykar-production.git
cd baykar-production

# Docker konteynerlerini başlatın
docker-compose up -d

# Uygulama şu adreste kullanılabilir olacaktır:
# http://localhost:8000
# API dokümantasyonu: http://localhost:8000/api/schema/swagger/
```

### REST API
Sistem, tüm işlemler için kapsamlı bir RESTful API sağlar:

- `/api/parts/`: Parçaları yönetin (GET, POST, PUT, DELETE)
- `/api/teams/`: Takımları yönetin (GET, POST, PUT, DELETE)
- `/api/teams/{id}/produce_part/`: Belirli bir takım için parça üretin
- `/api/teams/{id}/add_member/`: Bir takıma üye ekleyin
- `/api/teams/{id}/remove_member/`: Bir takımdan üye çıkarın
- `/api/aircraft/`: Hava araçlarını yönetin (GET, POST, PUT, DELETE)
- `/api/aircraft/{id}/complete_production/`: Hava aracı üretimini tamamlayın
- `/api/users/`: Kullanıcıları yönetin (GET, POST, PUT)

Uygulamayı başlattıktan sonra API dokümantasyonuna `/api/schema/swagger/` adresinden erişilebilir.

### Karşılaşılabilecek Sorunlar

#### 1. TTY Hatası
- **Hata Mesajı**: "Superuser creation skipped due to not running in a TTY."
- **Çözüm**: Windows kullanıcıları için `winpty` komutunu kullanarak süper kullanıcı oluşturun:
```bash
winpty docker-compose exec web python manage.py createsuperuser
```

#### 2. Docker Compose Versiyon Uyarısı
- **Hata Mesajı**: "version is obsolete"
- **Çözüm**: Bu bir uyarıdır ve sistemi etkilemez. Docker Compose'un güncel versiyonunu kullanmaya devam edebilirsiniz.

#### 3. URL Namespace Uyarıları
- **Hata Mesajı**: "URL namespace 'admin' isn't unique."
- **Açıklama**: Bu uyarı, URL çakışmalarını gösterir ancak uygulamanın çalışmasını etkilemez.
- **Çözüm**: Uygulamanın çalışmasını engellemediği için görmezden gelinebilir. İsterseniz, projenin ilerleyen aşamalarında URL yapısını optimize edebilirsiniz.

#### 4. Windows MINGW64 Terminal Sorunları
- **Sorun**: Windows Git Bash veya MINGW64 terminali kullanırken TTY veya interaktif shell sorunları yaşanabilir.
- **Çözüm**:
   * Windows CMD veya PowerShell kullanın
   * Veya `winpty` önekini kullanın:
```bash
winpty docker-compose exec web bash
winpty docker-compose exec web python manage.py createsuperuser
```

### Ek Bilgiler
- Konteyner durumunu kontrol etmek için: `docker-compose ps`
- Konteyner loglarını görüntülemek için: `docker-compose logs -f web`
- Bir sorun olduğunda konteynerleri yeniden başlatmak için: `docker-compose down && docker-compose up -d`
- Docker ile çalışırken, her zaman terminal veya komut istemcisinde hata mesajlarını kontrol edin.

---

## Contact | İletişim

### English
For questions and support, please contact:
- Project Manager: [@omerfeyzioglu](https://github.com/omerfeyzioglu)
- Project Repository: [https://github.com/omerfeyzioglu/aircraft-manufacturing-web-application](https://github.com/omerfeyzioglu/aircraft-manufacturing-web-application)

### Türkçe
Sorularınız ve destek için lütfen iletişime geçin:
- Proje Yöneticisi: [@omerfeyzioglu](https://github.com/omerfeyzioglu)
- Proje Deposu: [https://github.com/omerfeyzioglu/aircraft-manufacturing-web-application](https://github.com/omerfeyzioglu/aircraft-manufacturing-web-application) 
