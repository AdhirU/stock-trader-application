FROM python:3.8-alpine

RUN pip install grpcio grpcio-tools requests

WORKDIR /app

COPY src/catalog/*.py src/catalog/*.pyi ./

ENTRYPOINT ["python", "-u", "catalog_service.py"]
