from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/willow")

    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ROOT_USER: str = os.getenv("MINIO_ROOT_USER", "minioadmin")
    MINIO_ROOT_PASSWORD: str = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "plant-images")

    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
    OPENAI_EMBEDDING_API_KEY: str = os.getenv("OPENAI_EMBEDDING_API_KEY", os.getenv("OPENAI_API_KEY", "your-openai-embedding-api-key"))

    # Pinecone settings
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "your-pinecone-api-key")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "plant-diseases")

    class Config:
        env_file = ".env"

settings = Settings()
