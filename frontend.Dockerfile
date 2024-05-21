FROM python:3.8-alpine

RUN pip install grpcio grpcio-tools Flask waitress Flask-Session

WORKDIR /app

COPY src/frontend/*.py src/frontend/*.pyi src/frontend/replica_config.json ./

ENTRYPOINT ["python", "-u", "frontend_service.py"]
