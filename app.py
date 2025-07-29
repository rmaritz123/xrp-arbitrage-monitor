import streamlit as st
import requests

st.set_page_config(page_title="XRP Arbitrage Monitor", layout="centered")
st.title("🔍 XRP Arbitrage Monitor")

@st.cache_data(ttl=60)
def get_luno_price():
    resp = requests.get("https://api.mybitx.com/api/1/ticker?pair=XRPZAR")
    return float(resp.json()['ask'])

@st.cache_data(ttl=60)
def get_coinbase_price():
    resp = requests.get("https://api.coinbase.com/v2/prices/XRP-EUR/spot")
    return float(resp.json()['data']['amount'])

@st.cache_data(ttl=60)
def get_exchange_rate():
    resp = requests.get("https://api.frankfurter.dev/v1/latest?base=EUR&symbols=ZAR")
    data = resp.json()
    if 'rates' in data and 'ZAR' in data['rates']:
        return float(data['rates']['ZAR'])
    else:
        raise ValueError(f"Unexpected exchange data: {data}")

def calculate_gap():
    luno = get_luno_price()
    coin_eur = get_coinbase_price()
    eur_to_zar = get_exchange_rate()
    coin_zar = coin_eur * eur_to_zar
    gap = luno - coin_zar
    pct = (gap / coin_zar) * 100
    return luno, coin_eur, coin_zar, eur_to_zar, gap, pct

def estimate_profit():
    EUR_INVEST = 1000
    coin_eur = get_coinbase_price()
    eur_to_zar = get_exchange_rate()
    luno_price = get_luno_price()

    # Coinbase fees: approx 1.5%, Luno fees: 0.1% trading + 0.0001 XRP withdrawal fee
    cb_fee = EUR_INVEST * 0.015
    eur_after_fee = EUR_INVEST - cb_fee

    # XRP purchase on Coinbase
    xrp_bought = eur_after_fee / coin_eur

    # Send XRP to Luno (minimal XRP network fee, already excluded)
    zar_received = xrp_bought * luno_price
    zar_fee = zar_received * 0.001  # Luno trading fee
    zar_final = zar_received - zar_fee

    cost_in_zar = EUR_INVEST * eur_to_zar
    profit = zar_final - cost_in_zar
    profit_pct = (profit / cost_in_zar) * 100
    
    return zar_final, cost_in_zar, profit, profit_pct

try:
    luno, coin_eur, coin_zar, eur_to_zar, gap, pct = calculate_gap()
    zar_final, cost_zar, profit, profit_pct = estimate_profit()

    st.metric("Luno Price (ZAR)", f"ZAR {luno:.2f}")
    st.metric("Coinbase Price (EUR)", f"EUR {coin_eur:.4f}")
    st.metric("Coinbase Equivalent (ZAR)", f"ZAR {coin_zar:.2f}")
    st.metric("Gap (ZAR)", f"ZAR {gap:.2f}", delta=f"{pct:.2f}%")

    st.subheader("💰 Profit/Loss on EUR 1000 XRP Arbitrage")
    st.write(f"**Total received on Luno after fees:** ZAR {zar_final:,.2f}")
    st.write(f"**Total cost in ZAR (EUR 1000):** ZAR {cost_zar:,.2f}")
    st.write(f"**Estimated Profit/Loss:** ZAR {profit:,.2f} ({profit_pct:.2f}%)")

except Exception as e:
    st.error(f"Error fetching data: {e}")
