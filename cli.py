from order_book import LimitOrderBook
from order import Order, Side
import time

# Simple ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

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


def print_book(book, depth=5):
    print("\n================ ORDER BOOK ================\n")

    # --- TAPE SECTION ---
    print("Recent Trades:")
    if getattr(book, "trade_history", None):
        for price, qty in book.trade_history[-5:]:
            print(f"  [TAPE] {qty} @ {price:.2f}")
    else:
        print("  No trades yet.")
    print("\n--------------------------------------------\n")

    # Collect asks (ascending)
    ask_levels = []
    for price in book.asks:
        level = book.asks[price]

        total_qty = sum(order.qty for order in level)  
        order_count = len(level)

        ask_levels.append((price, total_qty, order_count))

    # Collect bids (descending)
    bid_levels = []
    for price in reversed(book.bids):
        level = book.bids[price]

        total_qty = sum(order.qty for order in level)  
        order_count = len(level)

        bid_levels.append((price, total_qty, order_count))

    ask_levels = ask_levels[:depth]
    bid_levels = bid_levels[:depth]

    # Print asks
    print("        ASK SIDE")
    print(" Price      Size    Orders    CumSize")
    print("------------------------------------------------")

    cumulative = 0
    for price, qty, count in ask_levels:
        cumulative += qty
        print(
            f"{RED}{price:>7.2f} {qty:>10} {count:>9} {cumulative:>10}{RESET}"
        )

    print("------------------------------------------------")

    # Print bids
    cumulative = 0
    for price, qty, count in bid_levels:
        cumulative += qty
        print(
            f"{GREEN}{price:>7.2f} {qty:>10} {count:>9} {cumulative:>10}{RESET}"
        )

    print("------------------------------------------------")

    # Top of Book
    best_bid = None
    best_ask = None

    if book.bids:
        best_bid_price = book.bids.peekitem(-1)[0]
        best_bid_qty = sum(
            order.qty for order in book.bids[best_bid_price]
        )  
        best_bid = (best_bid_price, best_bid_qty)

    if book.asks:
        best_ask_price = book.asks.peekitem(0)[0]
        best_ask_qty = sum(
            order.qty for order in book.asks[best_ask_price]
        )  
        best_ask = (best_ask_price, best_ask_qty)

    print("\nTop of Book:")
    print(
        f"Best Bid: {GREEN}{best_bid[0]:.2f} ({best_bid[1]}){RESET}"
        if best_bid
        else "Best Bid: None"
    )
    print(
        f"Best Ask: {RED}{best_ask[0]:.2f} ({best_ask[1]}){RESET}"
        if best_ask
        else "Best Ask: None"
    )

    if best_bid and best_ask:
        spread = best_ask[0] - best_bid[0]
        print(f"Spread:   {spread:.2f}")

    print("\n============================================\n")


if __name__ == "__main__":
    run_cli()