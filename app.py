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
    # Frankfurter endpoint: EUR base, ZAR symbol — no key needed
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
    return luno, coin_eur, coin_zar, gap, pct

try:
    luno, coin_eur, coin_zar, gap, pct = calculate_gap()
    st.metric("Luno Price (ZAR)", f"ZAR {luno:.2f}")
    st.metric("Coinbase Price (EUR)", f"EUR {coin_eur:.4f}")
    st.metric("Coinbase Equivalent (ZAR)", f"ZAR {coin_zar:.2f}")
    st.metric("Gap (ZAR)", f"ZAR {gap:.2f}", delta=f"{pct:.2f}%")
except Exception as e:
    st.error(f"Error fetching data: {e}")
