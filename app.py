import streamlit as st
import requests

st.set_page_config(page_title="XRP Arbitrage Monitor", layout="centered")
st.title("🔍 XRP Arbitrage Monitor")

@st.cache_data(ttl=60)
def get_luno_price():
    url = "https://api.mybitx.com/api/1/ticker?pair=XRPZAR"
    response = requests.get(url)
    data = response.json()
    return float(data['ask'])

@st.cache_data(ttl=60)
def get_coinbase_price():
    url = "https://api.coinbase.com/v2/prices/XRP-EUR/spot"
    response = requests.get(url)
    data = response.json()
    return float(data['data']['amount'])

@st.cache_data(ttl=60)
def get_exchange_rate():
    url = "https://api.exchangerate.host/latest?base=EUR&symbols=ZAR"
    response = requests.get(url)
    data = response.json()
    return float(data['rates']['ZAR'])

def calculate_gap():
    luno_price = get_luno_price()
    coinbase_price_eur = get_coinbase_price()
    eur_to_zar = get_exchange_rate()
    coinbase_price_zar = coinbase_price_eur * eur_to_zar
    gap = luno_price - coinbase_price_zar
    gap_percent = (gap / coinbase_price_zar) * 100
    return luno_price, coinbase_price_eur, coinbase_price_zar, gap, gap_percent

try:
    luno_price, coinbase_price_eur, coinbase_price_zar, gap, gap_percent = calculate_gap()

    st.metric("Luno Price (ZAR)", f"ZAR {luno_price:.2f}")
    st.metric("Coinbase Price (EUR)", f"EUR {coinbase_price_eur:.4f}")
    st.metric("Coinbase Equivalent (ZAR)", f"ZAR {coinbase_price_zar:.2f}")
    st.metric("Gap (ZAR)", f"ZAR {gap:.2f}", delta=f"{gap_percent:.2f}%")

except Exception as e:
    st.error(f"Error fetching data: {e}")
