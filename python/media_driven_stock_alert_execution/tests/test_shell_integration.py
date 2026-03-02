import os
import sys

# make sure the project root is on sys.path so modules are importable when
# pytest changes the working directory during collection
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)

from shell_integration import detect_commands


def test_detect_simple_buy():
    text = "Buy 100 AAPL at 150"
    cmds = detect_commands(text)
    assert len(cmds) == 1
    c = cmds[0]
    assert c["action"] == "BUY"
    assert c["symbol"] == "AAPL"
    assert c["qty"] == 100
    assert c["price"] == 150.0


def test_detect_market_sell():
    text = "TSLA sell 50 market"
    cmds = detect_commands(text)
    assert len(cmds) == 1
    c = cmds[0]
    assert c["action"] == "SELL"
    assert c["symbol"] == "TSLA"
    assert c["price_type"] == "market"
