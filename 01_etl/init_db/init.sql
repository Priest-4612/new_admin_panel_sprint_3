\c test_movies_database

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE SCHEMA IF NOT EXISTS "content";
ALTER ROLE app SET search_path TO "content", "public";
