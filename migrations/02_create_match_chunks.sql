-- database/migrations/02_create_match_chunks.sql
create or replace function match_chunks (
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
returns table (
  chunk_id text,
  topic text,
  subtopic text,
  content text,
  similarity_score float
)
language sql stable
as $$
  select
    knowledge_chunks.chunk_id,
    knowledge_chunks.topic,
    knowledge_chunks.subtopic,
    knowledge_chunks.content,
    1 - (knowledge_chunks.embedding <=> query_embedding) as similarity_score
  from knowledge_chunks
  where 1 - (knowledge_chunks.embedding <=> query_embedding) > match_threshold
  order by similarity_score desc
  limit match_count;
$$;
