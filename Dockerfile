FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
   PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
   apt-get upgrade -y && \
   rm -rf /var/lib/apt/lists/* && \
   groupadd -r appgroup && \
   useradd -r -g appgroup appuser

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip setuptools && \
   python -m pip install --no-cache-dir --only-binary=:all: -r requirements.txt && \
   python -m pip check && \
   python -m pip uninstall -y pip

COPY . .
RUN chown -R appuser:appgroup /app

USER appuser

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
   CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
