# 전역 로거 포맷과 로그 레벨 설정
import os
import logging
from dotenv import load_dotenv

load_dotenv()

log_mode = os.getenv("LOGGING_MODE", "info").lower()
log_level = logging.DEBUG if log_mode == "debug" else logging.INFO


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=log_level,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    force=True,  # 다른 라이브러리(uvicorn 등)가 먼저 로깅 설정을 했더라도 덮어써서 이 설정을 적용
)

def get_logger(name : str | None = None) -> logging.Logger:
    logger_name = name or os.getenv("LOGGER_NAME", "rag-api")
    return logging.getLogger(logger_name)

logger = get_logger()