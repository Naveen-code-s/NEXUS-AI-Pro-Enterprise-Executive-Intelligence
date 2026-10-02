from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name:str="NEXUS AI"; app_version:str="0.9.0-pro"; groq_api_key:str=""
    llm_model:str="llama-3.3-70b-versatile"; embedding_model:str="sentence-transformers/all-MiniLM-L6-v2"
    database_url:str="sqlite:///data/nexus.db"; faiss_path:str="data/vector_store"; upload_dir:str="data/uploads"; report_dir:str="data/reports"
    top_k:int=6; chunk_size:int=900; chunk_overlap:int=120; log_level:str="INFO"
    semantic_scholar_api_url:str="https://api.semanticscholar.org/graph/v1/paper/search"
    openalex_api_url:str="https://api.openalex.org/works"; crossref_api_url:str="https://api.crossref.org/works"
    model_config=SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)
@lru_cache
def get_settings(): return Settings()
