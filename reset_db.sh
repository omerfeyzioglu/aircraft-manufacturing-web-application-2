#!/bin/bash
# Veritabanı sıfırlama aracı

# Script dosyasını Docker container'a kopyala
echo "Reset scripti container'a kopyalanıyor..."
docker cp reset_db.py baykar-web-1:/app/

# Reset scriptini çalıştır
echo "Reset scripti çalıştırılıyor..."
docker-compose exec web python /app/reset_db.py

echo "İşlem tamamlandı." 