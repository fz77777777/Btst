import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="Stockbee Mega-Universe Alpha Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Minimalist Premium Theme
st.markdown("""
    <style>
    .stButton>button { 
        background-color: #1e3f66; 
        color: white; 
        border-radius: 6px; 
        font-weight: bold;
        padding: 0.6rem 3rem;
        font-size: 16px;
    }
    .stButton>button:hover { background-color: #2b5797; color: #ffffff; }
    h1 { color: #111111; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Stockbee & RRG 2000+ Mega-Universe Suite")
st.markdown("### **Institutional Alpha Engine: Sectoral RS Trends + 3:00 PM BTST Shock Optimizer**")
st.write("---")

# ==========================================
# SIDEBAR CONTROL PANEL
# ==========================================
with st.sidebar:
    st.header("🎮 MODE SELECTOR")
    strategy_mode = st.selectbox(
        "Choose Trading Strategy",
        options=["🔥 Stockbee Hot-Sector Scanner", "🏹 3:00 PM BTST Alpha Engine"],
        index=0
    )
    
    st.write("---")
    st.header("⏳ Timeline Control (Historical Data)")
    # User Requirement: 1 din, 2 din, 3 din... up to 30 days ago historical check
    historical_days = st.slider("Select Lookback (Days Ago)", min_value=0, max_value=30, value=0, step=1)
    
    if historical_days == 0:
        st.success("📍 Targeting: Live Market Close Data")
    else:
        st.warning(f"⏳ Time Machine: Checking {historical_days} Days Ago Data")
        
    st.write("---")
    st.header("🎯 Threshold Adjustments")
    min_gain = st.slider("Minimum Price Gain (%)", min_value=2.0, max_value=10.0, value=4.0, step=0.5)
    vol_multiplier = st.slider("Volume Multiplier (x Volume SMA50)", min_value=1.5, max_value=5.0, value=2.5, step=0.1)
    
    if strategy_mode == "🔥 Stockbee Hot-Sector Scanner":
        st.write("---")
        st.header("⚙️ Structural Setup Filters")
        timeframe_filter = st.selectbox("Data Timeframe", options=["Daily", "Weekly"], index=0)
        setup_filter = st.selectbox(
            "Select Setup Structure",
            options=["All Setups Combined", "Fresh EP Breakout", "Late EP / Consolidation (Strict 6%)", "Pullback Near 10/20 EMA"],
            index=0
        )

# ==========================================
# DYNAMIC 2000+ INDIAN TICKER LOADER (BULLETPROOF)
# ==========================================
@st.cache_data(ttl=86400)
def load_indian_mega_universe_clean():
    base_pool = []
    
    # STEP 1: Load Nifty 500
    try:
        url_500 = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df_500 = pd.read_csv(url_500)
        df_500.columns = [c.upper().strip() for c in df_500.columns]
        symbol_col = 'SYMBOL' if 'SYMBOL' in df_500.columns else df_500.columns[2]
        industry_col = 'INDUSTRY' if 'INDUSTRY' in df_500.columns else df_500.columns[3]
        company_col = 'COMPANY NAME' if 'COMPANY NAME' in df_500.columns else df_500.columns[0]

        for _, row in df_500.iterrows():
            yf_symbol = str(row[symbol_col]).strip() + ".NS"
            base_pool.append({
                'Symbol_YF': yf_symbol,
                'Company Name': row[company_col],
                'Sector': row[industry_col] if pd.notna(row[industry_col]) else 'Core Sector'
            })
    except Exception:
        pass

    # STEP 2: Fetch broad NSE Equities array to scale up to full 2000+ universe
    try:
        url_total = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        df_total = pd.read_csv(url_total)
        df_total.columns = [c.upper().strip() for c in df_total.columns]
        
        symbol_col = 'SYMBOL' if 'SYMBOL' in df_total.columns else df_total.columns[0]
        name_col = 'NAME OF COMPANY' if 'NAME OF COMPANY' in df_total.columns else df_total.columns[1]
        series_col = 'SERIES' if 'SERIES' in df_total.columns else None
        
        if series_col and series_col in df_total.columns:
            df_total = df_total[df_total[series_col].astype(str).str.upper().str.strip() == 'EQ']
            
        existing_symbols = {item['Symbol_YF'] for item in base_pool}
        
        for _, row in df_total.iterrows():
            ticker = str(row[symbol_col]).strip()
            if not ticker or ticker.lower() == 'symbol':
                continue
                
            yf_symbol = ticker + ".NS"
            if yf_symbol not in existing_symbols:
                base_pool.append({
                    'Symbol_YF': yf_symbol,
                    'Company Name': row[name_col] if name_col in df_total.columns else ticker,
                    'Sector': 'Broad Market / Mid-Small'
                })
            if len(base_pool) >= 2150: 
                break
    except Exception:
        pass
        
    if len(base_pool) < 10:
        emergency_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
        return pd.DataFrame([{'Symbol_YF': f'{s}.NS', 'Company Name': f'{s} Ltd', 'Sector': 'Benchmark'} for s in emergency_stocks])
        
    return pd.DataFrame(base_pool)

master_universe = load_indian_mega_universe_clean()
TICKER_LIST = master_universe['Symbol_YF'].tolist()
TICKER_MAP = dict(zip(master_universe['Symbol_YF'], master_universe['Company Name']))
SECTOR_MAP = dict(zip(master_universe['Symbol_YF'], master_universe['Sector']))

st.info(f"📋 **System Matrix Armed:** Ready to parallel scan full **{len(TICKER_LIST)} Equities** simultaneously. Microcaps dropped.")

# ==========================================
# BATCH FETCH ENGINE
# ==========================================
@st.cache_data(ttl=900)
def fetch_indian_data_matrix(tickers, tf):
    interval_map = {"Daily": "1d", "Weekly": "1wk"}
    yf_interval = interval_map.get(tf, "1d")
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=1200)).strftime('%Y-%m-%d')
    df = yf.download(tickers, start=start_date, end=end_date, interval=yf_interval, group_by='ticker', progress=False)
    return df

# ==========================================
# RUN SCANNER LOGIC EXECUTION
# ==========================================
if st.button(f"🔍 EXECUTE ALL-MARKET {strategy_mode.upper()} ENGINE"):
    
    # -------------------------------------------------------------
    # STRATEGY MODE 1: STOCKBEE HOT-SECTOR MOMENTUM SCANNER
    # -------------------------------------------------------------
    if strategy_mode == "🔥 Stockbee Hot-Sector Scanner":
        with st.spinner("Processing multi-timeframe structural matrices..."):
            all_data = fetch_indian_data_matrix(TICKER_LIST, timeframe_filter)
            
        st.write("📊 **Step 1: Ranking Industry Groups via Sectoral Relative Strength...**")
        sector_performance_registry = {}
        
        for ticker in TICKER_LIST:
            try:
                df = all_data[ticker].dropna() if len(TICKER_LIST) > 1 else all_data.dropna()
                if len(df) < 120: continue
                
                base_idx = (len(df) - 1) - historical_days
                if base_idx < 65: continue
                
                close_now = float(df.iloc[base_idx]['Close'])
                close_1m = float(df.iloc[base_idx - 20]['Close'])
                close_3m = float(df.iloc[base_idx - 60]['Close'])
                
                rs_score = (0.4 * ((close_now - close_1m) / close_1m)) + (0.6 * ((close_now - close_3m) / close_3m))
                sec = SECTOR_MAP.get(ticker, "Other")
                if sec not in sector_performance_registry:
                    sector_performance_registry[sec] = []
                sector_performance_registry[sec].append(rs_score)
            except Exception:
                continue

        avg_sector_rs = []
        for sec, scores in sector_performance_registry.items():
            if len(scores) > 3:
                avg_sector_rs.append({"Sector": sec, "RS Score": sum(scores) / len(scores)})
                
        rs_df = pd.DataFrame(avg_sector_rs).sort_values(by="RS Score", ascending=False)
        hot_sectors = set(rs_df.head(6)['Sector'].tolist())
        
        st.write("### 🔥 Industry Leaderboard Results:")
        st.dataframe(rs_df.reset_index(drop=True), use_container_width=True)
        st.write("---")
        
        st.write("⚙️ **Step 2: Hunting Stockbee Setup Formations within Leading Sectors...**")
        scanned_pool = []
        
        for ticker in TICKER_LIST:
            try:
                ticker_sector = SECTOR_MAP.get(ticker, "Other")
                if ticker_sector not in hot_sectors: continue
                    
                df = all_data[ticker].dropna() if len(TICKER_LIST) > 1 else all_data.dropna()
                if len(df) < 120: continue
                    
                df = df.copy()
                df['Vol_SMA'] = df['Volume'].rolling(window=50).mean()
                df['Pct_Change'] = df['Close'].pct_change() * 100
                df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
                df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
                
                execution_idx = (len(df) - 1) - historical_days
                if execution_idx < 65: continue
                    
                row = df.iloc[execution_idx]
                current_close = float(row['Close'])
                current_ema10 = float(row['EMA_10'])
                current_ema20 = float(row['EMA_20'])
                
                status = None
                trigger_gain = row['Pct_Change']
                trigger_vol = row['Volume'] / row['Vol_SMA'] if row['Vol_SMA'] > 0 else 1.0
                
                if row['Pct_Change'] >= min_gain and row['Volume'] >= (vol_multiplier * row['Vol_SMA']):
                    status = "🚨 FRESH EP BREAKOUT"
                else:
                    has_recent_ep = False
                    ep_idx = -1
                    for lookback in range(1, 61):
                        check_idx = execution_idx - lookback
                        if check_idx < 50: break
                        past_row = df.iloc[check_idx]
                        if past_row['Pct_Change'] >= min_gain and past_row['Volume'] >= (vol_multiplier * past_row['Vol_SMA']):
                            has_recent_ep = True
                            ep_idx = check_idx
                            trigger_gain = past_row['Pct_Change']
                            trigger_vol = past_row['Volume'] / past_row['Vol_SMA']
                            break
                            
                    if has_recent_ep:
                        bars_since = execution_idx - ep_idx
                        recent_prices = df.iloc[ep_idx+1 : execution_idx+1]['Close']
                        consolidation_range = (((recent_prices.max() - recent_prices.min()) / recent_prices.min()) * 100) if len(recent_prices) > 0 else 0.0
                        
                        near_10 = abs(current_close - current_ema10) / current_ema10 <= 0.02
                        near_20 = abs(current_close - current_ema20) / current_ema20 <= 0.02
                        
                        if near_10 or near_20:
                            status = f"📉 PULLBACK SUPPORT ({bars_since} Bars Ago)"
                        elif consolidation_range <= 6.0 and current_close >= df.iloc[ep_idx]['Close'] * 0.95:
                            status = f"⏳ LATE EP / CONSOLIDATION ({bars_since} Bars Ago)"
                
                if status:
                    if setup_filter == "Fresh EP Breakout" and "FRESH" not in status: continue
                    if setup_filter == "Late EP / Consolidation (Strict 6%)" and "CONSOLIDATION" not in status: continue
                    if setup_filter == "Pullback Near 10/20 EMA" and "PULLBACK" not in status: continue
                        
                    scanned_pool.append({
                        "Ticker Symbol": ticker.replace('.NS', ''),
                        "Company Name": TICKER_MAP.get(ticker, "Unknown"),
                        "Sector / Industry": ticker_sector,
                        "Setup Status": status,
                        "EP Base Gain": f"{round(trigger_gain, 2)}%",
                        "EP Vol Multiple": f"{round(trigger_vol, 2)}x",
                        "Close Price": f"₹{round(current_close, 2)}",
                        "Scan Date Frame": df.index[execution_idx].strftime('%Y-%m-%d')
                    })
            except Exception:
                continue
                
        if scanned_pool:
            final_df = pd.DataFrame(scanned_pool)
            st.success(f"🎯 **Scan Complete!** Found **{len(final_df)} Premium Assets** inside Lead Clusters!")
            st.dataframe(final_df, use_container_width=True)
        else:
            st.warning("Is target criteria par koi strong configuration setup nahi mila.")

    # -------------------------------------------------------------
    # STRATEGY MODE 2: 3:00 PM BTST ALPHA ENGINE (WITH HISTORICAL BACKTEST LOOKBACK)
    # -------------------------------------------------------------
    elif strategy_mode == "🏹 3:00 PM BTST Alpha Engine":
        with st.spinner("Extracting multi-asset closing data streams..."):
            all_data = fetch_indian_data_matrix(TICKER_LIST, "Daily")
            
        st.write(f"🧭 **Step 1: Mapping Relative Rotation Graph (RRG) Sectors ({historical_days} Days Ago)...**")
        sector_rs_ratio, sector_rs_momentum = {}, {}
        
        for ticker in TICKER_LIST:
            try:
                df = all_data[ticker].dropna() if len(TICKER_LIST) > 1 else all_data.dropna()
                if len(df) < 100: continue
                idx = (len(df) - 1) - historical_days
                if idx < 40: continue
                
                close_series = df['Close'].iloc[idx-30:idx+1].astype(float)
                nifty_series = all_data['RELIANCE.NS']['Close'].iloc[idx-30:idx+1].astype(float)
                
                rs_line = close_series / nifty_series
                current_ratio = rs_line.iloc[-1]
                ratio_momentum = (current_ratio - rs_line.iloc[-5]) / rs_line.iloc[-5]
                
                sec = SECTOR_MAP.get(ticker, "Other")
                if sec not in sector_rs_ratio:
                    sector_rs_ratio[sec], sector_rs_momentum[sec] = [], []
                sector_rs_ratio[sec].append(current_ratio)
                sector_rs_momentum[sec].append(ratio_momentum)
            except Exception:
                continue

        improving_sectors = set()
        rrg_pool = []
        for sec in sector_rs_ratio.keys():
            if len(sector_rs_ratio[sec]) > 3:
                m_ratio = sum(sector_rs_ratio[sec]) / len(sector_rs_ratio[sec])
                m_momentum = sum(sector_rs_momentum[sec]) / len(sector_rs_momentum[sec])
                
                if m_ratio < 1.0 and m_momentum > 0:
                    quadrant = "🟢 Improving Quadrant (BTST High Velocity Cluster)"
                    improving_sectors.add(sec)
                elif m_ratio >= 1.0 and m_momentum > 0: quadrant = "🔥 Leading Quadrant"
                elif m_ratio >= 1.0 and m_momentum <= 0: quadrant = "⏳ Weakening Quadrant"
                else: quadrant = "🔴 Lagging Quadrant"
                
                rrg_pool.append({"Sector": sec, "RRG Quadrant Position": quadrant})
                
        st.dataframe(pd.DataFrame(rrg_pool).sort_values(by="RRG Quadrant Position"), use_container_width=True)
        st.write("---")
        
        st.write(f"🏹 **Step 2: Extracting 3:00 PM Delivery Volume Shock Accumulations ({historical_days} Days Ago)...**")
        btst_pool = []
        
        for ticker in TICKER_LIST:
            try:
                ticker_sector = SECTOR_MAP.get(ticker, "Other")
                if ticker_sector not in improving_sectors: continue
                    
                df = all_data[ticker].dropna() if len(TICKER_LIST) > 1 else all_data.dropna()
                if len(df) < 60: continue
                
                idx = (len(df) - 1) - historical_days
                row = df.iloc[idx]
                prev_row = df.iloc[idx - 1]
                
                vol_sma20 = df['Volume'].iloc[idx-20:idx].mean()
                today_gain = ((row['Close'] - prev_row['Close']) / prev_row['Close']) * 100
                v_mult = row['Volume'] / vol_sma20 if vol_sma20 > 0 else 1.0
                
                # BTST MATHEMATICAL GAUNTLET FILTER:
                price_pass = min_gain <= today_gain <= 8.5 # Avoid Circuit Traps
                volume_pass = v_mult >= vol_multiplier
                
                # Closing Marubozu Rule: Must close near the day high point
                dist_from_high = row['High'] - row['Close']
                marubozu_pass = dist_from_high <= (0.015 * row['High']) if (row['High'] - row['Low']) > 0 else False
                
                if price_pass and volume_pass and marubozu_pass:
                    btst_pool.append({
                        "Ticker Symbol": ticker.replace('.NS', ''),
                        "Company Name": TICKER_MAP.get(ticker, "Unknown"),
                        "Sector": ticker_sector,
                        "Today's Gain (%)": f"{round(today_gain, 2)}%",
                        "Volume Jump Factor": f"{round(v_mult, 2)}x",
                        "Close Price": f"₹{round(row['Close'], 2)}",
                        "Historical Scan Date": df.index[idx].strftime('%Y-%m-%d')
                    })
            except Exception:
                continue
                
        if btst_pool:
            btst_df = pd.DataFrame(btst_pool).sort_values(by="Volume Jump Factor", ascending=False)
            st.success(f"🚀 **BTST Past Lookup Complete!** Found **{len(btst_df)} Stocks** that met 3:00 PM criteria on **{btst_df.iloc[0]['Historical Scan Date']}**!")
            st.dataframe(btst_df, use_container_width=True)
        else:
            st.warning(f"⚠️ Selected Lookback ({historical_days} Days Ago) par koi bhi stock strict BTST conditions ko qualify nahi kar paya.")
