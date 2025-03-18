# Veritabanı sıfırlama aracı (PowerShell versiyonu)

# Otomatik sıfırlama parametresi
param(
    [switch]$Auto
)

# Parametreler
$autoParam = ""
if ($Auto) {
    $autoParam = "--auto"
    Write-Host "Otomatik mod aktif: Tüm veritabanı içeriği onay istenmeden sıfırlanacak!" -ForegroundColor Red
}

# Script dosyasını Docker container'a kopyala
Write-Host "Reset scripti container'a kopyalanıyor..." -ForegroundColor Green
docker cp reset_db.py baykar-web-1:/app/

# Reset scriptini çalıştır
Write-Host "Reset scripti çalıştırılıyor..." -ForegroundColor Yellow
docker-compose exec web python /app/reset_db.py $autoParam

Write-Host "İşlem tamamlandı." -ForegroundColor Green 