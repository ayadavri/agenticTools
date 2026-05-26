# AgentCore Runtime requires ARM64 (AWS Graviton). Build with:
#   docker build --platform linux/arm64 -t get-consumer-documents-runtime .
#
# On x86 hosts, use buildx:
#   docker buildx build --platform linux/arm64 -t get-consumer-documents-runtime --load .

FROM public.ecr.aws/docker/library/python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCKER_CONTAINER=1 \
    PORT=8080

COPY runtime/requirements.txt /app/runtime/requirements.txt
RUN pip install --no-cache-dir -r /app/runtime/requirements.txt

COPY collection /app/collection
COPY runtime /app/runtime

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/ping')" || exit 1

CMD ["python", "/app/runtime/main.py"]
