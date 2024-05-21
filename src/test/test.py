import argparse
import requests


def test_get(host):
    with requests.Session() as s:
        # Testing incorrect lookup
        r = s.get(host + "/stocks/NomadCo").json()
        print(r)

        code = r.get("error").get("code")
        message = r.get("error").get("message")
        assert code == 404
        print("  >> Correct error code obtained for stock that does not exist:", code)
        assert message == "stock not found"
        print("  >> Correct error message for stock that does not exist: ", message)

        # Testing correct lookup
        r = s.get(host + "/stocks/BoarCo").json()
        print(r)

        name = r.get("data").get("name")
        assert name == "BoarCo"
        print("  >> Correct name obtained from /stock/BoarCo:", name)

        price = r.get("data").get("price")
        assert price
        print("  >> Correct parameter returned: price")

        quantity = r.get("data").get("quantity")
        assert quantity
        print("  >> Correct parameter returned: quantity")

        # Testing incorrect buy
        data = {"name": "BoarCo", "quantity": quantity + 5, "type": "buy"}
        r = s.post(host + "/orders", data=data).json()
        print(r)

        code = r.get("error").get("code")
        message = r.get("error").get("message")
        assert int(code) == 404
        print("  >> Correct unsuccessful buy due to insufficient stock")
        print(message)
        assert message == "insufficient stock available"
        print("  >> Correct error message due to insufficient stock available")

        # Testing correct buy
        data = {"name": "BoarCo", "quantity": 1, "type": "buy"}

        r = s.post(host + "/orders", data=data).json()
        print(r)

        data = r.get("data")
        assert data
        print("  >> Correct response for successful buy")
        tran_id_1 = r.get("data").get("transaction_number")
        assert type(tran_id_1) == int
        print("  >> Correct return type for transaction id")

        # Testing successive buy and transaction ID
        data = {"name": "BoarCo", "quantity": 1, "type": "buy"}

        r = s.post(host + "/orders", data=data).json()
        print(r)
        tran_id_2 = r.get("data").get("transaction_number")
        assert tran_id_1 + 1 == tran_id_2
        print("  >> Correct increment of transaction id after successive transactions")

        # Testing change in quantity
        r = s.get(host + "/stocks/BoarCo").json()
        print(r)

        quantity_2 = r.get("data").get("quantity")
        assert quantity  == quantity_2
        print("  >> Correct decreases in quantity after two buys")

        print("\n\nAll test passed\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Testing the services")
    parser.add_argument("ip", type=str, help="Server IP address")
    args = parser.parse_args()

    host = "http://" + args.ip + ":8080"

    test_get(host)
