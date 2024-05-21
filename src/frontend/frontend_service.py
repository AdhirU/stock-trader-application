import os
import json
from socket import gethostname, gethostbyname
from threading import Lock
from flask import Flask, request, session, redirect, url_for
from flask_session import Session
from waitress import serve
import grpc
import catalog_pb2
import catalog_pb2_grpc
import order_pb2
import order_pb2_grpc

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/stocks/<stock_name>")
def get_stock(stock_name):
    if os.getenv("CACHING") == "ON":
        if "cache" not in session:
            session["cache"] = {}
        cache = session.get("cache")
        # Set timestamp for cache eviction
        if "timestamp" not in session:
            session["timestamp"] = 0
        # Load data from cache if available
        if stock_name in cache:
            data = {
                "name": cache[stock_name]["name"],
                "price": cache[stock_name]["price"],
                "quantity": cache[stock_name]["quantity"],
            }
            return {"data": data}
    # Query Catalog Service for data and update cache
    catalog_host = os.getenv("CATALOG_HOST", "catalog") + ":50015"
    with grpc.insecure_channel(catalog_host) as channel:
        stub = catalog_pb2_grpc.CatalogStub(channel)
        res = stub.LookUp(catalog_pb2.StockName(stockName=stock_name))
        if res.price == -1:
            return {"error": {"code": 404, "message": "stock not found"}}, 404
        else:
            data = {
                "name": stock_name,
                "price": round(res.price, 2),
                "quantity": res.quantity,
            }
            # Implementing LRU for cache eviction
            if os.getenv("CACHING") == "ON":
                timestamp = session.get("timestamp")
                cache_size = os.environ.get("CACHE_SIZE", 64)
                if len(cache) >= cache_size:
                    least_recent_time = timestamp
                    for stock, data in cache:
                        if data["timestamp"] < least_recent_time:
                            least_recent_time = data["timestamp"]
                            lru_stock = stock
                    del cache[lru_stock]

                # Storing newly updated data in cache
                cache[stock_name] = data
                cache[stock_name]["timestamp"] = timestamp
                session["timestamp"] += 1

            return {"data": data}


@app.route("/orders/<order_number>")
def get_order_details(order_number):
    count = 0
    while count < 3:
        order_host = os.getenv("ORDER_HOST") + ":" + os.getenv("ORDER_PORT")
        try:
            with grpc.insecure_channel(order_host) as channel:
                stub = order_pb2_grpc.OrderStub(channel)
                res = stub.GetOrder(
                    order_pb2.OrderNumber(orderNumber=int(order_number))
                )
                if res.orderNumber == -1:
                    return {"error": {"code": 404, "message": "order not found"}}, 404
                else:
                    data = {
                        "number": res.orderNumber,
                        "name": res.stockName,
                        "type": res.type,
                        "quantity": res.quantity,
                    }
                return {"data": data}
        except:
            print("Leader down, picking new leader")
            elect_leader()
            count += 1
    return {"error": {"code": 500, "message": "service down"}}, 500


@app.route("/orders", methods=["POST"])
def place_order():
    name = request.form["name"]
    quantity = int(request.form["quantity"])
    trade = request.form["type"]

    count = 0
    while count < 3:
        order_host = os.getenv("ORDER_HOST") + ":" + os.getenv("ORDER_PORT")
        try:
            with grpc.insecure_channel(order_host) as channel:
                stub = order_pb2_grpc.OrderStub(channel)
                res = stub.Trade(
                    order_pb2.TradeDetails(stockName=name, N=quantity, type=trade),
                    timeout=1,
                )
                if res.code == -1:
                    return {"error": {"code": 404, "message": res.message}}, 404
                else:
                    return {"data": {"transaction_number": res.transactionNumber}}
        except Exception:
            print("Leader down, picking new leader")
            elect_leader()
            count += 1
    return {"error": {"code": 500, "message": "service down"}}, 500


@app.route("/cache/<stock_name>", methods=["POST"])
def invalidate_cache(stock_name):
    if "cache" not in session:
        session["cache"] = {}
    cache = session.get("cache")
    if stock_name in cache:
        del cache[stock_name]
    return {"code": 1, "message": "cache successfully deleted"}


@app.errorhandler(404)
def not_found(error):
    res = {"code": 404, "message": "invalid request"}
    return {"error": res}, 404


def elect_leader():
    # Load replica details from config file
    with open("replica_config.json", "r") as f:
        replica_data = json.load(f)
    replica_ids = [int(x) for x in replica_data.keys()]
    dead_replicas = []
    leader_id = None
    leader_host = None
    leader_port = None

    # Ping replicas to find one with highest id
    for id in sorted(replica_ids, reverse=True):
        hostname = replica_data[str(id)]["hostname"]
        port = replica_data[str(id)]["port"]
        with grpc.insecure_channel(hostname + ":" + port) as channel:
            print(f"Trying ID#{id}")
            stub = order_pb2_grpc.OrderStub(channel)
            try:
                res = stub.Ping(order_pb2.LiveCheck(code=1), timeout=1)
                if res.code == 1:
                    leader_id = id
                    leader_host = hostname
                    leader_port = port
                    print(
                        f"Ping successful, ID#{id}: {leader_host}:{leader_port} selected as leader"
                    )
                    os.environ["ORDER_HOST"] = leader_host
                    os.environ["ORDER_PORT"] = leader_port
                    break
            except:
                dead_replicas.append(id)
                print(f"Ping failed for ID#{id}: {hostname}:{port}")
                continue

    # Inform other alive replicas of the elected leader
    others = [id for id in replica_ids if id not in dead_replicas and id != leader_id]
    for id in others:
        hostname = replica_data[str(id)]["hostname"]
        port = replica_data[str(id)]["port"]
        with grpc.insecure_channel(hostname + ":" + port) as channel:
            stub = order_pb2_grpc.OrderStub(channel)
            try:
                res = stub.SetLeader(
                    order_pb2.LeaderDetails(
                        id=leader_id, hostname=leader_host, port=leader_port
                    ),
                    timeout=1,
                )
            except Exception as e:
                print(f"Failed to inform Replica#{id}")


if __name__ == "__main__":
    # Select order leader from replicas
    elect_leader()

    # Start frontend server
    hostname = gethostbyname(gethostname())
    port = "8080"
    print(f"Frontend service started, host: {hostname}, port: {port}")
    serve(app, port=8080, host="0.0.0.0", threads=10)
