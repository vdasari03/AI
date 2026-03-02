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
