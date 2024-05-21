import os
import csv
import json
from concurrent import futures
from socket import gethostname, gethostbyname
from threading import Lock

import grpc
import order_pb2
import order_pb2_grpc
import catalog_pb2
import catalog_pb2_grpc


class Order(order_pb2_grpc.OrderServicer):
    lock = Lock()
    transaction_number = 1

    def Trade(self, request, context):
        # Query catalog to perform update
        catalog_host = os.getenv("CATALOG_HOST", "catalog") + ":50015"
        with grpc.insecure_channel(catalog_host) as channel:
            stub = catalog_pb2_grpc.CatalogStub(channel)
            response = stub.Update(
                catalog_pb2.TradeDetails(
                    stockName=request.stockName, N=request.N, type=request.type
                )
            )
            if response.message != 1:
                if response.message == -1:
                    message = "stock not found"
                else:
                    message = "insufficient stock available"
                return order_pb2.ResponseMessage(
                    code=-1, transactionNumber=-1, message=message
                )
        # Update order log
        with self.lock:
            transaction_number = self.transaction_number
            id = os.getenv("ID")
            with open(f"order_log{id}.csv", "a") as log:
                log.write(
                    f"{transaction_number},{request.stockName},{request.type},{request.N}\n"
                )
            self.transaction_number += 1
        # Propagate order to other replicas
        with open("replica_config.json", "r") as f:
            replica_data = json.load(f)
        for id, replica in replica_data.items():
            host = replica["hostname"]
            port = replica["port"]
            if id != os.getenv("ID"):
                try:
                    with grpc.insecure_channel(host + ":" + port) as channel:
                        stub = order_pb2_grpc.OrderStub(channel)
                        res = stub.PropagateOrder(order_pb2.OrderDetails(orderNumber=transaction_number, 
                                                        stockName=request.stockName, type=request.type, quantity=request.N), timeout=0.5)
                except Exception as e:
                    print(f"Could not propagate order to {host}:{port}")
                    
        
        return order_pb2.ResponseMessage(
            code=1, transactionNumber=transaction_number, message="success"
        )

    def GetOrder(self, request, context):
        id = os.getenv("ID")
        with self.lock:
            with open(f"order_log{id}.csv", "r") as log:
                reader = csv.reader(log)
                for line in reader:
                    if int(line[0]) == request.orderNumber:
                        return order_pb2.OrderDetails(
                            orderNumber=int(line[0]), stockName=line[1], type=line[2], quantity=int(line[3])
                        )
                return order_pb2.OrderDetails(orderNumber=-1, stockName="", type="", quantity=-1)
            
    def Ping(self, request, context):
        if request.code == 1:
            return order_pb2.Success(code=1)
        
    def SetLeader(self, request, context):
        print(f"ID#{os.getenv('ID')} has selected ID#{request.id} as leader")
        with open("replica_config.json", "r") as f:
            replica_data = json.load(f)
            for id in replica_data:
                if int(id) == request.id:
                    replica_data[id]["leader"] = True
                else:
                    replica_data[id]["leader"] = False
        with open("replica_config.json", "w") as f:
            json.dump(replica_data, f, indent=4)
        return order_pb2.Success(code=1)
    
    def PropagateOrder(self, request, context):
        id = os.getenv("ID")
        transaction_number = request.orderNumber
        with self.lock:
            with open(f"order_log{id}.csv", "a") as log:
                log.write(
                    f"{transaction_number},{request.stockName},{request.type},{request.quantity}\n"
                )
            self.transaction_number = max(self.transaction_number, transaction_number) + 1
        return order_pb2.Success(code=1)
    
    def FetchNewOrders(self, request, context):
        id = os.getenv("ID")
        with self.lock:
            if request.orderNumber == self.transaction_number:
                return order_pb2.NewOrders(latestOrder=self.transaction_number, missingOrders="")
            with open(f"order_log{id}.csv", "r") as log:
                reader = csv.reader(log)
                missing_orders = ""
                add_order = False
                for row in reader:
                    if not add_order:
                        id = int(row[0])
                        if id == request.orderNumber:
                            add_order = True
                    else:
                        missing_orders += ",".join(row) + "\n"
            return order_pb2.NewOrders(latestOrder=self.transaction_number, missingOrders=missing_orders)        

def serve():
    # Get last transaction ID
    id = os.getenv("ID")
    if os.path.isfile(f"./order_log{id}.csv"):
        with open(f"order_log{id}.csv", "r") as log:
            last_line = log.readlines()[-1]
            if len(last_line) != 0:
                last_transaction = int(last_line.split(",")[0])
                Order.transaction_number = last_transaction + 1

    # Get leader data
    leader_host = None
    leader_port = None
    with open("replica_config.json", "r") as f:
        replica_data = json.load(f)
    for replica in replica_data.values():
        if replica["leader"]:
            leader_host = replica["hostname"]
            leader_port = replica["port"]

    # Get recent orders from leader if other replicas are up
    if leader_host:
        try:
            with grpc.insecure_channel(leader_host + ":" + leader_port) as channel:
                stub = order_pb2_grpc.OrderStub(channel)
                res = stub.FetchNewOrders(order_pb2.OrderNumber(orderNumber=last_transaction), timeout=0.5)
                if res.latestOrder != Order.transaction_number:
                    print(f"ID#{id} recovering lost log data")
                    with open(f"order_log{id}.csv", "a") as log:
                        log.writelines(res.missingOrders)
        except:
            pass


    # Serve gRPC server
    hostname = gethostbyname(gethostname())
    port = os.getenv("PORT")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderServicer_to_server(Order(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print(f"Order service started, host: {hostname}, port: {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
