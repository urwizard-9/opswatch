# ── 빌드 스테이지 ──
FROM python:3.13-slim AS builder

WORKDIR /app

# 의존성만 먼저 복사 (레이어 캐싱 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── 런타임 스테이지 ──
FROM python:3.13-slim

WORKDIR /app

# 빌드 스테이지에서 설치된 패키지 복사
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 소스 코드 복사
COPY app/ ./app/

# 비루트 사용자 (보안)
RUN adduser --disabled-password --gecos "" opswatch \
    && chown -R opswatch:opswatch /app
USER opswatch

# 포트 노출
EXPOSE 8000

# 헬스체크 (Render / Docker 모두 사용)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
