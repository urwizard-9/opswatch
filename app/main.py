"""OpsWatch FastAPI 애플리케이션 진입점."""

from fastapi import FastAPI

from app.core.config import settings
from app.database import Base, engine
from app.schemas import HealthResponse

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 인스턴스 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="배포 서버 통신 상태 모니터링 및 장애 이력관리 시스템",
)


@app.get("/health", response_model=HealthResponse, tags=["Operation"])
def health_check():
    """OpsWatch 앱 자체 상태 확인.

    GitHub Actions smoke test 및 Render 배포 확인용.
    """
    return HealthResponse(
        status="ok",
        service=settings.APP_NAME.lower(),
        version=settings.APP_VERSION,
    )
