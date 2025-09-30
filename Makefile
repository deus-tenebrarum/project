.PHONY: help build up down restart logs shell db-shell migrate test clean

help:
	@echo "Команды для управления проектом БАС:"
	@echo "  make build    - Сборка всех контейнеров"
	@echo "  make up       - Запуск всех сервисов"
	@echo "  make down     - Остановка всех сервисов"
	@echo "  make restart  - Перезапуск всех сервисов"
	@echo "  make logs     - Просмотр логов"
	@echo "  make shell    - Вход в контейнер backend"
	@echo "  make db-shell - Вход в PostgreSQL"
	@echo "  make migrate  - Выполнение миграций БД"
	@echo "  make test     - Запуск тестов"
	@echo "  make clean    - Очистка volumes и кэша"

build:
	docker-compose build --no-cache

up:
	docker-compose up -d
	@echo "Сервисы запущены:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend API: http://localhost:8000"
	@echo "  Swagger: http://localhost:8000/docs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec backend bash

db-shell:
	docker-compose exec db psql -U postgres -d bas_flights

migrate:
	docker-compose exec backend alembic upgrade head

test:
	docker-compose exec backend pytest tests/ -v

clean:
	docker-compose down -v
	docker system prune -f
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Загрузка тестовых данных
load-test-data:
	docker-compose exec backend python scripts/load_test_data.py

# Резервное копирование БД
backup:
	docker-compose exec db pg_dump -U postgres bas_flights > backup_$$(date +%Y%m%d_%H%M%S).sql

# Восстановление БД
restore:
	@read -p "Введите имя файла бэкапа: " file; \
	docker-compose exec -T db psql -U postgres bas_flights < $$file