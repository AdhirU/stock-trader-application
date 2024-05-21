from concurrent import futures
from socket import gethostname, gethostbyname
from threading import Lock
import requests
import json

import grpc
import catalog_pb2
import catalog_pb2_grpc

import os

class Catalog(catalog_pb2_grpc.CatalogServicer):
    stocks = {}
    lock = Lock()

    def LookUp(self, request, context):
        name = request.stockName
        # Lock access to shared stocks object when fetching prices
        with self.lock:
            if name not in self.stocks:
                price = -1
                quantity = -1
            else:
                price = self.stocks[name]["price"]
                quantity = self.stocks[name]["quantity"]

        return catalog_pb2.StockDetails(price=price, quantity=quantity)

    def Update(self, request, context):
        name = request.stockName
        N = request.N
        trade_type = request.type
        # Lock access to shared stocks object when fetching prices
        with self.lock:
            if name not in self.stocks or trade_type not in ("buy", "sell"):
                response = -1
            elif trade_type == "buy" and self.stocks[name]["quantity"] < N:
                # Number of stocks requested to be bought more than number available
                response = 0
            else:
                updated_stocks = self.stocks[name].copy()
                # If buy, decrease quantity of stock, else increase quantity
                if trade_type == "buy":
                    updated_stocks["quantity"] -= N
                else:
                    updated_stocks["quantity"] += N
                # Increment volumne of stocks traded
                updated_stocks["volume"] += N

                # Send invalidation request to frontend cache
                if os.getenv("CACHING") == "ON":
                    frontend_host = "http://" + gethostbyname("frontend") + ":8080"
                    r = requests.post(frontend_host + "/cache/" + name).json()
                    if r.get("code") == 1:
                        # Save changes to in memory data
                        self.stocks[name] = updated_stocks
                        # Store updated data in .json storage
                        with open("data.json", "w") as db:
                            json.dump(self.stocks, db, indent=4)

                response = 1

                

        return catalog_pb2.SuccessMessage(message=response)


def serve():
    # Initialize the stock data
    with open("data.json", "r") as db:
        Catalog.stocks = json.load(db)

    # Serve gRPC server
    hostname = gethostbyname(gethostname())
    port = "50015"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    catalog_pb2_grpc.add_CatalogServicer_to_server(Catalog(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print(f"Catalog service started, host: {hostname}, port: {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
