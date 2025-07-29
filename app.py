import streamlit as st
import requests

st.set_page_config(page_title="Crypto Arbitrage Monitor", layout="wide")
st.title("🔍 Luno vs Coinbase Arbitrage (EUR → ZAR)")

COINS = ["BTC", "ETH", "XRP", "LTC", "BCH", "USDC", "UNI", "LINK", "SOL"]

@st.cache_data(ttl=60)
def get_price(exchange: str, coin: str):
    if exchange == "luno":
        url = f"https://api.mybitx.com/api/1/ticker?pair={coin}ZAR"
        resp = requests.get(url)
        return float(resp.json()["ask"])
    elif exchange == "coinbase":
        url = f"https://api.coinbase.com/v2/prices/{coin}-EUR/spot"
        resp = requests.get(url)
        return float(resp.json()["data"]["amount"])
    else:
        raise ValueError("Unknown exchange")

@st.cache_data(ttl=60)
def get_fx():
    resp = requests.get("https://api.frankfurter.dev/v1/latest?base=EUR&symbols=ZAR")
    data = resp.json()
    return float(data["rates"]["ZAR"]) if "rates" in data and "ZAR" in data["rates"] else None

def simulate(coin: str, invest_eur=1000.0):
    eur_to_zar = get_fx()
    buy_price = get_price("coinbase", coin)
    sell_price = get_price("luno", coin)

    cb_fee = invest_eur * 0.015
    eur_after = invest_eur - cb_fee
    amount_coin = eur_after / buy_price

    zar_received = amount_coin * sell_price
    zar_fee = zar_received * 0.001
    net_zar = zar_received - zar_fee

    cost_zar = invest_eur * eur_to_zar
    profit = net_zar - cost_zar
    pct = (profit / cost_zar) * 100

    return {
        "Coin": coin,
        "Buy EUR price": f"€{buy_price:.2f}",
        "Sell ZAR price": f"R {sell_price:.2f}",
        "Cost in ZAR": f"R {cost_zar:.2f}",
        "Received in ZAR": f"R {net_zar:.2f}",
        "Profit/Loss": f"R {profit:.2f}",
        "Profit %": f"{pct:.2f}%"
    }

fx = get_fx()
if fx is None:
    st.error("FX rate error")
else:
    rows = [simulate(c) for c in COINS]
    st.table(rows)
