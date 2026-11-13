# 전역에서 참조할 LLM 모델 및 임베딩 설정, PGVector 접속 정보 관리

import os
from dotenv import load_dotenv

load_dotenv()

class Settings : 
    # LLM 모델 설정
    API_KEY : str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL : str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    LLM_PROVIDER : str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL : str = os.getenv("LLM_MODEL", "gpt-6-luna")
    REASONING_EFFORT : str = os.getenv("REASONING_EFFORT", "low")

    # PostgreSQL (PGVector) 접속 정보
    DATABASE_URL : str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/rag_db"
    )

    # 도메인별 컬렉션 분리
    CHATBOT_COLLECTION : str = os.getenv("CHATBOT_COLLECTION", "company_policies")
    RECOMMEND_COLLECTION : str = os.getenv("RECOMMEND_COLLECTION", "product_catalog")


settings = Settings()