FROM python:3.12-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
  gcc \
  default-libmysqlclient-dev \
  pkg-config \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# poetry 설치
RUN pip install --upgrade pip && pip install poetry

# 작업 디렉토리
WORKDIR /backend

# pyproject.toml & poetry.lock 복사 → 의존성 설치
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi --without dev

# 실제 소스 복사
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
