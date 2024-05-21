import requests
import argparse
import random
import time


def start_session(addr, p=0.5):
    local_order_info = {}  # Locally stored order information
    stocks = [
        "GameStart",
        "MenhirCo",
        "FishCo",
        "BoarCo",
        "Windmillite",
        "SlimeCo",
        "TerraTop",
        "DuckCo",
        "LaserCo",
        "TimeStop",
    ]
    lookup_times = []
    trade_times = []
    # Execute trade lookup and order requests
    for _ in range(100):
        # We have hardcoded session length to be 20 lookups + optional trades
        with requests.Session() as s:
            stock = random.choice(stocks)
            start = time.time()
            r = s.get(addr + "/stocks/" + stock).json()
            print(r)
            lookup_times.append(time.time() - start)
            data = r.get("data")
            # If server returns error, continue to next lookup
            if not data:
                continue
            quantity = data.get("quantity")
            if quantity > 0 and random.random() < p:
                # Stock, trade type and amount traded are randomly chosen
                trade = random.choice(["buy", "sell"])
                quant = random.randint(1, 100)
                order_data = {"name": stock, "quantity": quant, "type": trade}
                start = time.time()
                r = s.post(
                    addr + "/orders",
                    data=order_data,
                )
                trade_times.append(time.time() - start)
                if r.status_code == 200:
                    r = r.json()
                    print(r)
                    local_order_info[r["data"]["transaction_number"]] = order_data

    # Calculate average lookup and trade times
    print(f"Average lookup time: {sum(lookup_times) / len(lookup_times)}")
    print(f"Average trade time: {sum(trade_times) / len(trade_times)}")
    # Verify orders data with local data
    with requests.Session() as s:
        print("\nVerifying orders...")
        correct_orders = 0
        total_orders = 0
        for order_number, order_data in local_order_info.items():
            r = s.get(addr + "/orders/" + str(order_number)).json()
            print(r)
            response_data = r.get("data")
            if (
                response_data
                and response_data["number"] == order_number
                and response_data["name"] == order_data["name"]
                and response_data["type"] == order_data["type"]
                and response_data["quantity"] == order_data["quantity"]
            ):
                correct_orders += 1
            total_orders += 1
    print(f"{correct_orders}/{total_orders} orders verified to be correct")


if __name__ == "__main__":
    # User must provide two parameters: IP address of server and probability of lookup
    parser = argparse.ArgumentParser(description="Client for REST Service")
    parser.add_argument("ip", type=str, help="Server IP address")
    parser.add_argument("p", type=float, help="Probability of trade")
    args = parser.parse_args()

    # Send requests to server in port 8080
    addr = "http://" + args.ip + ":8080"

    start_session(addr, args.p)
