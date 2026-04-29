"""OpsWatch 장애 이력 API 라우터."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Incident, Server
from app.schemas import IncidentResolveRequest, IncidentResponse
from app.services.incident_service import resolve_incident

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=list[IncidentResponse])
def list_incidents(
    status: str | None = Query(default=None, description="OPEN 또는 RESOLVED"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """장애 이력을 조회합니다. status 파라미터로 필터링 가능."""
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == status.upper())

    records = query.order_by(Incident.created_at.desc()).limit(limit).all()

    # server_name 추가
    result = []
    for r in records:
        server = db.query(Server).filter(Server.id == r.server_id).first()
        result.append(
            IncidentResponse(
                id=r.id,
                server_id=r.server_id,
                server_name=server.name if server else None,
                status=r.status,
                reason=r.reason,
                action_taken=r.action_taken,
                github_issue_url=r.github_issue_url,
                created_at=r.created_at,
                resolved_at=r.resolved_at,
            )
        )
    return result


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """특정 장애 이력의 상세 정보를 조회합니다."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="장애 이력을 찾을 수 없습니다")

    server = db.query(Server).filter(Server.id == incident.server_id).first()
    return IncidentResponse(
        id=incident.id,
        server_id=incident.server_id,
        server_name=server.name if server else None,
        status=incident.status,
        reason=incident.reason,
        action_taken=incident.action_taken,
        github_issue_url=incident.github_issue_url,
        created_at=incident.created_at,
        resolved_at=incident.resolved_at,
    )


@router.put("/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident_endpoint(
    incident_id: int,
    body: IncidentResolveRequest,
    db: Session = Depends(get_db),
):
    """장애를 해결 처리합니다. 원인과 조치 내용을 기록합니다."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="장애 이력을 찾을 수 없습니다")

    if incident.status == "RESOLVED":
        raise HTTPException(status_code=400, detail="이미 해결된 장애입니다")

    resolved = resolve_incident(db, incident, body.reason, body.action_taken)

    server = db.query(Server).filter(Server.id == resolved.server_id).first()
    return IncidentResponse(
        id=resolved.id,
        server_id=resolved.server_id,
        server_name=server.name if server else None,
        status=resolved.status,
        reason=resolved.reason,
        action_taken=resolved.action_taken,
        github_issue_url=resolved.github_issue_url,
        created_at=resolved.created_at,
        resolved_at=resolved.resolved_at,
    )
