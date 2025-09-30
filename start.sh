#!/bin/bash

echo "🚀 Запуск системы анализа полетов БАС..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и Docker Compose."
    exit 1
fi

# Создание необходимых директорий
echo "📁 Создание директорий..."
mkdir -p uploads reports shapefiles nginx/logs nginx/ssl

# Проверка и создание .env файла для backend
if [ ! -f "PythonProject2/.env" ]; then
    echo "📝 Создание .env файла для backend..."
    cat > PythonProject2/.env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/bas_flights
REDIS_URL=redis://redis:6379/0
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=10080
LOG_LEVEL=INFO
EOF
fi

# Проверка и создание .env файла для frontend
if [ ! -f "frontend/bas_app/.env" ]; then
    echo "📝 Создание .env файла для frontend..."
    cat > frontend/bas_app/.env << EOF
REACT_APP_API_URL=http://localhost:8000/api/v1
EOF
fi

# Остановка старых контейнеров
echo "🛑 Остановка старых контейнеров..."
docker-compose down

# Сборка контейнеров
echo "🔨 Сборка контейнеров..."
docker-compose build

# Запуск сервисов
echo "🚀 Запуск сервисов..."
docker-compose up -d

# Ожидание запуска БД
echo "⏳ Ожидание запуска базы данных..."
sleep 10

# Выполнение миграций
echo "📊 Выполнение миграций БД..."
docker-compose exec backend alembic upgrade head 2>/dev/null || true

# Проверка статуса
echo "✅ Проверка статуса сервисов..."
docker-compose ps

echo "
✨ Система успешно запущена!

📍 Доступные сервисы:
   • Frontend: http://localhost:3000
   • Backend API: http://localhost:8000
   • API Документация: http://localhost:8000/docs
   • PostgreSQL: localhost:5432
   • Redis: localhost:6379

📖 Полезные команды:
   • Просмотр логов: docker-compose logs -f
   • Остановка: docker-compose down
   • Перезапуск: docker-compose restart
"