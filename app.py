import streamlit as st
import plotly.graph_objects as go
import requests
import pandas as pd
import time

st.set_page_config(
    page_title="KSE Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1e2130;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("⚙️ Settings")
symbol = st.sidebar.text_input("Stock Symbol", value="ATRL").upper()
refresh_rate = st.sidebar.slider("Refresh every (seconds)", 1, 10, 2)
chart_type = st.sidebar.selectbox("Chart Type", ["Line", "Candlestick", "Area"])

st.title(f"📈 {symbol} — Live Stock Dashboard")

@st.cache_data(ttl=1)
def fetch_data(symbol):
    url = f"https://www.khistocks.com/company/getintra/{symbol}"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        df = pd.DataFrame(data)
        df['last_trade_price'] = pd.to_numeric(df['last_trade_price'])
        df['last_trade_volume'] = pd.to_numeric(df['last_trade_volume'])
        df['total_traded_volume'] = pd.to_numeric(df['total_traded_volume'])
        df['high_price'] = pd.to_numeric(df['high_price'])
        df['low_price'] = pd.to_numeric(df['low_price'])
        df['day_open_price'] = pd.to_numeric(df['day_open_price'])
        df['last_day_close_price'] = pd.to_numeric(df['last_day_close_price'])
        df['net_change'] = pd.to_numeric(df['net_change'])
        return df
    except Exception as e:
        return None

placeholder = st.empty()

while True:
    df = fetch_data(symbol)

    if df is None:
        st.error("❌ Failed to fetch data. Check symbol or connection.")
        break

    latest = df.iloc[0]
    price = latest['last_trade_price']
    change = latest['net_change']

    with placeholder.container():

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("💰 Last Price", f"{price:.2f}")
        c2.metric("📊 Change", f"{change:.2f}", delta=f"{change:.2f}")
        c3.metric("🔼 High", f"{latest['high_price']:.2f}")
        c4.metric("🔽 Low", f"{latest['low_price']:.2f}")
        c5.metric("📂 Open", f"{latest['day_open_price']:.2f}")
        c6.metric("📅 Prev Close", f"{latest['last_day_close_price']:.2f}")

        st.divider()

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📉 Price Chart")
            fig = go.Figure()

            if chart_type == "Line":
                fig.add_trace(go.Scatter(
                    x=df['last_trade_time'],
                    y=df['last_trade_price'],
                    mode='lines',
                    line=dict(color='#00d4ff', width=2),
                    name='Price'
                ))
            elif chart_type == "Area":
                fig.add_trace(go.Scatter(
                    x=df['last_trade_time'],
                    y=df['last_trade_price'],
                    fill='tozeroy',
                    fillcolor='rgba(0,212,255,0.1)',
                    line=dict(color='#00d4ff', width=2),
                    name='Price'
                ))
            elif chart_type == "Candlestick":
                fig.add_trace(go.Candlestick(
                    x=df['last_trade_time'],
                    open=df['day_open_price'],
                    high=df['high_price'],
                    low=df['low_price'],
                    close=df['last_trade_price'],
                    name='OHLC'
                ))

            fig.update_layout(
                paper_bgcolor='#0e1117',
                plot_bgcolor='#0e1117',
                font=dict(color='white'),
                xaxis=dict(showgrid=False, color='white'),
                yaxis=dict(showgrid=True, gridcolor='#2a2a2a', color='white'),
                margin=dict(l=10, r=10, t=10, b=10),
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📦 Volume Chart")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df['last_trade_time'],
                y=df['last_trade_volume'],
                marker_color='#7b61ff',
                name='Volume'
            ))
            fig2.update_layout(
                paper_bgcolor='#0e1117',
                plot_bgcolor='#0e1117',
                font=dict(color='white'),
                xaxis=dict(showgrid=False, color='white'),
                yaxis=dict(showgrid=True, gridcolor='#2a2a2a', color='white'),
                margin=dict(l=10, r=10, t=10, b=10),
                height=400,
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("🗂️ Recent Trades")
        table_df = df[['last_trade_time', 'last_trade_price',
                        'last_trade_volume', 'bid_price',
                        'ask_price', 'total_traded_volume']].head(10)
        table_df.columns = ['Time', 'Price', 'Volume', 'Bid', 'Ask', 'Total Volume']
        st.dataframe(table_df, use_container_width=True, hide_index=True)

        st.caption(f"🔄 Last updated: {latest['last_trade_time']} | Refreshing every {refresh_rate}s")

    time.sleep(refresh_rate)
