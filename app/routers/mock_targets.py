"""OpsWatch Mock Target API 라우터.

시연용 mock 엔드포인트를 제공합니다.
실제 외부 서버 대신 이 엔드포인트들을 점검 대상으로 등록하여 테스트할 수 있습니다.
"""

import asyncio
import random

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/mock", tags=["Mock Targets"])


@router.get("/normal")
async def mock_normal():
    """정상 서버 시뮬레이션. 즉시 200 OK를 반환합니다."""
    return {"status": "ok", "message": "normal server is running"}


@router.get("/slow")
async def mock_slow():
    """지연 서버 시뮬레이션. 3초 대기 후 200 OK를 반환합니다."""
    await asyncio.sleep(3)
    return {"status": "slow", "message": "slow response simulated"}


@router.get("/error")
async def mock_error():
    """장애 서버 시뮬레이션. 500 Internal Server Error를 반환합니다."""
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "server error simulated"},
    )


@router.get("/random")
async def mock_random():
    """불안정 서버 시뮬레이션. 랜덤하게 200 또는 500을 반환합니다."""
    if random.choice([True, False]):
        return {"status": "ok", "message": "random status generated"}
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "random status generated"},
    )
