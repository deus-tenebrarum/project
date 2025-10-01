--
-- PostgreSQL database dump
--

-- Dumped from database version 15.8 (Debian 15.8-1.pgdg110+1)
-- Dumped by pg_dump version 15.8 (Debian 15.8-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: tiger; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tiger;


ALTER SCHEMA tiger OWNER TO postgres;

--
-- Name: tiger_data; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tiger_data;


ALTER SCHEMA tiger_data OWNER TO postgres;

--
-- Name: topology; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA topology;


ALTER SCHEMA topology OWNER TO postgres;

--
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';


--
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA public;


--
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: postgis_tiger_geocoder; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder WITH SCHEMA tiger;


--
-- Name: EXTENSION postgis_tiger_geocoder; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_tiger_geocoder IS 'PostGIS tiger geocoder and reverse geocoder';


--
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: flights; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.flights (
    id integer NOT NULL,
    sid character varying(20),
    flight_date timestamp without time zone,
    dep_point public.geometry(Point,4326),
    dep_coords character varying(50),
    dep_time timestamp without time zone,
    dep_region character varying(100),
    arr_point public.geometry(Point,4326),
    arr_coords character varying(50),
    arr_time timestamp without time zone,
    arr_region character varying(100),
    uav_type character varying(50),
    uav_reg character varying(50),
    operator character varying(200),
    operator_phone character varying(20),
    altitude_min double precision,
    altitude_max double precision,
    flight_zone json,
    duration_minutes integer,
    status character varying(20),
    center_name character varying(100),
    raw_shr text,
    raw_dep text,
    raw_arr text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.flights OWNER TO postgres;

--
-- Name: flights_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.flights_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.flights_id_seq OWNER TO postgres;

--
-- Name: flights_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.flights_id_seq OWNED BY public.flights.id;


--
-- Name: flights id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flights ALTER COLUMN id SET DEFAULT nextval('public.flights_id_seq'::regclass);


--
-- Data for Name: flights; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.flights (id, sid, flight_date, dep_point, dep_coords, dep_time, dep_region, arr_point, arr_coords, arr_time, arr_region, uav_type, uav_reg, operator, operator_phone, altitude_min, altitude_max, flight_zone, duration_minutes, status, center_name, raw_shr, raw_dep, raw_arr, created_at, updated_at) FROM stdin;
8885	7772187998	2025-02-01 00:00:00	\N	(59.95, 29.083333333333332)	2025-02-01 07:05:00	Ленинградская область	\N	\N	\N	\N	SHAR	\N	МАЛИНОВСКИЙ НИКИТА АЛЕКСАНДРОВИ4	\N	\N	\N	\N	\N	scheduled	Санкт-Петербургский	(SHR-ZZZZZ\n-ZZZZ0705\n-K0300M3000\n-DEP/5957N02905E DOF/250201 OPR/МАЛИНОВСКИЙ НИКИТА АЛЕКСАНДРОВИ4\n+79313215153 TYP/SHAR RMK/ОБОЛО4КА 300 ДЛЯ ЗОНДИРОВАНИЯ АТМОСФЕРЫ\nSID/7772187998)	-TITLE IDEP\n-SID 7772187998\n-ADD 250201\n-ATD 0705\n-ADEP ZZZZ\n-ADEPZ 5957N02905E\n-PAP 0		2025-10-01 17:18:46.933358	2025-10-01 17:18:46.933362
8886	7772251137	2025-01-24 00:00:00	\N	(44.13333333333333, 43.13333333333333)	2025-01-24 06:00:00	Неопределен	\N	(44.13333333333333, 43.13333333333333)	2025-01-24 12:50:00	Неопределен	BLA	00724	ГУ М4С РОССИИ ПО СТАВРОПОЛЬСКОМУ КРАЮ	\N	0	5	\N	410	arrived	Ростовский	(SHR-00725\n-ZZZZ0600\n-M0000/M0005 /ZONA R0,5 4408N04308E/\n-ZZZZ0700\n-DEP/4408N04308E DEST/4408N04308E DOF/250124 OPR/ГУ М4С РОССИИ ПО\nСТАВРОПОЛЬСКОМУ КРАЮ REG/00724,REG00725 STS/SAR TYP/BLA RMK/WR655 В\nЗОНЕ ВИЗУАЛЬНОГО ПОЛЕТА СОГЛАСОВАНО С ЕСОРВД РОСТОВ ПОЛЕТ БЛА В\nВП-С-М4С МОНИТОРИНГ ПАВОДКООПАСНЫХ У4АСТКОВ РАЗРЕШЕНИЕ 10-37/9425\n15.11.2024 АДМИНИСТРАЦИЯ МИНЕРАЛОВОДСКОГО МУНИЦИПАЛЬНОГО ОКРУГА\nОПЕРАТОР ЛЯХОВСКАЯ +79283000251 ЛЯПИН +79620149012 SID/7772251137)	-TITLE IDEP\n-SID 7772251137\n-ADD 250124\n-ATD 0600\n-ADEP ZZZZ\n-ADEPZ 440846N0430829E\n-PAP 0\n	-TITLE IARR\n-SID 7772251137\n-ADA 250124\n-ATA 1250\n-ADARR ZZZZ\n-ADARRZ 440846N0430829E\n-PAP 0\n	2025-10-01 17:18:46.933362	2025-10-01 17:18:46.933363
8887	7772251311	2025-01-23 00:00:00	\N	(51.86666666666667, 86.0)	2025-01-23 04:02:00	Красноярский край	\N	(51.86666666666667, 86.0)	2025-01-23 09:02:00	Красноярский край	BLA	RF37362	МВД ПО РЕСПУБЛИКЕ АЛТАЙ	\N	0	80	\N	300	arrived	Новосибирский	(SHR-RF37362\n-ZZZZ0400\n-M0000/M0080 /ZONA R002 5152N08600E/\n-ZZZZ1100\n-DEP/5152N08600E DEST/5152N08600E DOF/250123 EET/UNNT0000 OPR/МВД ПО\nРЕСПУБЛИКЕ АЛТАЙ REG/RF37362 TYP/BLA RMK/ПОЛЕТ БВС В СООТВЕТСТВИИ С\nП.В СТ.114 ФП ИВП РЕШЕНИЕ ПРИНЯЛ НА4АЛЬНИК ЦИТСИЗИ МВД ПО РЕСПУБЛИКЕ\nАЛТАЙ ПОДПОЛКОВНИК ВНУТРЕННЕЙ СЛУЖБЫ ОПЕРАТОР БВС ХМЕЛЕВ А.А.\n+79139986050 SID/7772251311)	-TITLE IDEP\n-SID 7772251311\n-ADD 250123\n-ATD 0402\n-ADEP ZZZZ\n-ADEPZ 5152N08600E\n-PAP 0\n-REG RF37362	-TITLE IARR\n-SID 7772251311\n-ADA 250123\n-ATA 0902\n-ADARR ZZZZ\n-ADARRZ 5152N08600E\n-PAP 0\n-REG RF37362	2025-10-01 17:18:46.933363	2025-10-01 17:18:46.933363
8888	7772251691	2025-01-11 00:00:00	\N	(56.766666666666666, 62.03333333333333)	2025-01-11 10:00:00	Свердловская область	\N	(56.766666666666666, 62.03333333333333)	2025-01-11 17:12:00	Свердловская область	AER	RA	МАЕВСКИЙ ИВАН СЕРГЕЕВИ4	\N	0	5	\N	432	arrived	Екатеринбургский	(SHR-0938G\n-ZZZZ1000\n-M0000/M0005 /ZONA 5646N06202E 5646N06203E 5647N06203E 5647N06202E\n5646N06202E/\n-ZZZZ0300\n-DEP/5646N06202E DEST/5646N06202E DOF/250111 EET/USSV0001\nOPR/МАЕВСКИЙ ИВАН СЕРГЕЕВИ4 REG/RA-0938G TYP/AER RMK/РАЗРЕШЕНИЕ\nБОГДАНОВИ4А N-16 ОТ 20.12 2024 . ТО4НЫЕ КООРДИНАТЫ 564630N 0620220E .\nПОДЬЕМЫ АЭРОСТАТА НА ПРИВЯЗИ, НЕ ВЫШЕ 50 МЕТРОВ ОТ САМОЙ ВЫСОКОЙ\nТО4КИ АЭРОСТАТА ОТ ЗЕМЛИ, ПОДБОР ОБЕСПЕ4ИВАЕТСЯ ГРУППОЙ\nСОПРОВОЖДЕНИЯ. МАЕВСКИЙ ИВАН СЕРГЕЕВИ4 +7 902 2 610 610 SID/7772251691)	-TITLE IDEP\n-SID 7772251691\n-ADD 250111\n-ATD 1000	-TITLE IARR\n-SID 7772251691\n-ADA 250111\n-ATA 1712\n-ADARR ZZZZ\n-ADARRZ 5646N06202E\n-PAP 0\n-REG 0938G	2025-10-01 17:18:46.933364	2025-10-01 17:18:46.933364
8889	\N	2024-05-30 00:00:00	\N	\N	\N	Санкт-Петербург	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	scheduled	\N	ZZZZZ	06L0679	BLA	2025-10-01 17:21:40.227378	2025-10-01 17:21:40.22738
8890	\N	2024-05-30 00:00:00	\N	\N	\N	Санкт-Петербург	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	scheduled	\N	ZZZZZ	ZZZZZ	BLA	2025-10-01 17:21:40.22738	2025-10-01 17:21:40.227381
8891	\N	2024-05-30 00:00:00	\N	\N	\N	Санкт-Петербург	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	scheduled	\N	ZZZZZ	001S492	BLA	2025-10-01 17:21:40.227381	2025-10-01 17:21:40.227381
8892	\N	2024-05-30 00:00:00	\N	\N	\N	Санкт-Петербург	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	scheduled	\N	059P070		BLA	2025-10-01 17:21:40.227381	2025-10-01 17:21:40.227382
8893	\N	2024-05-30 00:00:00	\N	\N	\N	Санкт-Петербург	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	scheduled	\N	ZZZZZ	J006767	BLA	2025-10-01 17:21:40.227382	2025-10-01 17:21:40.227382
8894	\N	2024-05-30 00:00:00	\N	\N	\N	Санкт-Петербург	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	scheduled	\N	0316T45	0316T45	BLA	2025-10-01 17:21:40.227382	2025-10-01 17:21:40.227382
8895	\N	2024-05-30 00:00:00	\N	\N	\N	Санкт-Петербург	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	scheduled	\N	ZZZZZ	A001837	BLA	2025-10-01 17:21:40.227383	2025-10-01 17:21:40.227383
8896	7772270360	2024-12-31 00:00:00	\N	(53.06666666666667, 158.3)	\N	Неопределен	\N	(53.06666666666667, 158.3)	\N	Неопределен	BLA	\N	\N	\N	2	5	\N	\N	scheduled	1.0	(SHR-08J7209_x000D_\n-ZZZZ0200_x000D_\n-M0002/M0005 /ZONA MP12085/_x000D_\n-ZZZZ0315_x000D_\n-DEP/5304N15818E DEST/5304N15818E DOF/241231 OPR/ШАХРАЙ ЮРИЙ ИВАНОВИ4_x000D_\nORGN/+79140247906 TYP/BLA RMK/АВИАМОДЕЛЬ. ПОЛЕТЫ 20-50M/MSL_x000D_\n SID/7772270360)_x000D_\n_x000D_\n_x000D_\n_x000D_\n_x000D_\n_x000D_\n_x000D_\n_x000D_\n	(DEP-08J7209-ZZZZ0200-ZZZZ_x000D_\n-DEP/5304N15818E SOSNOWKA DEST/5304N15818E SOSNOWKA DOF/241231 RMK/ _x000D_\nМР12085 ВВЕДЕН _x000D_\nSID/7772270360)_x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D_\nНННН	(ARR-08J7209-ZZZZ0200-ZZZZ0505_x000D_\n-DEP/5304N15818E SOSNOWKA DEST/5304N15818E SOSNOWKA DOF/241231 RMK/ _x000D_\nSID/7772270360)_x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D_\nНННН	2025-10-01 17:21:40.227383	2025-10-01 17:21:40.227383
8897	7772270356	2024-12-30 00:00:00	\N	(53.06666666666667, 158.3)	\N	Неопределен	\N	(53.06666666666667, 158.3)	\N	Неопределен	BLA	\N	\N	\N	2	5	\N	\N	scheduled	2.0	(SHR-08J7209_x000D_\n-ZZZZ0200_x000D_\n-M0002/M0005 /ZONA MP12085/_x000D_\n-ZZZZ0315_x000D_\n-DEP/5304N15818E DEST/5304N15818E DOF/241230 OPR/ШАХРАЙ ЮРИЙ ИВАНОВИ4_x000D_\nORGN/+79140247906 TYP/BLA RMK/АВИАМОДЕЛЬ. ПОЛЕТЫ 20-50M/MSL_x000D_\n SID/7772270356)_x000D_\n_x000D_\n_x000D_\n_x000D_\n_x000D_\n_x000D_\n_x000D_\n_x000D_\n	(DEP-08J7209-ZZZZ0200-ZZZZ_x000D_\n-DEP/5304N15818E SOSNOWKA DEST/5304N15818E SOSNOWKA DOF/241230 _x000D_\nRMK/ВВЕДЕН МР12085 SID/7772270356)_x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D_\nНННН	(ARR-08J7209-ZZZZ0200-ZZZZ0505_x000D_\n-DEP/5304N15818E SOSNOWKA DEST/5304N15818E SOSNOWKA DOF/241230 RMK/ _x000D_\nSID/7772270356)_x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D__x000D_\n_x000D_\nНННН	2025-10-01 17:21:40.227384	2025-10-01 17:21:40.227384
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: geocode_settings; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.geocode_settings (name, setting, unit, category, short_desc) FROM stdin;
\.


--
-- Data for Name: pagc_gaz; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.pagc_gaz (id, seq, word, stdword, token, is_custom) FROM stdin;
\.


--
-- Data for Name: pagc_lex; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.pagc_lex (id, seq, word, stdword, token, is_custom) FROM stdin;
\.


--
-- Data for Name: pagc_rules; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.pagc_rules (id, rule, is_custom) FROM stdin;
\.


--
-- Data for Name: topology; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.topology (id, name, srid, "precision", hasz) FROM stdin;
\.


--
-- Data for Name: layer; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.layer (topology_id, layer_id, schema_name, table_name, feature_column, feature_type, level, child_id) FROM stdin;
\.


--
-- Name: flights_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.flights_id_seq', 20877, true);


--
-- Name: topology_id_seq; Type: SEQUENCE SET; Schema: topology; Owner: postgres
--

SELECT pg_catalog.setval('topology.topology_id_seq', 1, false);


--
-- Name: flights flights_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flights
    ADD CONSTRAINT flights_pkey PRIMARY KEY (id);


--
-- Name: idx_flight_date_region; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_flight_date_region ON public.flights USING btree (flight_date, dep_region);


--
-- Name: idx_flights_arr_point; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_flights_arr_point ON public.flights USING gist (arr_point);


--
-- Name: idx_flights_dep_point; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_flights_dep_point ON public.flights USING gist (dep_point);


--
-- Name: idx_operator; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_operator ON public.flights USING btree (operator);


--
-- Name: ix_flights_arr_region; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_flights_arr_region ON public.flights USING btree (arr_region);


--
-- Name: ix_flights_dep_region; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_flights_dep_region ON public.flights USING btree (dep_region);


--
-- Name: ix_flights_flight_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_flights_flight_date ON public.flights USING btree (flight_date);


--
-- Name: ix_flights_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_flights_id ON public.flights USING btree (id);


--
-- Name: ix_flights_sid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_flights_sid ON public.flights USING btree (sid);


--
-- PostgreSQL database dump complete
--

