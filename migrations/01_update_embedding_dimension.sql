-- database/migrations/01_update_embedding_dimension.sql
-- Remove old embedding column (which was created as VECTOR(768))
ALTER TABLE knowledge_chunks DROP COLUMN IF EXISTS embedding;

-- Create new embedding column for all-MiniLM-L6-v2 (which generates 384-dimensional vectors)
ALTER TABLE knowledge_chunks ADD COLUMN embedding vector(384);
