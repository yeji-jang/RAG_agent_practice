"""
도메인 비즈니스 전역 예외 처리기 구성
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from shared.core.exceptions import SharedException
from shared.core.logger import get_logger
from shared.core.schemas import APIResponse


logger = get_logger(__name__)


def register_exception_handlers(app : FastAPI) -> None : 

    @app.exception_handler(SharedException)
    async def shared_exception_hadler(request : Request, exc : SharedException) :
        logger.warning(
            "비즈니스 예외 [%s]: %s (path : %s)",
            exc.error_code,
            exc.message,
            request.url.path
        )
        response_dto = APIResponse.fail(
            code=exc.error_code,
            message=exc.message,
            errors=exc.errors
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response_dto.model_dump(mode="json")
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request : Request, exc : RequestValidationError) :
        errors_map : dict[str, list[str]] = {}

        for err in exc.errors() :
            loc = ".".join(str(item) for item in err["loc"] if item != "body")
            errors_map.setdefault(loc or "non_field_errors", []).append(err["msg"])

        response_dto = APIResponse.fail(
            code = "REQUEST_VALIDATION_ERROR",
            message="요청 입력값 검증에 실패했습니다.",
            errors=errors_map,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=response_dto.model_dump(mode="json")
        )

    @app.exception_handler(Exception) 
    async def unhandled_exception_handler(request : Request, exc : Exception) :
        logger.exception("미처리 시스템 오류 발생 (path : %s) : %s", request.url.path, exc)
        response_dto = APIResponse.fail(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다. 관리자에게 문의해주세요."
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_dto.model_dump(mode="json")
        )