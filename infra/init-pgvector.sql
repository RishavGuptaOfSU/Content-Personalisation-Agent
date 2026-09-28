-- Runs once, on first initialisation of the postgres volume.
-- The pgvector/pgvector image ships the extension; this enables it in the
-- application database so Alembic can create the vector column.
CREATE EXTENSION IF NOT EXISTS vector;
