import pytest
import time
from order_book import LimitOrderBook
from order import Order, Side

@pytest.fixture
def lob():
    """Fresh order book for each test."""
    return LimitOrderBook()

def make_order(order_id, side, price, qty):
    """Helper to reduce boilerplate in every test."""
    return Order(order_id, side, price, qty, int(time.time()))

def test_cancel_existing_order(lob):
    lob.add_order(make_order("B1", Side.BUY, 100.0, 10))

    assert lob.cancel_order("B1") is True
    assert lob.get_best_bid() is None

def test_cancel_middle_order_fifo(lob):
    lob.add_order(make_order("B1", Side.BUY, 100.0, 5))
    lob.add_order(make_order("B2", Side.BUY, 100.0, 5))
    lob.add_order(make_order("B3", Side.BUY, 100.0, 5))

    lob.cancel_order("B2")

    queue = lob.bids[100.0]
    assert len(queue) == 2
    assert queue[0].order_id == "B1"
    assert queue[1].order_id == "B3"

def test_cancel_nonexistent_order(lob):
    assert lob.cancel_order("ghost") is False