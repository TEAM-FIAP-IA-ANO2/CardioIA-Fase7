FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY cardioia ./cardioia
COPY artifacts ./artifacts
COPY data ./data
RUN pip install --no-cache-dir .
RUN useradd -m appuser && mkdir -p /app/.runtime && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn","cardioia.api:app","--host","0.0.0.0","--port","8000"]
