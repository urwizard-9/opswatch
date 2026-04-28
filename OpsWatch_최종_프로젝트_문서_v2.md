# OpsWatch 최종 프로젝트 문서 v2

## 프로젝트명

**OpsWatch: 배포 서버 통신 상태 모니터링 및 장애 이력관리 DevOps 시스템**


---

## v2 업데이트 반영 내용

이 문서는 기존 OpsWatch 최종 프로젝트 문서에 **로깅 수업 내용**을 반영한 업데이트 버전이다. 프로젝트 주제 자체는 유지하되, `로그 기반 운영`, `예외 traceback 기록`, `장애 대응 자동화`, `GitHub Issue 연동`을 강화한다.

추가·강화된 내용은 다음과 같다.

```text
1. 로깅 요구사항 강화
2. 로그 레벨 기준 구체화
3. 좋은 로그 포맷 적용
4. logger.exception 기반 예외 traceback 기록
5. 장애 발생 시 GitHub Issue 자동 생성 선택 기능 추가
6. GH_REPO, GH_TOKEN, ENABLE_GITHUB_ISSUE 환경변수 추가
7. Issue 기반 장애 대응 흐름 추가
8. fix 브랜치 → 코드 수정 → 테스트 → GitHub Actions → Render 재배포 → Incident 해결 처리 흐름 추가
```

즉, v2에서는 단순히 “로그를 남긴다”가 아니라, **운영 중 발생한 장애를 로그로 추적하고, 필요하면 GitHub Issue로 연결하여 개발 이력과 장애 대응 이력을 함께 관리하는 DevOps 흐름**을 보여주는 것을 목표로 한다.

---

## 0. 문서 목적

이 문서는 DevOps 중간 프로젝트를 수행하기 위한 최종 기획서이자 구현 지시서이다.

추후 Claude Code, Codex, Gemini CLI, Cursor, Antigravity 등의 코드 생성 모델에게 전달하여 실제 프로젝트를 구현할 때 기준 문서로 사용한다.

이 프로젝트의 핵심은 단순히 FastAPI 웹 서비스를 만드는 것이 아니다.  
수업에서 배운 DevOps 흐름을 자체 SW에 적용하여 다음을 증명하는 것이다.

```text
코드 작성
→ Git/GitHub 버전 관리
→ 테스트 자동화
→ GitHub Actions 기반 CI
→ Docker 패키징
→ Render 배포
→ 로그 기반 운영
→ 장애 로그 분석 및 traceback 추적
→ 선택적 GitHub Issue 자동 생성
→ Prometheus/Grafana 기반 모니터링
→ 장애 발생 및 대응 이력 관리
```

따라서 구현 과정에서 기능 자체의 화려함보다 다음 항목을 우선한다.

```text
1. 실제 동작하는 SW인가?
2. 구조가 정리되어 있는가?
3. 테스트가 자동화되어 있는가?
4. GitHub Actions로 품질 검증이 자동 수행되는가?
5. Docker로 실행 환경이 고정되어 있는가?
6. Render에 배포 가능한가?
7. 로그와 장애 이력으로 운영 증거를 제시할 수 있는가?
8. Prometheus/Grafana로 모니터링 확장성을 보여줄 수 있는가?
9. README와 보고서로 개발·운영 과정을 설명할 수 있는가?
```

---

## 1. 프로젝트 최종 주제

## OpsWatch: 배포 서버 통신 상태 모니터링 및 장애 이력관리 DevOps 시스템

### 1.1 한 줄 설명

여러 서버/API를 운영 중인 상황을 가정하고, 각 서버의 통신 상태를 점검하여 `UP`, `SLOW`, `DOWN` 상태를 판별하고, 점검 이력·장애 이력·로그·메트릭을 관리하는 FastAPI 기반 운영 모니터링 시스템을 구축한다.

### 1.2 프로젝트 컨셉

나는 여러 개의 백엔드 서버/API를 운영하고 있다고 가정한다.

예를 들어 다음과 같은 서버들이 있다고 본다.

```text
greennode-api
auth-server
image-server
ai-inference-server
database-health-api
```

운영자는 각 서버가 살아 있는지, 응답이 느려졌는지, 장애가 발생했는지 확인해야 한다.

OpsWatch는 각 서버의 URL을 등록하고, HTTP 요청을 보내 다음 정보를 수집한다.

```text
1. HTTP 응답 코드
2. 응답 시간
3. 통신 성공 여부
4. Timeout 여부
5. 장애 발생 여부
```

이후 수집된 결과를 바탕으로 서버 상태를 다음 세 가지로 분류한다.

```text
UP    : 정상
SLOW  : 응답 지연
DOWN  : 장애
```

장애가 발생하면 장애 이력 Incident를 자동 생성하고, 운영자는 장애 원인과 조치 내용을 기록한 뒤 해결 처리할 수 있다.

---

## 2. 프로젝트 배경

DevOps 수업은 단순한 SW 개발 수업이 아니라, 운영 가능한 SW를 만드는 과정을 다룬다.

수업의 주요 흐름은 다음과 같다.

```text
1. Git/GitHub 기반 버전 관리
2. 브랜치 기반 개발
3. 테스트 자동화
4. GitHub Actions 기반 CI
5. Docker 패키징
6. Render 배포
7. 로그 기반 운영
8. 모니터링 및 장애 대응
```

따라서 이 프로젝트는 단순 계산기, TODO 앱, CRUD 게시판보다 DevOps의 운영 관점을 더 잘 보여줄 수 있는 주제를 선택한다.

서버 상태 점검 및 장애 이력관리는 DevOps에서 중요한 `Operate`, `Monitor` 단계와 직접 연결된다.

---

## 3. 프로젝트 목표

### 3.1 SW 기능 목표

OpsWatch는 다음 기능을 제공해야 한다.

```text
1. 점검 대상 서버 등록
2. 등록된 서버 목록 조회
3. 서버 정보 수정
4. 서버 삭제
5. 개별 서버 상태 점검
6. 전체 서버 상태 점검
7. HTTP 응답 코드 및 응답 시간 측정
8. UP/SLOW/DOWN 상태 판별
9. 점검 결과 이력 저장
10. 장애 발생 시 Incident 자동 생성
11. 장애 이력 조회
12. 장애 상세 조회
13. 장애 해결 처리
14. 장애 원인 및 조치 내용 기록
15. 운영 로그 기록
16. 서비스 자체 상태 확인용 /health 제공
17. Prometheus 수집용 /metrics 제공
18. Mock 서버 엔드포인트 제공
19. Swagger UI를 통한 API 확인
20. 선택적으로 GitHub Issue 자동 생성
21. 선택적으로 간단한 HTML 대시보드 제공
```

### 3.2 DevOps 목표

프로젝트는 다음 DevOps 요소를 포함해야 한다.

```text
1. Git/GitHub 저장소 관리
2. 의미 있는 커밋 메시지 작성
3. 기능 단위 브랜치 사용
4. Pull Request 또는 브랜치 병합 이력 관리
5. pytest 기반 테스트 자동화
6. pytest-cov 기반 테스트 커버리지 측정
7. ruff 기반 코드 품질 검사
8. GitHub Actions 기반 CI 자동화
9. Dockerfile 작성
10. GitHub Actions에서 Docker 이미지 빌드 검증
11. 컨테이너 실행 후 /health smoke test
12. 컨테이너 실행 후 /metrics smoke test
13. Docker Compose 기반 로컬 운영 환경 구성
14. Prometheus 메트릭 수집
15. Grafana 대시보드 구성
16. Render 배포
17. Render 로그 확인
18. 장애 발생/복구 시나리오 캡처
19. README 및 보고서 작성
```

---

## 4. 평가 기준 대응 전략

### 4.1 SW 기본 구현 및 난이도

단순 계산기가 아니라 운영 모니터링 시스템을 구현한다.

구현 기능은 다음과 같이 구성한다.

```text
서버 등록
서버 상태 점검
점검 이력 저장
장애 이력 자동 생성
장애 해결 처리
로그 기록
메트릭 제공
```

따라서 단순 CRUD가 아니라 실제 운영 상황을 반영한 기능을 가진다.

### 4.2 DevOps 파이프라인 완성도

다음 흐름을 모두 보여준다.

```text
Git/GitHub
→ pytest
→ GitHub Actions
→ Docker
→ Render
→ Logging
→ Prometheus
→ Grafana
```

### 4.3 운영 및 관찰 가능성

다음 운영 증거를 제시한다.

```text
1. Render 배포 URL
2. Render 로그 화면
3. Swagger UI 화면
4. 장애 발생 로그
5. 장애 이력 DB 조회 결과
6. GitHub Actions 성공 화면
7. Docker build 성공 화면
8. Docker Compose 실행 화면
9. Prometheus target UP 화면
10. Grafana 대시보드 화면
11. 장애 해결 처리 화면
```

### 4.4 설명력 및 문서화

다음 문서를 작성한다.

```text
1. README.md
2. API 사용법
3. 실행 방법
4. 테스트 방법
5. Docker 실행 방법
6. Prometheus/Grafana 실행 방법
7. Render 배포 방법
8. 장애 시나리오
9. GitHub Actions 설명
10. 최종 보고서
```

---

## 5. 전체 시스템 구조

### 5.1 논리 구조

```text
[운영자]
   ↓
[OpsWatch FastAPI Application]
   ├── 서버 관리 API
   ├── 상태 점검 API
   ├── 점검 이력 API
   ├── 장애 이력 API
   ├── Mock Target API
   ├── /health
   └── /metrics
   ↓
[Database]
   ├── servers
   ├── check_results
   └── incidents
   ↓
[Logging]
   ├── INFO
   ├── WARNING
   └── ERROR
   ↓
[Prometheus]
   ↓
[Grafana Dashboard]
```

### 5.2 배포/운영 구조

```text
[GitHub Repository]
   ↓ push / pull_request
[GitHub Actions]
   ├── lint
   ├── test
   ├── coverage
   ├── docker build
   ├── docker smoke test
   └── optional security scan
   ↓
[Docker Image Build]
   ↓
[Render Deployment]
   ↓
[OpsWatch Public API]
   ├── /health
   ├── /metrics
   ├── /servers
   ├── /checks
   └── /incidents
```

### 5.3 Prometheus/Grafana 운영 구조

```text
[Docker Compose Local Environment]
   ├── opswatch-api
   ├── prometheus
   └── grafana

opswatch-api
   └── /metrics

prometheus
   └── scrape opswatch-api:8000/metrics

grafana
   └── visualize prometheus data
```

### 5.4 중요한 배포 전략

FastAPI 앱은 Render에 최종 배포한다.

Prometheus/Grafana는 Docker Compose 기반 로컬 운영 환경으로 구성한다.

즉, 최종 제출에서는 다음 두 가지를 모두 보여준다.

```text
1. Render에 배포된 FastAPI 운영 서비스
2. Docker Compose로 실행한 Prometheus/Grafana 모니터링 환경
```

Prometheus/Grafana까지 Render에 반드시 배포할 필요는 없다.  
오히려 Render에는 핵심 API 서버를 안정적으로 배포하고, Prometheus/Grafana는 로컬 운영 관찰 환경으로 구성하는 것이 현실적이다.

---

## 6. 상태 판별 기준

### 6.1 기본 기준

서버 상태는 다음 기준으로 판별한다.

| 조건 | 상태 | 설명 |
|---|---|---|
| HTTP 2xx + 응답 시간 2초 이하 | UP | 정상 |
| HTTP 2xx + 응답 시간 2초 초과 | SLOW | 응답 지연 |
| HTTP 4xx | DOWN | 클라이언트 요청 또는 접근 문제 |
| HTTP 5xx | DOWN | 서버 내부 오류 |
| Timeout | DOWN | 응답 없음 |
| Connection Error | DOWN | 연결 실패 |
| Invalid URL | DOWN | 잘못된 URL |

### 6.2 기본 timeout

```text
timeout = 5 seconds
```

### 6.3 slow threshold

```text
slow_threshold = 2 seconds
```

이 값은 설정 파일 또는 환경 변수에서 수정 가능하도록 한다.

---

## 7. 주요 기능 상세 요구사항

### 7.1 서버 등록 기능

#### 목적

운영자가 점검할 서버/API를 등록한다.

#### API

```http
POST /servers
```

#### 요청 예시

```json
{
  "name": "normal-server",
  "url": "http://localhost:8000/mock/normal",
  "description": "정상 응답 서버",
  "importance": "HIGH"
}
```

#### 응답 예시

```json
{
  "id": 1,
  "name": "normal-server",
  "url": "http://localhost:8000/mock/normal",
  "description": "정상 응답 서버",
  "importance": "HIGH",
  "is_active": true,
  "created_at": "2026-04-28T10:00:00"
}
```

#### 검증 규칙

```text
1. name은 비어 있으면 안 된다.
2. url은 비어 있으면 안 된다.
3. url은 http:// 또는 https://로 시작해야 한다.
4. importance는 LOW, MEDIUM, HIGH 중 하나이다.
5. 같은 name 중복 등록은 가능하면 막는다.
```

---

### 7.2 서버 목록 조회 기능

#### API

```http
GET /servers
```

#### 응답 예시

```json
[
  {
    "id": 1,
    "name": "normal-server",
    "url": "http://localhost:8000/mock/normal",
    "importance": "HIGH",
    "is_active": true
  }
]
```

---

### 7.3 서버 상세 조회 기능

#### API

```http
GET /servers/{server_id}
```

---

### 7.4 서버 수정 기능

#### API

```http
PUT /servers/{server_id}
```

#### 수정 가능 항목

```text
name
url
description
importance
is_active
```

---

### 7.5 서버 삭제 기능

#### API

```http
DELETE /servers/{server_id}
```

삭제 방식은 실제 DB 삭제 또는 soft delete 중 선택 가능하다.  
간단한 구현을 위해 실제 삭제를 사용해도 된다.

---

### 7.6 개별 서버 상태 점검 기능

#### 목적

특정 서버에 HTTP GET 요청을 보내 통신 상태를 판별한다.

#### API

```http
POST /checks/{server_id}
```

#### 동작 순서

```text
1. server_id로 서버 정보를 조회한다.
2. 서버 URL로 HTTP GET 요청을 보낸다.
3. 응답 시간을 측정한다.
4. 응답 코드와 응답 시간을 기준으로 상태를 판별한다.
5. CheckResult 테이블에 결과를 저장한다.
6. 상태가 DOWN이면 Incident를 자동 생성한다.
7. 로그를 기록한다.
8. 메트릭 값을 업데이트한다.
9. 결과를 반환한다.
```

#### 응답 예시

```json
{
  "server_id": 1,
  "server_name": "normal-server",
  "status": "UP",
  "status_code": 200,
  "response_time_ms": 120,
  "message": "Server is healthy",
  "checked_at": "2026-04-28T10:01:00"
}
```

---

### 7.7 전체 서버 상태 점검 기능

#### API

```http
POST /checks/run-all
```

#### 설명

등록된 active 서버 전체에 대해 상태 점검을 수행한다.

#### 응답 예시

```json
{
  "total": 4,
  "up": 1,
  "slow": 1,
  "down": 2,
  "results": [
    {
      "server_name": "normal-server",
      "status": "UP",
      "response_time_ms": 120
    },
    {
      "server_name": "slow-server",
      "status": "SLOW",
      "response_time_ms": 3010
    }
  ]
}
```

---

### 7.8 점검 이력 조회 기능

#### API

```http
GET /checks
GET /checks?server_id=1
GET /checks?status=DOWN
```

#### 설명

과거 점검 결과를 조회한다.

#### 조회 조건

```text
server_id
status
limit
offset
```

---

### 7.9 장애 이력 자동 생성 기능

#### 목적

서버 상태가 DOWN으로 판별되면 Incident를 자동 생성한다.

#### 생성 조건

```text
1. 점검 결과가 DOWN이다.
2. 해당 서버에 이미 OPEN 상태 Incident가 없으면 새 Incident를 생성한다.
3. 이미 OPEN 상태 Incident가 있으면 중복 생성하지 않는다.
```

#### Incident 상태

```text
OPEN       : 장애 발생, 아직 해결되지 않음
RESOLVED   : 해결 완료
```

#### Incident 생성 예시

```json
{
  "id": 1,
  "server_id": 3,
  "server_name": "error-server",
  "status": "OPEN",
  "reason": "HTTP 500 error detected",
  "action_taken": null,
  "created_at": "2026-04-28T10:05:00",
  "resolved_at": null
}
```

---

### 7.10 장애 이력 조회 기능

#### API

```http
GET /incidents
GET /incidents?status=OPEN
GET /incidents?server_id=3
```

---

### 7.11 장애 상세 조회 기능

#### API

```http
GET /incidents/{incident_id}
```

---

### 7.12 장애 해결 처리 기능

#### API

```http
PATCH /incidents/{incident_id}/resolve
```

#### 요청 예시

```json
{
  "reason": "Mock error endpoint caused intentional failure",
  "action_taken": "Changed target URL to /mock/normal and verified recovery"
}
```

#### 응답 예시

```json
{
  "id": 1,
  "status": "RESOLVED",
  "reason": "Mock error endpoint caused intentional failure",
  "action_taken": "Changed target URL to /mock/normal and verified recovery",
  "resolved_at": "2026-04-28T10:30:00"
}
```

---

### 7.13 Mock Target API

프로젝트 시연을 위해 앱 내부에 테스트용 mock endpoint를 구현한다.

#### `/mock/normal`

```text
즉시 200 OK 반환
```

응답 예시

```json
{
  "status": "ok",
  "message": "normal server is running"
}
```

#### `/mock/slow`

```text
3초 대기 후 200 OK 반환
```

응답 예시

```json
{
  "status": "slow",
  "message": "slow response simulated"
}
```

#### `/mock/error`

```text
500 Internal Server Error 반환
```

응답 예시

```json
{
  "status": "error",
  "message": "server error simulated"
}
```

#### `/mock/random`

```text
랜덤하게 200 또는 500 반환
```

응답 예시

```json
{
  "status": "random",
  "message": "random status generated"
}
```

---

### 7.14 `/health` 엔드포인트

#### 목적

OpsWatch 앱 자체가 정상 동작하는지 확인하기 위한 엔드포인트이다.

#### API

```http
GET /health
```

#### 응답 예시

```json
{
  "status": "ok",
  "service": "opswatch",
  "version": "1.0.0"
}
```

GitHub Actions의 Docker smoke test와 Render 배포 확인에서 사용한다.

---

### 7.15 `/metrics` 엔드포인트

#### 목적

Prometheus가 수집할 수 있는 메트릭을 제공한다.

#### API

```http
GET /metrics
```

#### 메트릭 예시

```text
opswatch_total_checks
opswatch_up_count
opswatch_slow_count
opswatch_down_count
opswatch_open_incidents
opswatch_response_time_seconds
opswatch_check_failures_total
```

#### Prometheus 메트릭 설명

| 메트릭명 | 타입 | 의미 |
|---|---|---|
| `opswatch_total_checks` | Counter | 전체 점검 횟수 |
| `opswatch_up_count` | Counter | UP 판정 횟수 |
| `opswatch_slow_count` | Counter | SLOW 판정 횟수 |
| `opswatch_down_count` | Counter | DOWN 판정 횟수 |
| `opswatch_open_incidents` | Gauge | 현재 OPEN 상태 장애 수 |
| `opswatch_response_time_seconds` | Histogram 또는 Gauge | 서버 응답 시간 |
| `opswatch_check_failures_total` | Counter | 점검 실패 누적 횟수 |

---

## 8. 데이터베이스 설계

### 8.1 Server 테이블

#### 목적

점검 대상 서버 정보를 저장한다.

#### 필드

| 필드명 | 타입 | 설명 |
|---|---|---|
| id | Integer | PK |
| name | String | 서버 이름 |
| url | String | 점검 URL |
| description | String | 설명 |
| importance | String | LOW/MEDIUM/HIGH |
| is_active | Boolean | 점검 활성화 여부 |
| created_at | DateTime | 생성 시각 |
| updated_at | DateTime | 수정 시각 |

---

### 8.2 CheckResult 테이블

#### 목적

서버 상태 점검 결과를 저장한다.

#### 필드

| 필드명 | 타입 | 설명 |
|---|---|---|
| id | Integer | PK |
| server_id | Integer | FK |
| status | String | UP/SLOW/DOWN |
| status_code | Integer | HTTP 응답 코드 |
| response_time_ms | Float | 응답 시간 |
| message | String | 점검 결과 메시지 |
| checked_at | DateTime | 점검 시각 |

---

### 8.3 Incident 테이블

#### 목적

장애 발생 및 해결 이력을 저장한다.

#### 필드

| 필드명 | 타입 | 설명 |
|---|---|---|
| id | Integer | PK |
| server_id | Integer | FK |
| status | String | OPEN/RESOLVED |
| reason | String | 장애 원인 |
| action_taken | String | 조치 내용 |
| created_at | DateTime | 장애 발생 시각 |
| resolved_at | DateTime | 장애 해결 시각 |

---

## 9. API 명세 요약

### 9.1 Server API

| Method | Path | 설명 |
|---|---|---|
| POST | `/servers` | 서버 등록 |
| GET | `/servers` | 서버 목록 조회 |
| GET | `/servers/{server_id}` | 서버 상세 조회 |
| PUT | `/servers/{server_id}` | 서버 정보 수정 |
| DELETE | `/servers/{server_id}` | 서버 삭제 |

### 9.2 Check API

| Method | Path | 설명 |
|---|---|---|
| POST | `/checks/{server_id}` | 개별 서버 점검 |
| POST | `/checks/run-all` | 전체 서버 점검 |
| GET | `/checks` | 점검 이력 조회 |

### 9.3 Incident API

| Method | Path | 설명 |
|---|---|---|
| GET | `/incidents` | 장애 이력 조회 |
| GET | `/incidents/{incident_id}` | 장애 상세 조회 |
| PATCH | `/incidents/{incident_id}/resolve` | 장애 해결 처리 |

### 9.4 Mock API

| Method | Path | 설명 |
|---|---|---|
| GET | `/mock/normal` | 정상 서버 시뮬레이션 |
| GET | `/mock/slow` | 지연 서버 시뮬레이션 |
| GET | `/mock/error` | 장애 서버 시뮬레이션 |
| GET | `/mock/random` | 불안정 서버 시뮬레이션 |

### 9.5 Operation API

| Method | Path | 설명 |
|---|---|---|
| GET | `/health` | 앱 자체 상태 확인 |
| GET | `/metrics` | Prometheus 메트릭 제공 |

---

## 10. 프로젝트 디렉토리 구조

다음 구조를 기준으로 구현한다.

```text
opswatch/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging_config.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── servers.py
│   │   ├── checks.py
│   │   ├── incidents.py
│   │   ├── mock_targets.py
│   │   └── metrics.py
│   └── services/
│       ├── __init__.py
│       ├── monitor_service.py
│       └── incident_service.py
│
├── tests/
│   ├── __init__.py
│   ├── test_servers.py
│   ├── test_checks.py
│   ├── test_incidents.py
│   └── test_metrics.py
│
├── prometheus/
│   └── prometheus.yml
│
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── datasource.yml
│       └── dashboards/
│           └── dashboard.yml
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── docker.yml
│       └── security.yml
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── .gitignore
└── render.yaml
```

---

## 11. 각 파일 역할

### 11.1 app/main.py

FastAPI 앱의 진입점이다.

역할:

```text
1. FastAPI 인스턴스 생성
2. 라우터 등록
3. DB 초기화
4. CORS 설정 선택
5. /health 등록
```

---

### 11.2 app/database.py

DB 연결 및 세션 관리를 담당한다.

역할:

```text
1. SQLAlchemy engine 생성
2. SessionLocal 생성
3. Base 선언
4. get_db dependency 제공
```

---

### 11.3 app/models.py

SQLAlchemy ORM 모델을 정의한다.

포함 모델:

```text
Server
CheckResult
Incident
```

---

### 11.4 app/schemas.py

Pydantic 요청/응답 스키마를 정의한다.

포함 스키마:

```text
ServerCreate
ServerUpdate
ServerResponse
CheckResultResponse
IncidentResponse
IncidentResolveRequest
HealthResponse
```

---

### 11.5 app/core/config.py

설정값을 관리한다.

관리 항목:

```text
DATABASE_URL
APP_NAME
APP_VERSION
CHECK_TIMEOUT_SECONDS
SLOW_THRESHOLD_SECONDS
LOG_LEVEL
ENABLE_GITHUB_ISSUE
GH_REPO
GH_TOKEN
```

---

### 11.6 app/core/logging_config.py

Python logging 설정을 담당한다.

로그 포맷 예시:

```text
[2026-04-28 10:00:00] [INFO] [opswatch] Health check started: normal-server
[2026-04-28 10:00:03] [WARNING] [opswatch] Slow response detected: slow-server 3010ms
[2026-04-28 10:00:05] [ERROR] [opswatch] Service down: error-server status_code=500
```

---

### 11.7 app/routers/servers.py

서버 등록/조회/수정/삭제 API를 담당한다.

---

### 11.8 app/routers/checks.py

서버 상태 점검 및 점검 이력 조회 API를 담당한다.

---

### 11.9 app/routers/incidents.py

장애 이력 조회 및 해결 처리 API를 담당한다.

---

### 11.10 app/routers/mock_targets.py

시연용 mock endpoint를 담당한다.

---

### 11.11 app/routers/metrics.py

Prometheus `/metrics` 엔드포인트를 담당한다.

---

### 11.12 app/services/monitor_service.py

상태 점검 핵심 로직을 담당한다.

역할:

```text
1. httpx로 HTTP 요청 전송
2. 응답 시간 측정
3. UP/SLOW/DOWN 판별
4. CheckResult 저장용 데이터 생성
5. 메트릭 업데이트
```

---

### 11.13 app/services/incident_service.py

장애 이력 생성 및 해결 로직을 담당한다.

역할:

```text
1. DOWN 발생 시 Incident 생성
2. OPEN Incident 중복 생성 방지
3. Incident RESOLVED 처리
4. OPEN Incident 개수 계산
```

---

## 12. 테스트 요구사항

테스트는 pytest 기반으로 작성한다.

### 12.1 테스트 대상

```text
1. 서버 등록 성공
2. 잘못된 URL 등록 실패
3. 서버 목록 조회
4. 서버 수정
5. 서버 삭제
6. /mock/normal 상태 점검 시 UP 반환
7. /mock/slow 상태 점검 시 SLOW 반환
8. /mock/error 상태 점검 시 DOWN 반환
9. DOWN 발생 시 Incident 자동 생성
10. OPEN Incident 중복 생성 방지
11. Incident 조회
12. Incident 해결 처리
13. /health 응답 확인
14. /metrics 응답 확인
```

### 12.2 테스트 파일 구성

```text
tests/test_servers.py
- 서버 등록/조회/수정/삭제 테스트

tests/test_checks.py
- 상태 점검 로직 테스트
- UP/SLOW/DOWN 판별 테스트

tests/test_incidents.py
- 장애 이력 생성/조회/해결 테스트

tests/test_metrics.py
- /health, /metrics 응답 테스트
```

### 12.3 테스트 실행 명령어

```bash
pytest
```

### 12.4 커버리지 측정 명령어

```bash
pytest --cov=app --cov-report=term-missing
```

### 12.5 테스트 커버리지 목표

```text
최소 목표: 70% 이상
권장 목표: 80% 이상
```

---

## 13. GitHub Actions 요구사항

GitHub Actions는 단순 pytest 실행을 넘어서 다음 수준까지 구성한다.

---

### 13.1 ci.yml

목적:

```text
코드 품질 검사 + 테스트 + 커버리지 측정
```

Trigger:

```yaml
on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main" ]
```

Jobs:

```text
1. lint
2. test
3. coverage
```

수행 단계:

```text
1. 코드 checkout
2. Python 3.11 설치
3. requirements.txt 설치
4. ruff로 코드 품질 검사
5. pytest 실행
6. pytest-cov로 커버리지 측정
```

권장 명령어:

```bash
ruff check .
pytest --cov=app --cov-report=term-missing
```

---

### 13.2 docker.yml

목적:

```text
Docker 이미지 빌드 검증 + 컨테이너 smoke test
```

Trigger:

```yaml
on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main" ]
```

수행 단계:

```text
1. 코드 checkout
2. Docker 이미지 빌드
3. 컨테이너 실행
4. /health 호출
5. /metrics 호출
6. 정상 응답이면 성공
```

권장 명령어:

```bash
docker build -t opswatch:test .
docker run -d -p 8000:8000 --name opswatch-test opswatch:test
curl -f http://localhost:8000/health
curl -f http://localhost:8000/metrics
docker stop opswatch-test
docker rm opswatch-test
```

---

### 13.3 security.yml

목적:

```text
의존성 보안 취약점 점검
```

도구:

```text
pip-audit
```

수행 명령어:

```bash
pip install pip-audit
pip-audit
```

주의:

```text
security.yml은 선택 사항이다.
실패 가능성이 있으면 필수 workflow로 두지 말고 보고서에서 선택적 DevSecOps 확장으로 설명한다.
```

---

## 14. Docker 요구사항

### 14.1 Dockerfile

Dockerfile은 FastAPI 앱 실행 환경을 고정한다.

요구사항:

```text
1. Python 3.11 slim 이미지 사용
2. 작업 디렉토리 /app 설정
3. requirements.txt 복사
4. pip install 수행
5. 전체 소스 복사
6. uvicorn으로 앱 실행
7. Render의 PORT 환경변수 대응
```

권장 실행 명령:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 14.2 Docker build

```bash
docker build -t opswatch .
```

### 14.3 Docker run

```bash
docker run -p 8000:8000 opswatch
```

### 14.4 확인

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

---

## 15. Docker Compose 요구사항

Docker Compose는 로컬에서 FastAPI + Prometheus + Grafana를 함께 실행하기 위해 사용한다.

### 15.1 서비스 구성

```text
1. opswatch-api
2. prometheus
3. grafana
```

선택적으로 PostgreSQL을 추가할 수 있으나, 구현 안정성을 위해 SQLite를 기본으로 한다.

### 15.2 포트 구성

| 서비스 | 포트 |
|---|---|
| OpsWatch FastAPI | 8000 |
| Prometheus | 9090 |
| Grafana | 3000 |

### 15.3 실행 명령어

```bash
docker compose up --build
```

### 15.4 접속 주소

```text
FastAPI Swagger: http://localhost:8000/docs
Health Check: http://localhost:8000/health
Metrics: http://localhost:8000/metrics
Prometheus: http://localhost:9090
Grafana: http://localhost:3000
```

---

## 16. Prometheus 요구사항

### 16.1 prometheus.yml

Prometheus는 OpsWatch의 `/metrics`를 주기적으로 수집한다.

권장 설정:

```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "opswatch"
    metrics_path: "/metrics"
    static_configs:
      - targets: ["opswatch-api:8000"]
```

### 16.2 Prometheus에서 확인할 항목

```text
1. target 상태가 UP인지 확인
2. opswatch_total_checks 검색
3. opswatch_up_count 검색
4. opswatch_down_count 검색
5. opswatch_open_incidents 검색
```

---

## 17. Grafana 요구사항

### 17.1 Grafana 목적

Prometheus가 수집한 OpsWatch 메트릭을 시각화한다.

### 17.2 구성해야 할 패널

최소한 다음 패널을 구성한다.

```text
1. Total Checks
2. UP Count
3. SLOW Count
4. DOWN Count
5. Open Incidents
6. Response Time
```

### 17.3 보고서 캡처 항목

```text
1. Grafana 로그인 화면
2. Prometheus datasource 연결 화면
3. OpsWatch Dashboard 화면
4. 장애 발생 전/후 메트릭 변화 화면
```

---

## 18. Render 배포 요구사항

### 18.1 Render 배포 대상

Render에는 FastAPI OpsWatch 앱을 배포한다.

### 18.2 Render 배포 방식

가능한 방식:

```text
1. GitHub 저장소 연결
2. Web Service 생성
3. Build Command 설정
4. Start Command 설정
5. 환경 변수 설정
6. 자동 배포 확인
```

### 18.3 Render Start Command

Docker를 사용하지 않는 경우:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Docker 기반 배포를 사용하는 경우 Dockerfile의 CMD에서 처리한다.

### 18.4 Render 배포 후 확인

```text
1. https://배포주소.onrender.com/health
2. https://배포주소.onrender.com/docs
3. https://배포주소.onrender.com/metrics
```

---

## 19. 로깅 요구사항

### 19.1 로그 레벨

| 상황 | 로그 레벨 |
|---|---|
| 서버 등록 | INFO |
| 서버 점검 시작 | INFO |
| 정상 응답 | INFO |
| 응답 지연 | WARNING |
| 장애 발생 | ERROR |
| Incident 생성 | ERROR |
| Incident 해결 | INFO |
| 예상하지 못한 예외 | ERROR |

### 19.2 로그 예시

```text
[2026-04-28 10:00:00] [INFO] Server registered: normal-server
[2026-04-28 10:01:00] [INFO] Health check started: normal-server
[2026-04-28 10:01:01] [INFO] Server UP: normal-server response_time=120ms
[2026-04-28 10:02:03] [WARNING] Server SLOW: slow-server response_time=3010ms
[2026-04-28 10:03:00] [ERROR] Server DOWN: error-server status_code=500
[2026-04-28 10:03:01] [ERROR] Incident created: server=error-server
[2026-04-28 10:10:00] [INFO] Incident resolved: incident_id=1
```

### 19.3 보고서 활용

Render 로그 또는 로컬 실행 로그를 캡처하여 운영 증거로 사용한다.

---

## 20. 브랜치 전략

복잡한 Git Flow까지는 필요하지 않다. 다음 정도로 관리한다.

```text
main
- 최종 안정 버전
- Render 배포 대상

develop
- 개발 통합 브랜치

feature/server-api
- 서버 등록/조회 기능

feature/check-api
- 상태 점검 기능

feature/incident-api
- 장애 이력 기능

feature/metrics
- Prometheus 메트릭 기능

feature/docker-ci
- Docker 및 GitHub Actions 구성
```

권장 흐름:

```text
feature 브랜치에서 개발
→ develop으로 merge
→ 테스트 통과
→ main으로 merge
→ Render 배포
```

혼자 진행하는 프로젝트라면 브랜치 수를 줄여도 된다.  
하지만 보고서에서는 최소 2~3개 기능 브랜치를 사용한 증거를 남기는 것이 좋다.

---

## 21. 커밋 메시지 규칙

커밋 메시지는 다음 형식을 권장한다.

```text
feat: 서버 등록 API 구현
feat: 서버 상태 점검 로직 구현
feat: 장애 이력 자동 생성 기능 추가
test: 서버 등록 API 테스트 추가
test: 장애 해결 처리 테스트 추가
ci: GitHub Actions 테스트 워크플로우 추가
ci: Docker build smoke test 추가
chore: Dockerfile 추가
docs: README 실행 방법 작성
fix: slow 응답 판별 기준 수정
```

---

## 22. README.md 필수 내용

README에는 다음 항목을 포함한다.

```text
1. 프로젝트 소개
2. 주요 기능
3. 기술 스택
4. 아키텍처
5. 실행 방법
6. API 사용 예시
7. 테스트 실행 방법
8. Docker 실행 방법
9. Docker Compose 실행 방법
10. Prometheus/Grafana 확인 방법
11. Render 배포 URL
12. GitHub Actions 설명
13. 장애 시나리오
14. 결과 화면
15. 한계 및 개선 방향
```

---

## 23. 보고서에 포함할 장애 시나리오

보고서에는 최소 다음 시나리오를 포함한다.

### 시나리오 1. 정상 서버 점검

```text
1. /mock/normal URL 등록
2. 개별 점검 실행
3. 상태 UP 확인
4. CheckResult 저장 확인
5. INFO 로그 확인
```

### 시나리오 2. 응답 지연 서버 점검

```text
1. /mock/slow URL 등록
2. 개별 점검 실행
3. 응답 시간이 2초 초과
4. 상태 SLOW 확인
5. WARNING 로그 확인
```

### 시나리오 3. 장애 서버 점검

```text
1. /mock/error URL 등록
2. 개별 점검 실행
3. 상태 DOWN 확인
4. Incident 자동 생성 확인
5. ERROR 로그 확인
6. Grafana에서 DOWN count 증가 확인
```

### 시나리오 4. 장애 해결 처리

```text
1. OPEN 상태 Incident 조회
2. 장애 원인과 조치 내용 입력
3. resolve API 호출
4. Incident 상태 RESOLVED 확인
5. resolved_at 기록 확인
```

### 시나리오 5. 전체 서버 점검

```text
1. normal, slow, error, random 서버 등록
2. /checks/run-all 호출
3. UP/SLOW/DOWN 요약 결과 확인
4. 점검 결과 DB 저장 확인
5. Grafana 패널 변화 확인
```

---

## 24. 최종 산출물

최종 제출 또는 보고서에 포함할 산출물은 다음과 같다.

```text
1. GitHub Repository URL
2. Render 배포 URL
3. README.md
4. Dockerfile
5. docker-compose.yml
6. GitHub Actions workflow 파일
7. 테스트 코드
8. Prometheus 설정 파일
9. Grafana 대시보드 화면
10. Swagger UI 화면
11. 장애 시나리오 실행 화면
12. Render 로그 화면
13. GitHub Actions 성공 화면
14. 최종 보고서
```

---

## 25. 구현 우선순위

### 25.1 반드시 구현해야 하는 핵심 기능

```text
1. FastAPI 앱 기본 구조
2. Server CRUD
3. Mock Target API
4. 개별 서버 상태 점검
5. 전체 서버 상태 점검
6. UP/SLOW/DOWN 판별
7. CheckResult 저장
8. Incident 자동 생성
9. Incident 조회/해결
10. logging
11. /health
12. pytest
13. GitHub Actions CI
14. Dockerfile
15. Render 배포
```

### 25.2 가산점용 심화 기능

```text
1. /metrics
2. prometheus-client
3. Docker Compose
4. Prometheus
5. Grafana
6. Docker build workflow
7. Docker smoke test
8. pytest-cov
9. ruff
10. pip-audit
```

### 25.3 시간이 부족하면 제외 가능한 기능

```text
1. HTML 대시보드
2. PostgreSQL
3. Grafana 자동 provisioning
4. pip-audit
5. 복잡한 인증 기능
6. 실제 주기적 스케줄러
```

주의: 주기적 자동 점검은 구현하지 않아도 된다.  
수동 점검 API와 전체 점검 API만 있어도 프로젝트 목적을 충분히 만족한다.  
다만 시간이 남으면 APScheduler를 이용해 일정 주기 자동 점검을 추가할 수 있다.

---

## 26. Claude Code에게 구현 요청 시 유의사항

Claude Code에게 이 문서를 전달할 때 다음 요구를 함께 전달한다.

```text
이 문서를 기준으로 프로젝트를 구현해줘.

중요한 원칙:
1. 한 번에 모든 기능을 과하게 만들지 말고, 실행 가능한 최소 단위부터 구현해줘.
2. FastAPI 앱이 먼저 실행되도록 만들어줘.
3. 그 다음 Server CRUD, Mock API, Check API, Incident API 순서로 구현해줘.
4. 각 기능 구현 후 테스트 코드를 함께 작성해줘.
5. GitHub Actions, Dockerfile, docker-compose.yml까지 포함해줘.
6. README.md에는 실행 방법과 시연 시나리오를 자세히 작성해줘.
7. 불필요하게 복잡한 인증, 프론트엔드, 외부 클라우드 연동은 넣지 마.
8. Render 배포를 고려해 PORT 환경변수에 대응하도록 만들어줘.
9. Prometheus/Grafana는 Docker Compose 기반 로컬 모니터링 환경으로 구성해줘.
10. 모든 코드는 초보자가 보고 이해할 수 있도록 구조적으로 작성해줘.
```

---

## 27. 최종 구현 완료 기준

프로젝트가 완료되었다고 판단하는 기준은 다음과 같다.

```text
1. 로컬에서 uvicorn으로 FastAPI 앱 실행 가능
2. Swagger UI에서 모든 주요 API 호출 가능
3. /mock/normal, /mock/slow, /mock/error가 정상 동작
4. 서버 등록 후 상태 점검 가능
5. UP/SLOW/DOWN 판별 가능
6. DOWN 발생 시 Incident 자동 생성
7. Incident 해결 처리 가능
8. pytest 테스트 통과
9. GitHub Actions CI 성공
10. Docker build 성공
11. Docker run 후 /health 응답 성공
12. Docker Compose로 Prometheus/Grafana 실행 가능
13. Prometheus target UP 확인 가능
14. Grafana에서 메트릭 시각화 가능
15. Render 배포 URL에서 /health 접근 가능
16. README에 실행/테스트/배포/모니터링 방법 작성 완료
17. 보고서에 장애 시나리오와 운영 증거 캡처 포함
```

---

## 28. 최종 요약

OpsWatch는 단순한 FastAPI CRUD 앱이 아니라, 여러 서버를 운영하는 상황을 가정하여 통신 상태를 점검하고 장애 이력을 관리하는 DevOps 실습형 SW이다.

이 프로젝트는 다음 요소를 모두 보여준다.

```text
1. 자체 SW 구현
2. 서버 상태 점검 로직
3. 장애 이력관리
4. 테스트 자동화
5. GitHub Actions CI
6. Docker 패키징
7. Render 배포
8. 로그 기반 운영
9. Prometheus/Grafana 모니터링
10. 장애 발생 및 복구 시나리오
```

최종적으로 이 프로젝트는 수업의 DevOps 파이프라인을 다음과 같이 재현한다.

```text
Plan
→ Code
→ Test
→ CI
→ Package
→ Deploy
→ Operate
→ Monitor
```

보고서 제목은 다음과 같이 작성한다.

```text
OpsWatch: FastAPI 기반 배포 서버 통신 상태 모니터링 및 장애 이력관리 시스템의 DevOps 파이프라인 구축
```


---

## 29. v2 추가: 로깅 수업 반영 요구사항

### 29.1 로깅 강화 목적

OpsWatch에서 로그는 단순 출력이 아니라 **운영 중 문제 분석을 위한 증거**이다. 운영 환경에서는 개발자가 직접 디버거를 붙일 수 없기 때문에, 문제 발생 시 로그만 보고 다음 질문에 답할 수 있어야 한다.

```text
1. 어떤 서버에서 문제가 발생했는가?
2. 언제 발생했는가?
3. 어떤 API 요청에서 발생했는가?
4. 응답 코드는 무엇이었는가?
5. 응답 시간은 얼마였는가?
6. 어떤 예외가 발생했는가?
7. 어느 파일, 어느 함수, 어느 라인에서 문제가 발생했는가?
8. Incident가 생성되었는가?
9. GitHub Issue 생성에 성공했는가?
10. 장애가 해결되었는가?
```

따라서 v2에서는 기존의 단순 로그 요구사항을 다음과 같이 강화한다.

```text
기존:
INFO/WARNING/ERROR 수준으로 서버 상태 점검 결과 기록

변경:
좋은 로그 포맷 적용
로그 레벨 정책 명확화
이벤트명 기반 로그 작성
예외 발생 시 logger.exception으로 traceback 기록
장애 발생 시 Incident 및 선택적 GitHub Issue와 연결
```

---

## 30. v2 추가: 로그 레벨 정책

### 30.1 로그 레벨 기준

| 로그 레벨 | 사용 상황 | OpsWatch 예시 |
|---|---|---|
| DEBUG | 개발 중 내부 로직, 변수 상태 확인 | 상태 판별 기준값, 내부 분기 확인 |
| INFO | 정상적인 주요 작업 흐름 | 서버 등록, 점검 시작, 정상 응답, 장애 해결 |
| WARNING | 장애는 아니지만 주의가 필요한 상황 | 응답 지연, GitHub Issue 생성 스킵, OPEN Incident 중복 |
| ERROR | 기능 실패, 장애 발생 | 서버 DOWN, Timeout, Connection Error, Incident 생성 |
| CRITICAL | 앱 자체 운영 불가능 수준 | DB 연결 실패, 핵심 설정 누락 |

### 30.2 상황별 로그 이벤트명

| 상황 | 레벨 | 이벤트명 |
|---|---|---|
| 앱 시작 | INFO | APP_STARTED |
| 서버 등록 | INFO | SERVER_CREATED |
| 서버 수정 | INFO | SERVER_UPDATED |
| 서버 삭제 | INFO | SERVER_DELETED |
| 점검 시작 | INFO | SERVER_CHECK_STARTED |
| 정상 응답 | INFO | SERVER_UP |
| 응답 지연 | WARNING | SERVER_SLOW |
| 서버 장애 | ERROR | SERVER_DOWN |
| Timeout | ERROR | SERVER_TIMEOUT |
| Connection Error | ERROR | SERVER_CONNECTION_ERROR |
| Incident 생성 | ERROR | INCIDENT_CREATED |
| Incident 중복 방지 | WARNING | INCIDENT_ALREADY_OPEN |
| Incident 해결 | INFO | INCIDENT_RESOLVED |
| GitHub Issue 생성 성공 | INFO | GITHUB_ISSUE_CREATED |
| GitHub Issue 환경변수 누락 | WARNING | GITHUB_ISSUE_SKIPPED |
| GitHub Issue 생성 실패 | WARNING | GITHUB_ISSUE_CREATE_FAILED |
| 예상하지 못한 예외 | ERROR | UNEXPECTED_EXCEPTION |
| DB 연결 실패 | CRITICAL | DATABASE_CONNECTION_FAILED |

### 30.3 좋은 로그 포맷

수업에서 배운 좋은 로그의 기본 요소를 반영하여 다음 정보를 포함한다.

```text
시간(timestamp)
로그 레벨
위치 정보: 파일명, 라인 번호, 함수명
메시지: 이벤트명과 핵심 상태 정보
환경 정보: 필요 시 PID, 모듈명 등
```

권장 Python logging 포맷은 다음과 같다.

```python
"%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d (%(funcName)s) | %(message)s"
```

로그 예시:

```text
2026-04-28 10:00:00 | INFO | servers.py:42 (create_server) | SERVER_CREATED server_id=1 name=normal-server url=http://localhost:8000/mock/normal
2026-04-28 10:02:03 | WARNING | monitor_service.py:75 (check_server) | SERVER_SLOW server_id=2 name=slow-server status_code=200 response_time_ms=3010 threshold_ms=2000
2026-04-28 10:03:00 | ERROR | monitor_service.py:87 (check_server) | SERVER_DOWN server_id=3 name=error-server status_code=500 response_time_ms=45
```

### 30.4 나쁜 로그와 좋은 로그 비교

나쁜 로그:

```text
에러 발생
실패
안 됨
문제
```

좋은 로그:

```text
SERVER_DOWN server_id=3 name=error-server url=http://localhost:8000/mock/error status_code=500 response_time_ms=42
SERVER_TIMEOUT server_id=4 name=timeout-server timeout_seconds=5
INCIDENT_CREATED incident_id=10 server_id=3 reason=HTTP_500
```

좋은 로그는 다음을 포함해야 한다.

```text
1. 이벤트명
2. server_id
3. server_name
4. url
5. status
6. status_code
7. response_time_ms
8. incident_id
9. error type
10. error message
```

---

## 31. v2 추가: logger.exception 기반 예외 추적

### 31.1 적용 목적

운영 중 장애가 발생했을 때 단순히 `ERROR`만 기록하면 원인 분석이 어렵다. 따라서 예상하지 못한 예외는 반드시 `logger.exception()`을 사용해 traceback을 남긴다.

### 31.2 logger.exception 사용 기준

다음 상황에서는 `logger.exception()`을 사용한다.

```text
1. 예상하지 못한 예외 발생
2. HTTP 요청 처리 중 예외 발생
3. DB 저장 중 예외 발생
4. Incident 생성 중 예외 발생
5. GitHub Issue 생성 중 예외 발생
6. /mock/crash 의도적 예외 발생
```

예시:

```python
try:
    result = await check_server(server)
except Exception as e:
    logger.exception(
        "UNEXPECTED_EXCEPTION | server_id=%s | name=%s | url=%s | error=%s",
        server.id,
        server.name,
        server.url,
        str(e),
    )
```

### 31.3 `/mock/crash` 선택 엔드포인트

로깅 수업의 “의도적 장애 삽입” 실습을 프로젝트에 반영하기 위해 다음 엔드포인트를 선택적으로 구현한다.

```http
GET /mock/crash
```

동작:

```text
1. 의도적으로 RuntimeError 발생
2. logger.exception으로 traceback 기록
3. 사용자에게는 단순한 오류 응답 반환
4. 선택적으로 GitHub Issue 자동 생성 흐름과 연결
```

사용자 응답 예시:

```json
{
  "status": "error",
  "message": "Internal Server Error"
}
```

로그 예시:

```text
2026-04-28 10:15:00 | ERROR | mock_targets.py:58 (crash) | MOCK_CRASH_TRIGGERED error=RuntimeError: intentional crash for logging test
Traceback (most recent call last):
...
RuntimeError: intentional crash for logging test
```

---

## 32. v2 추가: GitHub Issue 자동 생성 선택 기능

### 32.1 기능 목적

장애 발생 시 단순히 로그와 DB에만 남기는 것이 아니라, GitHub Issue를 자동 생성하여 개발 이슈 관리와 장애 대응을 연결한다.

이 기능은 로깅 수업의 “에러 발생 시 GitHub Issue 자동 생성” 흐름을 OpsWatch 프로젝트에 맞게 적용한 것이다.

### 32.2 필수 여부

이 기능은 **선택 심화 기능**이다.

기본 프로젝트 완성에는 없어도 되지만, 구현하면 다음 가산점 요소로 활용할 수 있다.

```text
1. 로깅 수업 내용 직접 반영
2. 장애 대응 자동화 구현
3. GitHub Issue와 운영 장애 연결
4. fix 브랜치/커밋/재배포 흐름 설명 가능
5. DevOps의 Operate → Monitor → Feedback → Code 흐름 표현 가능
```

### 32.3 동작 조건

```text
1. 서버 점검 결과가 DOWN이다.
2. 새 Incident가 생성되었다.
3. ENABLE_GITHUB_ISSUE=true이다.
4. GH_REPO 환경변수가 존재한다.
5. GH_TOKEN 환경변수가 존재한다.
6. 동일 Incident에 이미 GitHub Issue URL이 없을 때만 생성한다.
```

### 32.4 중복 생성 방지

장애가 계속 발생할 때마다 GitHub Issue가 무한히 생성되면 안 된다.

따라서 다음 정책을 적용한다.

```text
1. 서버별 OPEN Incident는 하나만 유지한다.
2. 이미 OPEN Incident가 있으면 새 Incident를 생성하지 않는다.
3. 새 Incident가 생성되지 않으면 GitHub Issue도 생성하지 않는다.
4. Incident에 github_issue_url이 있으면 다시 생성하지 않는다.
```

### 32.5 환경변수

```text
ENABLE_GITHUB_ISSUE=false
GH_REPO=username/repository
GH_TOKEN=GitHub Personal Access Token
```

보안 주의사항:

```text
1. GH_TOKEN은 절대 코드에 직접 작성하지 않는다.
2. 로컬에서는 .env 또는 shell 환경변수로 설정한다.
3. Render에서는 Environment Variables에 등록한다.
4. GitHub Actions에서는 Repository Secrets에 등록한다.
5. README에 실제 토큰 값을 노출하지 않는다.
```

`.env.example` 예시:

```env
DATABASE_URL=sqlite:///./opswatch.db
LOG_LEVEL=INFO
CHECK_TIMEOUT_SECONDS=5
SLOW_THRESHOLD_SECONDS=2
ENABLE_GITHUB_ISSUE=false
GH_REPO=your-github-id/your-repository
GH_TOKEN=your-token-here
```

주의: `.env.example`에는 실제 토큰을 넣지 않는다.

### 32.6 GitHub Issue 제목 예시

```text
[OpsWatch Incident] error-server DOWN: HTTP 500
```

### 32.7 GitHub Issue 본문 예시

````markdown
## Summary
- server: error-server
- url: http://localhost:8000/mock/error
- status: DOWN
- status_code: 500
- response_time_ms: 42

## Incident
- incident_id: 3
- created_at: 2026-04-28 10:03:00

## Error Message
HTTP 500 error detected

## Logs
```text
2026-04-28 10:03:00 | ERROR | monitor_service.py:87 (check_server) | SERVER_DOWN server=error-server status_code=500 response_time_ms=42
```

## Next Action
장애 원인 확인 후 fix 브랜치에서 수정 필요
````

### 32.8 GitHub Issue 생성 실패 시 처리

GitHub Issue 생성 실패가 전체 점검 기능 실패로 이어지면 안 된다.

따라서 다음 정책을 적용한다.

```text
1. GitHub Issue 생성 실패 시 WARNING 로그만 남긴다.
2. Incident 생성은 정상 유지한다.
3. API 응답은 정상 반환한다.
4. metrics에서 issue 생성 실패 횟수를 증가시킨다.
```

로그 예시:

```text
WARNING | GITHUB_ISSUE_SKIPPED reason=missing_env GH_REPO=false GH_TOKEN=false
WARNING | GITHUB_ISSUE_CREATE_FAILED status_code=401 message=Bad credentials
INFO | GITHUB_ISSUE_CREATED incident_id=3 url=https://github.com/user/repo/issues/7
```

### 32.9 추가 파일

기존 구조에 다음 파일을 추가한다.

```text
app/services/github_issue_service.py
```

역할:

```text
1. ENABLE_GITHUB_ISSUE 설정 확인
2. GH_REPO 환경변수 읽기
3. GH_TOKEN 환경변수 읽기
4. GitHub Issue API 호출
5. 성공 시 INFO 로그 기록
6. 실패 시 WARNING 로그 기록
7. 기능 실패가 전체 서버 점검 실패로 이어지지 않도록 예외 처리
```

### 32.10 DB 필드 추가

Incident 테이블에 다음 필드를 선택적으로 추가한다.

```text
github_issue_url: String, nullable=True
```

Incident 응답 예시:

```json
{
  "id": 1,
  "server_id": 3,
  "server_name": "error-server",
  "status": "OPEN",
  "reason": "HTTP 500 error detected",
  "action_taken": null,
  "github_issue_url": "https://github.com/user/repo/issues/7",
  "created_at": "2026-04-28T10:05:00",
  "resolved_at": null
}
```

---

## 33. v2 추가: 장애 대응 운영 시나리오 확장

### 33.1 기존 장애 대응 흐름

```text
서버 DOWN
→ Incident 자동 생성
→ 로그 확인
→ 원인 작성
→ 조치 내용 작성
→ Incident RESOLVED 처리
```

### 33.2 v2 확장 흐름

```text
서버 DOWN
→ ERROR 로그 기록
→ logger.exception traceback 기록 선택
→ Incident 자동 생성
→ GitHub Issue 자동 생성 선택
→ fix/issue-{번호}-{요약} 브랜치 생성
→ 코드 수정
→ 테스트 실행
→ GitHub Actions 통과
→ main 병합
→ Render 재배포
→ 정상 상태 재점검
→ Incident RESOLVED 처리
```

### 33.3 보고서용 시나리오

#### 시나리오 6. 예외 traceback 로그 확인

```text
1. /mock/crash 호출 또는 의도적 예외 발생
2. 사용자에게는 단순한 에러 응답 반환
3. Render 또는 로컬 로그에서 logger.exception traceback 확인
4. 파일명, 라인번호, 함수명, 예외 메시지 확인
5. 이 로그를 통해 문제 발생 위치를 추적할 수 있음을 설명
```

#### 시나리오 7. GitHub Issue 자동 생성 선택

```text
1. ENABLE_GITHUB_ISSUE=true 설정
2. GH_REPO, GH_TOKEN 설정
3. /mock/error 서버 등록
4. 상태 점검 실행
5. DOWN 판정
6. ERROR 로그 기록
7. Incident 자동 생성
8. GitHub Issue 자동 생성
9. Issue 제목과 본문 확인
10. fix/issue-{번호}-server-down 브랜치 생성
11. 코드 수정 또는 대상 URL 수정
12. 테스트 실행
13. GitHub Actions 통과
14. main 병합
15. Render 재배포
16. Incident RESOLVED 처리
```

#### 시나리오 8. GitHub Issue 생성 스킵

```text
1. ENABLE_GITHUB_ISSUE=true 설정
2. GH_TOKEN은 설정하지 않음
3. DOWN 장애 발생
4. Incident는 정상 생성됨
5. GitHub Issue는 생성되지 않음
6. WARNING 로그 확인: GITHUB_ISSUE_SKIPPED
7. 전체 점검 기능은 실패하지 않음
```

---

## 34. v2 추가: 테스트 요구사항 확장

기존 테스트에 다음 항목을 추가한다.

```text
1. logger.exception 흐름을 유발하는 예외 상황 테스트
2. GitHub Issue 비활성화 시 생성 스킵 테스트
3. GH_REPO/GH_TOKEN 누락 시 WARNING 처리 테스트
4. GitHub Issue 생성 실패 시 전체 점검 기능은 실패하지 않는지 테스트
5. OPEN Incident가 이미 있으면 GitHub Issue 중복 생성이 되지 않는지 테스트
```

추가 테스트 파일:

```text
tests/test_github_issue.py
```

테스트 예시 목표:

```text
test_github_issue_skipped_when_disabled
test_github_issue_skipped_when_env_missing
test_github_issue_failure_does_not_break_incident_creation
test_github_issue_not_created_when_open_incident_exists
test_mock_crash_returns_error_response
```

---

## 35. v2 추가: README 및 보고서 반영 항목

README와 보고서에는 다음 항목을 추가한다.

```text
1. 로깅 설계
2. 로그 레벨 정책
3. 좋은 로그 포맷 설명
4. logger.exception을 사용한 traceback 기록 예시
5. Render Logs 캡처
6. 장애 발생 시 Incident 생성 과정
7. 선택적 GitHub Issue 자동 생성 설정 방법
8. GH_REPO/GH_TOKEN 환경변수 설정 방법
9. GitHub Issue 생성 성공/실패/스킵 로그 예시
10. fix 브랜치 기반 장애 해결 흐름
```

보고서에서 강조할 문장 예시:

```text
본 프로젝트는 단순히 서버 상태를 점검하는 기능에 그치지 않고, 운영 중 발생하는 장애를 로그로 추적할 수 있도록 설계하였다. 특히 ERROR 상황에서는 서버명, URL, 응답 코드, 응답 시간 등 문제 분석에 필요한 맥락 정보를 함께 기록하였고, 예상하지 못한 예외는 logger.exception을 사용하여 traceback을 남기도록 구현하였다.
```

```text
또한 선택 기능으로 GitHub Issue 자동 생성을 구현하여 장애 발생 → 이슈 생성 → fix 브랜치 수정 → GitHub Actions 검증 → Render 재배포 → Incident 해결 처리로 이어지는 DevOps 운영 흐름을 재현하였다.
```

---

## 36. v2 최종 구현 완료 기준 추가

기존 완료 기준에 다음을 추가한다.

```text
1. INFO/WARNING/ERROR 로그가 상황별로 적절히 기록됨
2. 로그 포맷에 시간, 레벨, 파일명, 라인번호, 함수명, 메시지가 포함됨
3. 예외 발생 시 logger.exception으로 traceback이 기록됨
4. /mock/crash 또는 예외 시나리오를 통해 traceback 로그를 시연할 수 있음
5. ENABLE_GITHUB_ISSUE=false일 때 GitHub Issue 생성이 안전하게 비활성화됨
6. GH_REPO/GH_TOKEN이 없을 때 WARNING 로그만 남기고 기능이 계속 동작함
7. 선택적으로 GitHub Issue 자동 생성이 성공함
8. 선택적으로 Incident에 github_issue_url이 저장됨
9. GitHub Issue 기반 fix 브랜치/커밋/재배포 흐름을 보고서에 설명할 수 있음
```

---

## 37. v2 최종 요약

OpsWatch v2는 기존의 서버 상태 점검 및 장애 이력관리 시스템에 로깅 수업 내용을 반영한 버전이다.

기존 핵심 기능:

```text
서버 등록
서버 상태 점검
UP/SLOW/DOWN 판별
점검 이력 저장
장애 이력 생성
Prometheus/Grafana 모니터링
Render 배포
```

v2 강화 기능:

```text
좋은 로그 포맷
로그 레벨 정책
logger.exception traceback 기록
GitHub Issue 자동 생성 선택 기능
Issue 기반 fix 브랜치 장애 대응 흐름
Render 로그 기반 운영 증거 강화
```

최종적으로 이 프로젝트는 수업의 DevOps 파이프라인을 다음과 같이 재현한다.

```text
Plan
→ Code
→ Test
→ CI
→ Package
→ Deploy
→ Operate
→ Log
→ Monitor
→ Incident Response
→ Feedback to Code
```

보고서 제목은 다음 중 하나를 사용한다.

```text
OpsWatch: FastAPI 기반 배포 서버 통신 상태 모니터링 및 장애 이력관리 시스템의 DevOps 파이프라인 구축
```

또는 로깅 수업 반영을 강조하려면 다음 제목을 사용한다.

```text
OpsWatch: 로그 기반 장애 추적과 모니터링을 포함한 배포 서버 통신 상태 관리 DevOps 파이프라인 구축
```
