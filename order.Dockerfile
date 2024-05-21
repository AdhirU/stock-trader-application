FROM python:3.8-alpine

RUN pip install grpcio grpcio-tools

WORKDIR /app

COPY src/order/*.py src/order/*.pyi src/order/replica_config.json ./

ENTRYPOINT ["python", "-u", "order_service.py"]
