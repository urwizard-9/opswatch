# 🔍 OpsWatch

**배포 서버 통신 상태 모니터링 및 장애 이력관리 DevOps 시스템**

> 여러 서버/API의 통신 상태를 점검하여 UP/SLOW/DOWN을 판별하고,
> 점검 이력·장애 이력·로그·메트릭을 관리하는 FastAPI 기반 운영 모니터링 시스템

---

## 📋 프로젝트 개요

| 항목 | 내용 |
|---|---|
| **프로젝트** | 인공지능파이프라인 중간프로젝트 (26-1) |
| **기술 스택** | Python 3.13 / FastAPI / SQLAlchemy / Prometheus / Grafana |
| **배포** | Docker / Render |
| **CI/CD** | GitHub Actions (ruff + pytest + Docker smoke test) |
| **테스트** | pytest 30개, 커버리지 86% |

---

## 🏗️ DevOps 파이프라인

```
코드 작성 (feature/* 브랜치)
    ↓
Git Push → GitHub Actions CI
    ├─ ruff 코드 품질 검사
    ├─ pytest (30개 테스트, 커버리지 70%+ 검증)
    └─ Docker 빌드 + Smoke Test (/health 200 확인)
    ↓
Render 자동 배포 (main 브랜치)
    ↓
FastAPI 서비스 운영
    ├─ 60초 백그라운드 스케줄러 → 전체 서버 자동 점검
    ├─ DOWN 감지 → Incident 자동 생성 (중복 방지)
    ├─ 구조화된 로그 (이벤트 기반)
    └─ GET /metrics → Prometheus 메트릭 노출
         ↓
docker-compose up -d (로컬 모니터링)
    ├─ Prometheus (15초 스크레이프)
    └─ Grafana 대시보드 (6개 패널)
```

---

## 🚀 빠른 시작

### 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000

# API 문서 확인
# http://localhost:8000/docs
```

### Docker Compose (모니터링 스택 포함)

```bash
docker-compose up -d --build
```

| 서비스 | URL |
|---|---|
| OpsWatch API | http://localhost:8000 |
| Swagger 문서 | http://localhost:8000/docs |
| Prometheus | http://localhost:19090 |
| Grafana | http://localhost:13000 (admin / opswatch123) |

### 테스트

```bash
# 전체 테스트 + 커버리지
pytest tests/ --cov=app --cov-report=term-missing

# ruff 린트 검사
ruff check app/ tests/
```

---

## 📡 API 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| `GET` | `/health` | 앱 상태 확인 |
| `POST` | `/servers` | 서버 등록 |
| `GET` | `/servers` | 서버 목록 조회 |
| `GET` | `/servers/{id}` | 서버 상세 조회 |
| `PUT` | `/servers/{id}` | 서버 정보 수정 |
| `DELETE` | `/servers/{id}` | 서버 삭제 |
| `POST` | `/checks/run/{id}` | 개별 서버 점검 |
| `POST` | `/checks/run` | 전체 서버 점검 |
| `GET` | `/checks/history/{id}` | 점검 이력 조회 |
| `GET` | `/incidents` | 장애 이력 조회 |
| `GET` | `/incidents/{id}` | 장애 상세 조회 |
| `PUT` | `/incidents/{id}/resolve` | 장애 해결 처리 |
| `GET` | `/metrics` | Prometheus 메트릭 |
| `GET` | `/mock/normal` | Mock: 정상 응답 (200) |
| `GET` | `/mock/slow` | Mock: 지연 응답 (3초) |
| `GET` | `/mock/error` | Mock: 에러 응답 (500) |
| `GET` | `/mock/random` | Mock: 랜덤 응답 |
| `GET` | `/mock/crash` | Mock: 의도적 예외 |

---

## 📊 Prometheus 메트릭

| 메트릭 | 타입 | 설명 |
|---|---|---|
| `opswatch_checks_total` | Counter | 총 점검 횟수 (status 라벨) |
| `opswatch_servers_up` | Gauge | 현재 UP 서버 수 |
| `opswatch_servers_slow` | Gauge | 현재 SLOW 서버 수 |
| `opswatch_servers_down` | Gauge | 현재 DOWN 서버 수 |
| `opswatch_incidents_open` | Gauge | 현재 OPEN Incident 수 |
| `opswatch_response_time_ms` | Histogram | 응답 시간 분포 |

---

## 📁 프로젝트 구조

```
opswatch/
├── app/
│   ├── main.py                  # FastAPI 진입점 + lifespan
│   ├── database.py              # SQLAlchemy 설정
│   ├── models.py                # ORM 모델
│   ├── schemas.py               # Pydantic 스키마
│   ├── core/
│   │   ├── config.py            # 환경변수 설정
│   │   └── logging_config.py    # 구조화된 로깅
│   ├── routers/
│   │   ├── servers.py           # Server CRUD
│   │   ├── checks.py            # 상태 점검
│   │   ├── incidents.py         # 장애 이력
│   │   ├── metrics.py           # Prometheus /metrics
│   │   └── mock_targets.py      # Mock 대상 서버
│   └── services/
│       ├── monitor_service.py   # httpx 상태 판별
│       ├── incident_service.py  # Incident 자동 생성
│       └── scheduler.py         # 백그라운드 스케줄러
├── tests/                       # pytest 30개
├── prometheus/                  # Prometheus 설정
├── grafana/                     # Grafana 프로비저닝
├── .github/workflows/           # CI/CD 워크플로우
├── Dockerfile                   # 멀티스테이지 빌드
├── docker-compose.yml           # 3서비스 스택
├── render.yaml                  # Render 배포 설정
├── pyproject.toml               # ruff/pytest 설정
└── requirements.txt             # 의존성
```

---

## 📝 커밋 메시지 규칙

```
<type>: <설명>
```

| Type | 의미 | 예시 |
|---|---|---|
| `feat` | 새로운 기능 추가 | `feat: 서버 등록 API 구현` |
| `fix` | 버그 수정 | `fix: slow 응답 판별 기준 수정` |
| `test` | 테스트 추가/수정 | `test: 서버 등록 API 테스트 추가` |
| `ci` | CI/CD 설정 변경 | `ci: GitHub Actions 워크플로우 추가` |
| `chore` | 빌드, 도구, 설정 변경 | `chore: Dockerfile 추가` |
| `docs` | 문서 작성/수정 | `docs: README 작성` |
| `refactor` | 기능 변경 없는 구조 개선 | `refactor: 상태 점검 로직 분리` |
| `style` | 코드 스타일 변경 | `style: ruff 린트 경고 수정` |

---

## 📜 라이선스

MIT License
