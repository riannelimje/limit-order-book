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


#  Test 1: No match 

def test_no_match_orders_rest_on_book(lob):
    """
    Buy at 100, sell at 105 — prices don't cross so no match.
    Both orders should rest on their respective sides.
    """
    lob.add_order(make_order("1", Side.BUY, 100.0, 10))
    lob.add_order(make_order("2", Side.SELL, 105.0, 7))

    assert lob.get_best_bid() == 100.0
    assert lob.get_best_ask() == 105.0


#  Test 2: Full match 

def test_full_match_clears_both_sides(lob):
    """
    Sell 5 @ 100, buy 5 @ 105 — prices cross and quantities are equal.
    Both orders fully fill, book should be empty.
    """
    lob.add_order(make_order("S1", Side.SELL, 100.0, 5))
    lob.add_order(make_order("B1", Side.BUY, 105.0, 5))

    assert lob.get_best_bid() is None
    assert lob.get_best_ask() is None


#  Test 3: Partial fill — incoming larger 

def test_partial_fill_incoming_larger(lob):
    """
    Sell 5 @ 100, buy 10 @ 105 — resting sell fully consumed.
    Buy order has 5 remaining and should rest on bid side.
    """
    lob.add_order(make_order("S1", Side.SELL, 100.0, 5))
    lob.add_order(make_order("B1", Side.BUY, 105.0, 10))

    assert lob.get_best_bid() == 105.0  # 5 remaining resting
    assert lob.get_best_ask() is None   # sell fully consumed


#  Test 4: Partial fill — resting larger 

def test_partial_fill_resting_larger(lob):
    """
    Sell 10 @ 100, buy 4 @ 105 — buy fully fills but sell has 6 remaining.
    Ask side should still show 100.
    """
    lob.add_order(make_order("S1", Side.SELL, 100.0, 10))
    lob.add_order(make_order("B1", Side.BUY, 105.0, 4))

    assert lob.get_best_bid() is None   # buy fully consumed
    assert lob.get_best_ask() == 100.0  # 6 remaining resting


#  Test 5: Multiple price levels 

def test_multi_level_fill(lob):
    """
    Two ask levels at 100 and 101.
    Buy for 6 @ 105 — should consume all of 100 (5 units) 
    then 1 unit from 101, leaving 4 at 101.
    """
    lob.add_order(make_order("S1", Side.SELL, 100.0, 5))
    lob.add_order(make_order("S2", Side.SELL, 101.0, 5))
    lob.add_order(make_order("B1", Side.BUY, 105.0, 6))

    assert lob.get_best_ask() == 101.0  # 100 level fully consumed
    assert lob.get_best_bid() is None   # buy fully consumed


#  Test 6: FIFO within price level 

def test_fifo_within_price_level(lob):
    """
    Two sells at same price 100. Buy for 6 — should fill S1 fully (5 units)
    then 1 unit from S2. S2 should have 4 remaining.

    This tests price-time priority — S1 arrived first so fills first.
    If this fails, the deque is not behaving as a queue (FIFO).
    """
    lob.add_order(make_order("S1", Side.SELL, 100.0, 5))
    lob.add_order(make_order("S2", Side.SELL, 100.0, 5))
    lob.add_order(make_order("B1", Side.BUY, 105.0, 6))

    # S1 fully filled, S2 has 4 remaining at 100
    assert lob.get_best_ask() == 100.0

    # verify S2 is still there with correct remaining qty
    remaining = lob.asks[100.0][0]
    assert remaining.order_id == "S2"
    assert remaining.qty == 4


#  Test 7: Order map integrity 

def test_order_map_removes_filled_orders(lob):
    """
    After a full match, filled orders should be removed from order_map.
    order_map should only contain live resting orders.
    """
    lob.add_order(make_order("S1", Side.SELL, 100.0, 5))
    lob.add_order(make_order("B1", Side.BUY, 100.0, 5))

    assert "S1" not in lob.order_map
    assert "B1" not in lob.order_map


def test_order_map_keeps_resting_orders(lob):
    """
    Resting orders (no match) should be in order_map.
    """
    lob.add_order(make_order("1", Side.BUY, 99.0, 10))
    lob.add_order(make_order("2", Side.SELL, 101.0, 5))

    assert "1" in lob.order_map
    assert "2" in lob.order_map


#  Test 8: Empty book edge cases 

def test_empty_book_returns_none(lob):
    """No orders — best bid and ask should be None, not an error."""
    assert lob.get_best_bid() is None
    assert lob.get_best_ask() is None


def test_single_buy_no_asks(lob):
    """Single buy with no sells — should rest, no match attempted."""
    lob.add_order(make_order("B1", Side.BUY, 100.0, 10))

    assert lob.get_best_bid() == 100.0
    assert lob.get_best_ask() is None


def test_single_sell_no_bids(lob):
    """Single sell with no buys — should rest, no match attempted."""
    lob.add_order(make_order("S1", Side.SELL, 100.0, 10))

    assert lob.get_best_bid() is None
    assert lob.get_best_ask() == 100.0

#  Test 9: Multiple orders at same price accumulate in queue 
def test_multiple_bids_same_price_accumulate(lob):
    lob.add_order(make_order("B1", Side.BUY, 100.0, 5))
    lob.add_order(make_order("B2", Side.BUY, 100.0, 7))

    queue = lob.bids[100.0]
    assert len(queue) == 2
    assert queue[0].order_id == "B1"
    assert queue[1].order_id == "B2"