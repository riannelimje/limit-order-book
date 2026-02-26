import matplotlib.pyplot as plt


def _collect_book_depth(book):
    """
    Extract cumulative depth from the order book.

    Returns:
        bid_prices, bid_cum_qty
        ask_prices, ask_cum_qty
    """

    # ---------- ASKS (ascending) ----------
    ask_prices = []
    ask_sizes = []

    for price in book.asks:
        level = book.asks[price]
        total_qty = sum(order.qty for order in level)
        ask_prices.append(price)
        ask_sizes.append(total_qty)

    # cumulative
    ask_cum = []
    running = 0
    for qty in ask_sizes:
        running += qty
        ask_cum.append(running)

    # ---------- BIDS (descending) ----------
    bid_prices = []
    bid_sizes = []

    for price in reversed(book.bids):
        level = book.bids[price]
        total_qty = sum(order.qty for order in level)
        bid_prices.append(price)
        bid_sizes.append(total_qty)

    # cumulative
    bid_cum = []
    running = 0
    for qty in bid_sizes:
        running += qty
        bid_cum.append(running)

    return bid_prices, bid_cum, ask_prices, ask_cum

def plot_depth_chart(book):
    bid_prices, bid_cum, ask_prices, ask_cum = _collect_book_depth(book)

    best_bid = max(bid_prices) if bid_prices else None
    best_ask = min(ask_prices) if ask_prices else None
    mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else None

    plt.figure(figsize=(10, 6))

    # Plot bids (green)
    plt.step(
        bid_prices,
        bid_cum,
        where="post",
        label="Bids",
        linewidth=2
    )

    # Plot asks (red)
    plt.step(
        ask_prices,
        ask_cum,
        where="post",
        label="Asks",
        linewidth=2
    )

    # Fill areas
    plt.fill_between(bid_prices, bid_cum, step="post", alpha=0.3)
    plt.fill_between(ask_prices, ask_cum, step="post", alpha=0.3)

    # Mid price line
    if mid_price:
        plt.axvline(mid_price, linestyle="--", linewidth=1.5, label="Mid Price")

    # Spread shading
    if best_bid and best_ask:
        plt.axvspan(best_bid, best_ask, alpha=0.1)

    plt.title("Limit Order Book Depth", fontsize=14)
    plt.xlabel("Price")
    plt.ylabel("Cumulative Quantity")
    plt.legend()
    plt.grid(alpha=0.2)

    plt.tight_layout()
    plt.show()