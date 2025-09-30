-- Создание расширений
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- Установка русской локали
ALTER DATABASE bas_flights SET lc_messages TO 'ru_RU.UTF-8';
ALTER DATABASE bas_flights SET lc_monetary TO 'ru_RU.UTF-8';
ALTER DATABASE bas_flights SET lc_numeric TO 'ru_RU.UTF-8';
ALTER DATABASE bas_flights SET lc_time TO 'ru_RU.UTF-8';

-- Создание схемы для геоданных
CREATE SCHEMA IF NOT EXISTS geo;

-- Таблица регионов РФ
CREATE TABLE IF NOT EXISTS geo.regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(10) NOT NULL,
    geometry GEOMETRY(MultiPolygon, 4326),
    center_point GEOMETRY(Point, 4326),
    area_km2 DECIMAL,
    population INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для геоданных
CREATE INDEX IF NOT EXISTS idx_regions_geometry ON geo.regions USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_regions_center ON geo.regions USING GIST(center_point);
CREATE INDEX IF NOT EXISTS idx_regions_name ON geo.regions(name);
CREATE INDEX IF NOT EXISTS idx_regions_code ON geo.regions(code);