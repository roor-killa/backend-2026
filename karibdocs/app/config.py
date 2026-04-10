from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    LLM_PROVIDER: str = "ollama"
    LLM_TEMPERATURE: float = 0.1

    MISTRAL_API_KEY: str = ""
    MISTRAL_MODEL: str = "mistral-small-latest"
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"
    OLLAMA_MODEL: str = "llama3.1"

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/drive/oauth/callback"

    UPLOAD_DIR: str = "./uploads"
    CHROMA_DIR: str = "./chroma_db"
    MAX_FILE_SIZE_MB: int = 50

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RAG_K_RESULTS: int = 4
    EMBEDDING_PROVIDER: str = "huggingface"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    class Config:
        env_file = ".env"

settings = Settings()