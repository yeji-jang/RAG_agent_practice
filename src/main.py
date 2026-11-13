"""
fastAPI 수명주기(lifespan) 및 라우터 관리 엔트리포인트
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from shared.core.config import settings
from shared.core.exception_handlers import register_exception_handlers
from shared.core.logger import get_logger
from shared.core.vector_store import get_vector_store

logger = get_logger("app.main")

def _prepare_sample_data() -> None:
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    (data_dir / "hr_policy.txt").write_text(
        "제1조(연차휴가) 입사 1년 미만 근로자는 1개월 개근 시 1일의 유급휴가가 발생한다.\n\n"
        "제2조(재택근무) 주 2회까지 팀장 승인 하에 원격 근무를 신청할 수 있으며, 코어타임은 10:00~16:00이다.",
        encoding="utf-8",
    )
    (data_dir / "security_guide.txt").write_text(
        "제10조(VPN 접속) 외부 네트워크에서 사내 Git 저장소 접근 시 반드시 사내 VPN(오류코드 E-401 발생 시 인증서 재발급)을 사용해야 한다.\n\n"
        "제11조(API 키 관리) 소스 코드 내에 OPENAI_API_KEY 등 비밀키를 하드코딩하는 행위는 엄격히 금지된다.",
        encoding="utf-8",
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("애플리케이션 시작: 샘플 데이터 생성 및 PGVector 컬렉션 초기화 중...")
    _prepare_sample_data()
    get_vector_store(settings.CHATBOT_COLLECTION)
    get_vector_store(settings.RECOMMEND_COLLECTION)
    logger.info("애플리케이션 준비 완료.")
    yield
    logger.info("애플리케이션 종료.")

app = FastAPI(
    title="엔터프라이즈 RAG 통합 실습 API",
    description="1) 사내 규정 챗봇 / 2) 네이버 쇼핑 하이브리드 추천 / 3) RAGAS 평가 시스템",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)