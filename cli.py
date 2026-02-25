from order_book import LimitOrderBook
from order import Order, Side
import time

def run_cli():
    book = LimitOrderBook()

    print("Simple Order Book CLI")
    print("Commands: BUY price qty | SELL price qty | CANCEL id | BOOK | EXIT")

    order_counter = 0

    while True:
        cmd = input(">>> ").strip().split()

        if not cmd:
            continue

        action = cmd[0].upper()

        try:
            if action in ("BUY", "SELL"):
                price = float(cmd[1])
                qty = int(cmd[2])

                order = Order(
                    order_id=str(order_counter),
                    side=Side.BUY if action == "BUY" else Side.SELL,
                    price=price,
                    qty=qty,
                    timestamp=time.time(),
                )

                book.add_order(order)
                print(f"Submitted order id={order_counter}")
                order_counter += 1

            elif action == "CANCEL":
                oid = cmd[1]
                success = book.cancel_order(oid)
                print("Cancelled" if success else "Order not found")

            elif action == "BOOK":
                print_book(book)

            elif action == "EXIT":
                break

            else:
                print("Unknown command")

        except Exception as e:
            print("Error:", e)


def print_book(book):
    print("\n=== ORDER BOOK ===")

    print("\nASKS:")
    for price in book.asks:
        level = book.asks[price]
        total = sum(o.qty for o in level)
        print(f"{price}: {total}")

    print("\nBIDS:")
    for price in reversed(book.bids):
        level = book.bids[price]
        total = sum(o.qty for o in level)
        print(f"{price}: {total}")

    print("==================\n")


if __name__ == "__main__":
    run_cli()