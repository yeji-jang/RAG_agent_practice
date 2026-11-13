# ── 파이썬 표준 라이브러리 ──────────────────────────────
# Protocol: "이런 메서드를 가진 객체"라는 규칙(인터페이스)을 정의할 때 사용 (→ DBConnection)
# Any: 어떤 타입이든 허용한다는 타입 힌트
from typing import Protocol, Any

# ── PostgreSQL 드라이버 ────────────────────────────────
# 파이썬에서 PostgreSQL에 직접 접속해 SQL을 실행하는 라이브러리 (→ get_raw_db_connection)
import psycopg

# ── LangChain: 모델 생성 ────────────────────────────────
# 모델 이름 + 제공자(openai, anthropic 등)만 주면 알맞은 채팅 모델 객체를 만들어 주는 팩토리 함수 (→ get_llm)
from langchain.chat_models import init_chat_model

# ── LangChain: 추상 인터페이스(공통 타입) ───────────────
# 반환 타입을 특정 회사 클래스 대신 공통 타입으로 지정해서, 나중에 모델/DB를 바꿔도 호출부 코드는 그대로 쓰게 함
from langchain_core.embeddings import Embeddings              # 모든 임베딩 모델의 공통 부모 타입
from langchain_core.language_models import BaseChatModel      # 모든 채팅 모델(LLM)의 공통 부모 타입
from langchain_core.vectorstores import VectorStore           # 모든 벡터 DB의 공통 부모 타입

# ── LangChain: 실제 구현체 ─────────────────────────────
# OpenAI 임베딩 API로 문장을 벡터(숫자 배열)로 바꿔 주는 클래스 (→ get_embeddings)
from langchain_openai import OpenAIEmbeddings
# PostgreSQL + pgvector를 벡터 저장소로 쓰게 해 주는 클래스 (→ get_vector_store)
from langchain_postgres import PGVector
# 벡터 간 거리 계산 방식 선택용 (COSINE, EUCLIDEAN 등)
from langchain_postgres.vectorstores import DistanceStrategy

# ── 프로젝트 내부 모듈 ────────────────────────────
from shared.core.config import settings       # .env 기반 설정값 (모델명, DB 주소, API 키 등)
from shared.core.logger import get_logger     # 공통 로거 생성 함수


logger = get_logger(__name__)


"""
[ETL 작업 순서]
질문 ──▶ [get_embeddings] 질문을 벡터로 변환
           ▼
         [get_vector_store] rag_db에서 비슷한 문서 검색
           ▼
         [get_llm] 문서 + 질문으로 답변 생성 ──▶ 답변

         [get_raw_db_connection] SQL 직접 실행 (BM25, 중복 체크용)
"""


# 1. 답변을 만드는 AI
def get_llm() -> BaseChatModel : 
    """
    설정된 provider에 맞는 채팅 모델 인스턴스를 추상 타입으로 반환
    """
    return init_chat_model(
        model=settings.LLM_MODEL,
        model_provider=settings.LLM_PROVIDER,
        api_key=settings.API_KEY,
        reasoning_effort=settings.REASONING_EFFORT,
    )


# 2. 문장을 숫자로 바꾸는 번역기
def get_embeddings() -> Embeddings : 
    """
    임베딩 모델 인스턴스를 공통 Embeddings 인터페이스로 반환 
    """
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.API_KEY
    )


# 3. 벡터 창고
def get_vector_store(collection_name : str) -> VectorStore :
    """
    지정된 컬렉션 이름의 벡터 스토어를 공통 VectorStore 인터페이스로 반환
    """
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=collection_name,
        connection=settings.DATABASE_URL,
        distance_strategy=DistanceStrategy.COSINE,
        use_jsonb=True, 
    )


# 4. DB 직통 연결
class DBConnection(Protocol) :
    def cursor(self) -> Any : ...
    def commit(self) -> None : ...
    def rollback(self) -> None : ...
    def close(self) -> None : ...

def get_raw_db_connection() -> DBConnection :
    """
    증분 해시 조회 및 BM25 코퍼스 로드를 위한  DB 커넥션을 반환
    """
    raw_dsn = settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
    return psycopg.connect(raw_dsn)