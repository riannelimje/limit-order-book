from order_book import LimitOrderBook
from order import Order, Side
from visualisation.depth_chart import plot_depth_chart


def build_sample_book():
    book = LimitOrderBook()

    # sample bids
    book.add_order(Order("1", Side.BUY, 100, 5, 1))
    book.add_order(Order("2", Side.BUY, 99, 7, 2))
    book.add_order(Order("3", Side.BUY, 98, 10, 3))

    # sample asks
    book.add_order(Order("4", Side.SELL, 101, 6, 4))
    book.add_order(Order("5", Side.SELL, 102, 8, 5))
    book.add_order(Order("6", Side.SELL, 103, 12, 6))

    return book


if __name__ == "__main__":
    book = build_sample_book()
    plot_depth_chart(book)