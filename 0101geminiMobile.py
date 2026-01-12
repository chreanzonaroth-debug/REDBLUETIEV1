import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- ១. UI & MOBILE OPTIMIZED CSS ---
st.set_page_config(page_title="AI Guardian Pro V56.6 Mobile", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* ប៊ូតុងបញ្ជា ៣ ក្នុង ១ ជួរ */
    div[data-testid="stHorizontalBlock"] > div { padding: 2px !important; }
    div.stButton > button {
        width: 100%; height: 60px; font-size: 16px !important;
        font-weight: bold !important; border-radius: 12px !important;
    }
    
    /* Decision Banner */
    .decision-container { padding: 20px; border-radius: 20px; text-align: center; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1); }
    .attack-mode { background: linear-gradient(135deg, #00c853, #004d40); border: 2px solid #00ff00; }
    .dragon-mode { background: linear-gradient(135deg, #d50000, #b71c1c); border: 2px solid #ff0000; }
    .wait-mode { background: #111; border: 1px solid #333; }
    
    /* Risk Monitor Box (Step Loss & Max Error) */
    .risk-monitor-container {
        display: flex; justify-content: space-around;
        background: #0f0f0f; border: 1px solid #222;
        padding: 10px; border-radius: 15px; margin-bottom: 15px;
    }
    .risk-item { text-align: center; }
    .risk-label { font-size: 10px; color: #888; text-transform: uppercase; }
    .risk-value { font-size: 24px; font-weight: bold; }

    /* Grid យុទ្ធសាស្ត្រ */
    .strat-card { 
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); 
        border-radius: 10px; padding: 8px; text-align: center; margin-bottom: 5px;
    }
    .active-card { border: 1px solid #00ff00 !important; background: rgba(0, 255, 0, 0.08) !important; }
    .strat-name { font-size: 10px; color: #bbb; }
    .strat-guess { font-size: 24px; font-weight: 900; }
    
    /* គ្រាប់លទ្ធផល */
    .circle-p { height: 26px; width: 26px; background: #2979ff; border-radius: 50%; display: inline-block; color: white; text-align: center; line-height: 26px; font-size: 10px; margin: 1px; font-weight: bold; }
    .circle-b { height: 26px; width: 26px; background: #ff1744; border-radius: 50%; display: inline-block; color: white; text-align: center; line-height: 26px; font-size: 10px; margin: 1px; font-weight: bold; }
    .circle-win { height: 24px; width: 24px; background: #00c853; border-radius: 50%; display: inline-block; color: white; text-align: center; line-height: 24px; font-size: 10px; margin: 1px; border: 1px solid #00ff00; }
    .circle-loss { height: 24px; width: 24px; background: #d50000; border-radius: 50%; display: inline-block; color: white; text-align: center; line-height: 24px; font-size: 10px; margin: 1px; border: 1px solid #ff1744; }
    </style>
    """, unsafe_allow_html=True)

# --- ២. CORE ENGINE ---
DB_FILE = "ai_master_database_v55.csv"
if 'history' not in st.session_state:
    if os.path.exists(DB_FILE): st.session_state.history = pd.read_csv(DB_FILE)['res'].tolist()
    else: st.session_state.history = []
    st.session_state.prediction_logs, st.session_state.current_step, st.session_state.max_step = [], 0, 0
    st.session_state.strat_stats = {f"{i+1}": {"wins": 0, "losses": 0, "recent": [], "cur_err": 0, "max_err": 0} for i in range(9)}

def process_single_step(res):
    res = res.upper()
    if res not in ['P', 'B']: return
    h = st.session_state.history
    if len(h) >= 1:
        cur_gs = {"1": h[-1], "2": "B" if h[-1]=="P" else "P", "3": ("B" if h[-1]=="P" else "P") if len(h)>=2 and h[-1]==h[-2] else h[-1], "4": "P" if h[-1]=="B" else "B", "5": "P" if h.count('P')>=h.count('B') else "B", "6": "B" if h.count('P')>=h.count('B') else "P", "7": ("B" if h[-1]=="P" else "P") if len(h)>=2 and h[-1]==h[-2] else h[-1], "8": ("B" if h[-1]=="P" else "P") if len(h)>=3 and h[-1]==h[-2]==h[-3] else h[-1], "9": h[-1]}
        best_idx = max(st.session_state.strat_stats, key=lambda k: (sum(st.session_state.strat_stats[k]["recent"])*10) + (st.session_state.strat_stats[k]["wins"] / (st.session_state.strat_stats[k]["wins"]+st.session_state.strat_stats[k]["losses"]+0.1)))
        
        if res == cur_gs[best_idx]:
            st.session_state.prediction_logs.append(0); st.session_state.current_step = 0
        else:
            st.session_state.prediction_logs.append(1); st.session_state.current_step += 1
            if st.session_state.current_step > st.session_state.max_step: st.session_state.max_step = st.session_state.current_step
        
        for i in range(1, 10):
            idx = str(i); win = 1 if cur_gs[idx] == res else 0
            st.session_state.strat_stats[idx]["wins"] += win
            st.session_state.strat_stats[idx]["losses"] += (1-win)
            if win: st.session_state.strat_stats[idx]["cur_err"] = 0
            else:
                st.session_state.strat_stats[idx]["cur_err"] += 1
                if st.session_state.strat_stats[idx]["cur_err"] > st.session_state.strat_stats[idx]["max_err"]:
                    st.session_state.strat_stats[idx]["max_err"] = st.session_state.strat_stats[idx]["cur_err"]
            st.session_state.strat_stats[idx]["recent"].append(win)
            if len(st.session_state.strat_stats[idx]["recent"]) > 5: st.session_state.strat_stats[idx]["recent"].pop(0)
    st.session_state.history.append(res)
    pd.DataFrame({'res': st.session_state.history}).to_csv(DB_FILE, index=False)

# --- ៣. MAIN UI ---
st.markdown("<h5 style='text-align:center; color:#00ff00; margin-bottom:5px;'>🔱 AI GUARDIAN PRO MOBILE</h5>", unsafe_allow_html=True)

h = st.session_state.history
best_k = "1"
guesses = {str(i+1): "-" for i in range(9)}
if len(h) >= 1:
    guesses = {"1": h[-1], "2": "B" if h[-1]=="P" else "P", "3": ("B" if h[-1]=="P" else "P") if len(h)>=2 and h[-1]==h[-2] else h[-1], "4": "P" if h[-1]=="B" else "B", "5": "P" if h.count('P')>=h.count('B') else "B", "6": "B" if h.count('P')>=h.count('B') else "P", "7": ("B" if h[-1]=="P" else "P") if len(h)>=2 and h[-1]==h[-2] else h[-1], "8": ("B" if h[-1]=="P" else "P") if len(h)>=3 and h[-1]==h[-2]==h[-3] else h[-1], "9": h[-1]}
    best_k = max(st.session_state.strat_stats, key=lambda k: (sum(st.session_state.strat_stats[k]["recent"])*10) + (st.session_state.strat_stats[k]["wins"] / (st.session_state.strat_stats[k]["wins"]+st.session_state.strat_stats[k]["losses"]+0.1)))

vote_res = guesses[best_k]

# Decision Banner
if len(h) >= 3 and h[-1] == h[-2] == h[-3]:
    st.markdown(f'<div class="decision-container dragon-mode"><h2>🐲 DRAGON: {h[-1]}</h2></div>', unsafe_allow_html=True)
elif st.session_state.current_step >= 2:
    st.markdown(f'<div class="decision-container attack-mode"><h2>🎯 ATTACK: {vote_res}</h2></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="decision-container wait-mode"><h2 style="color:#666;">🛡️ MONITORING</h2></div>', unsafe_allow_html=True)

# --- ប៊ូតុងបញ្ជា ៣ ក្នុង ១ ជួរ ---
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🔵 PLAYER"): process_single_step("P"); st.rerun()
with c2:
    if st.button("🔴 BANKER"): process_single_step("B"); st.rerun()
with c3:
    if st.button("↩️ UNDO"):
        if h: st.session_state.history.pop(); st.rerun()

# --- 🎯 ផ្នែក RISK MONITOR (Step Loss & Max Loss) ---
st.markdown(f"""
    <div class="risk-monitor-container">
        <div class="risk-item">
            <div class="risk-label">Step Loss</div>
            <div class="risk-value" style="color:#ff1744;">{st.session_state.current_step}</div>
        </div>
        <div class="risk-item">
            <div class="risk-label">Max Error</div>
            <div class="risk-value" style="color:#ffab00;">{st.session_state.max_step}</div>
        </div>
        <div class="risk-item">
            <div class="risk-label">Total Cards</div>
            <div class="risk-value">{len(h)}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Grid យុទ្ធសាស្ត្រ ៣x៣ ---
strat_names = ["Dragon", "Ping", "2-Cut", "Rev", "Big", "Inv", "Twin", "3-Cut", "Deep"]
cols = st.columns(3)
for i in range(9):
    idx = str(i+1); g = guesses[idx]; s = st.session_state.strat_stats[idx]
    active = "active-card" if idx == best_k else ""
    clr = "#2979ff" if g == "P" else "#ff1744" if g == "B" else "#555"
    with cols[i % 3]:
        st.markdown(f"""
            <div class="strat-card {active}">
                <div class="strat-name">{strat_names[i]}</div>
                <div class="strat-guess" style="color:{clr};">{g}</div>
                <div style="font-size:10px; color:#00ff00;">{ (s['wins']/(s['wins']+s['losses']+0.1)*100):.0f}%</div>
            </div>
        """, unsafe_allow_html=True)

# --- Bead Plate & Meta ---
st.divider()
beads = "".join([f"<div class='circle-{'p' if r=='P' else 'b'}'>{r}</div>" for r in h[-24:]])
st.markdown(f"<div style='text-align:center;'>{beads}</div>", unsafe_allow_html=True)

meta_logs = st.session_state.prediction_logs[-24:]
meta_html = "".join([f"<div class='{'circle-win' if m==0 else 'circle-loss'}'>{m}</div>" for m in meta_logs])
st.markdown(f"<div style='text-align:center; margin-top:5px;'>{meta_html}</div>", unsafe_allow_html=True)

# Sidebar for Import/Export/Settings
with st.sidebar:
    st.markdown("### ⚙️ SETTINGS & DATA")
    cap = st.number_input("Capital ($)", value=200.0)
    risk_mul = st.slider("Multiplier", 2.0, 2.3, 2.0)
    
    st.divider()
    if st.button("🧹 RESET DATA"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.history, st.session_state.prediction_logs, st.session_state.current_step, st.session_state.max_step = [], [], 0, 0
        st.session_state.strat_stats = {f"{i+1}": {"wins": 0, "losses": 0, "recent": [], "cur_err": 0, "max_err": 0} for i in range(9)}
        st.rerun()
