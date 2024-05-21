# Design Document

## Frontend Service Design

- The frontend service runs as a Flask application
- `Flask-Sessions` plugin is used to implement caching for the service. A filesystem implements persistance for the cache and timestamp data.
- The caching is implemented using the LRU (Least Recently Used) policiy. A timestamp marks the time a data item was last accessed, and the least recently accessed item is evicted when a new item arrives and the cache size is more than a pre-determined `CACHE_SIZE` value, which can be provided as an environment variable.
- In addition, when a new order is placed the Catalog service sends an invalidation command that deletes that item from the cache.
- The service first calls the `elect_leader` function to elect a new leader for the order replicas

```
elect_leader()
    Load the replica data from the replica_config.json file and iterate from highest ID to lowest
    For each replica, call Ping to see if it is alive. Exit the loop if a live replica is found
    Collect other replicas (those that are not dead and not leader) into a list and iterate over them
    For each other replica, call SetLeader to provide it with details of the leader replica
```
- Run the Flask application with hardcoded PORT 8080 and 10 worker threads. We are using the production-grade `waitress` library to host the application, with 10 worker threads to handle requests
- The Frontend Service has 4 endpoints:
```
GET /stocks/<stock_name>
    - If caching is ON and the stock is in the cache, load the stock details from cache and return
    - Else query the stock details from the catalog service and store it in the cache. 
    - Returns JSON data with the name, price and quantity of the stock


GET /orders/<order_number>
    - Uses the environment variables to access the leader's host and port information, and queries the leader Order service for details of the order_number
    - If the leader fails, the service calls the elect_leader() function and performs the query again with the new leader. If this fails 3 times, the service returns a 500 code error saying the service is down.

POST /orders
    - Accepts JSON data for a trade order, which has the name, quantity and type of order (buy or sell)
    - Forwards the request to the Order service and re-elects leader if the service does not respond.

POST /cache/<stock_name> 
    - This is called by the Catalog service to invalidate a cache entry when the stock data is updated
```
- Error handling:
    - If the stock is not found a 404 error is returned along with a message
    - If the service times out a 500 error is returned along with a message
    


## Catalog Service Design
- The Catalog service runs as a gRPC application on the PORT 50019. It uses a ThreadPool of 10 maximum working threads to handle concurrent requests.
- The service stores the stock data in a `data.json` file which contains the name, price, quantity (of the stock available) and volume traded for each stock.
- On initialization, the service loads the data from the .json file into memory
- A lock is used to prevent race conditions due to different threads accessing the common stock data at the same time.
- The Catalog service has 2 endpoints:
```
Lookup
    - Fetches the stock's price and quantity if it exists, or returns -1 values if it does not

Update
    - Performs a trade using the stockName, N (quantity of stock) and type (buy or sell) information in the request object
    - If the stock does not exist a value of -1 is returned
    - If the request is to buy but for a quantity greater than that available, a value of 0 is returned
    -  Else, the stock quantity and volume information is modified in memory and loaded to the file in disk. An invalidation request is sent to the frontend's /cache endpoint and a value of 1 is returned.
```

## Order Service Design
- Three replicas of the Order service are created with three different log csv files to store order data.
- The Order service's ID and PORT values are provided as environment variables
- The service also has access to a replica_config.json file that contains information of the other Order replicas and which one is the leader
- On initialization, the service first checks its log data to find the last transaction ID for its order.
- It then queries the leader (whose information is in the config file), providing its last transaction number. If the leader finds that it has more transactions performed, it returns the rest of the transaction data to this replica. The replica then appends its own order_log file with the missing transactions.
- It then starts a gRPC service that listens to PORT given by its port environment variable.
- The Order service has five endpoints:

```
Trade:
    - Listens to trade requests from the Frontend and forwards them to the Catalog to perform an update on the stock information
    - If the catalog returns code -1 the Order service returns a message saying stock is not found, else a message saying insufficient stocks available
    - If the trade order is successfully executed, a lock is obtained before the service updates its order_log file to log the newest trade order.
    - It then propagates this trade order information to other Order replicas who update their own log files.

GetOrder:
    - Reads the order details for a particular order number from the order_log file

Ping:
    - Returns a live message with code 1 if the server is up

SetLeader:
    - Listens to requests from the frontend about which replica was selected as leader
    - The leader's host and port information is stored in the replica_config file so that it can be used in case the service needs to be restarted and obtain missing log information

FetchNewOrders:
    - This is used by the leader server to listen to requests by other replicas that want to obtain missing log data
    - The leader reads the last transaction number available to the replica and iterates through its own order_log file to collect all transactions that happened since the last transaction.
```

## General Architecture
- The three services were containerized into microservices using Docker.
- Docker compose was used to easily build the services. Port forwarding, persistent volumes and environment variables were specified in the compose file. In addition, the dependencies of the services (the three order replicas depend on catalog, and the frontend service depends on the three order services) was also specified.


## AWS

- We are running the application on an AWS EC2 instance of type small.
- The code was copied to the instance using sftp and the python libraries were installed into a virtual environment (read README-instructions-on-how-to-run.md)
- The code runs as Docker containers that are created using docker compose