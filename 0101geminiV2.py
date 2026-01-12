import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- ១. UI & LUXURY CSS (កែសម្រួលទំហំអក្សរ និងគ្រាប់ Meta) ---
st.set_page_config(page_title="AI Guardian Pro V56.6", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .decision-container { padding: 30px; border-radius: 25px; text-align: center; margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.1); }
    .attack-mode { background: linear-gradient(135deg, #00c853, #004d40); border: 2px solid #00ff00; }
    .dragon-mode { background: linear-gradient(135deg, #d50000, #b71c1c); border: 2px solid #ff0000; }
    .wait-mode { background: #111; border: 1px solid #333; }
    
    /* កែសម្រួលអក្សរក្នុង Column ឱ្យធំ */
    .strat-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; text-align: center; min-height: 160px; }
    .strat-name { font-size: 14px; color: #bbb; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .strat-guess { font-size: 38px; font-weight: 900; line-height: 1; }
    .active-card { border: 3px solid #00ff00 !important; background: rgba(0, 255, 0, 0.08) !important; }
    
    .risk-box { background: #0f0f0f; border-radius: 15px; padding: 20px; border: 1px solid #222; text-align: center; }
    .risk-val { font-size: 32px; font-weight: bold; color: #ffab00; }
    
    /* គ្រាប់ P/B និង គ្រាប់ 0/1 ឱ្យប៉ុនគ្នា */
    .circle-p { height: 26px; width: 26px; background: radial-gradient(circle, #2979ff, #0d47a1); border-radius: 50%; display: inline-block; color: white; text-align: center; line-height: 26px; font-size: 11px; font-weight: bold; margin: 2px; }
    .circle-b { height: 26px; width: 26px; background: radial-gradient(circle, #ff1744, #880e4f); border-radius: 50%; display: inline-block; color: white; text-align: center; line-height: 26px; font-size: 11px; font-weight: bold; margin: 2px; }
    .circle-win { height: 26px; width: 26px; background: #00c853; border-radius: 50%; display: inline-block; color: white; text-align: center; line-height: 26px; font-size: 11px; font-weight: bold; margin: 2px; border: 1px solid #00ff00; }
    .circle-loss { height: 26px; width: 26px; background: #d50000; border-radius: 50%; display: inline-block; color: white; text-align: center; line-height: 26px; font-size: 11px; font-weight: bold; margin: 2px; border: 1px solid #ff1744; }
    
    .stat-card { background: rgba(255, 255, 255, 0.05); border: 1px solid #444; border-radius: 10px; padding: 10px; text-align: center; }
    .stat-val-new { font-size: 40px; font-weight: bold; color: #00ff00; }
    .error-tag { font-size: 12px; color: #ff4444; margin-top: 8px; font-weight: bold; border-top: 1px solid #333; padding-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- ២. CORE ENGINE (Logic ដដែល) ---
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

# --- ៣. KEYBOARD COMMANDS ---
st.components.v1.html("""<script>const doc = window.parent.document; doc.addEventListener('keydown', function(e) {
    if (e.key.toLowerCase() === 'p') doc.querySelectorAll('button').forEach(btn => { if (btn.innerText.includes('PLAYER')) btn.click(); });
    else if (e.key.toLowerCase() === 'b') doc.querySelectorAll('button').forEach(btn => { if (btn.innerText.includes('BANKER')) btn.click(); });
    else if (e.key.toLowerCase() === 'u') doc.querySelectorAll('button').forEach(btn => { if (btn.innerText.includes('UNDO')) btn.click(); });
});</script>""", height=0)

# --- ៤. SIDEBAR ---
with st.sidebar:
    st.markdown("## 📂 BIG DATA CENTER")
    uploaded_files = st.file_uploader("Import Multiple Shoes (CSV)", type="csv", accept_multiple_files=True)
    if uploaded_files:
        if st.button("🚀 MERGE & ANALYZE ALL"):
            combined_history = []
            for f in uploaded_files:
                df = pd.read_csv(f, header=None)
                vals = df.stack().astype(str).str.upper().tolist()
                clean_vals = [v.strip() for v in vals if v.strip() in ['P', 'B']]
                combined_history.extend(clean_vals)
            if combined_history:
                st.session_state.history, st.session_state.prediction_logs, st.session_state.current_step, st.session_state.max_step = [], [], 0, 0
                st.session_state.strat_stats = {f"{i+1}": {"wins": 0, "losses": 0, "recent": [], "cur_err": 0, "max_err": 0} for i in range(9)}
                for r in combined_history: process_single_step(r)
                st.rerun()
    if len(st.session_state.history) > 0:
        csv_data = pd.DataFrame({'res': st.session_state.history}).to_csv(index=False).encode('utf-8')
        st.download_button("📥 EXPORT MASTER CSV", csv_data, f"Master_AI_{datetime.now().strftime('%H%M')}.csv", "text/csv")
    if st.button("🧹 RESET ALL DATA"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.session_state.history, st.session_state.prediction_logs, st.session_state.current_step, st.session_state.max_step = [], [], 0, 0
        st.session_state.strat_stats = {f"{i+1}": {"wins": 0, "losses": 0, "recent": [], "cur_err": 0, "max_err": 0} for i in range(9)}
        st.rerun()

# --- ៥. DASHBOARD UI ---
h = st.session_state.history
if len(h) > 0:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="stat-card"><small>TOTAL CARDS</small><div class="stat-val-new">{len(h)}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card"><small>PLAYER (P)</small><div class="stat-val-new" style="color:#2979ff;">{h.count("P")}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="stat-card"><small>BANKER (B)</small><div class="stat-val-new" style="color:#ff1744;">{h.count("B")}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="stat-card"><small>EST. SHOES</small><div class="stat-val-new" style="color:#ffab00;">{round(len(h)/60,1)}</div></div>', unsafe_allow_html=True)
    st.divider()

strat_names = ["Dragon", "Ping-Pong", "2-Cut", "Reverse", "Big Side", "Inverse", "Twin Master", "3-Cut", "Deep AI"]
guesses = {str(i+1): "WAIT" for i in range(9)}
if len(h) >= 1:
    guesses = {"1": h[-1], "2": "B" if h[-1]=="P" else "P", "3": ("B" if h[-1]=="P" else "P") if len(h)>=2 and h[-1]==h[-2] else h[-1], "4": "P" if h[-1]=="B" else "B", "5": "P" if h.count('P')>=h.count('B') else "B", "6": "B" if h.count('P')>=h.count('B') else "P", "7": ("B" if h[-1]=="P" else "P") if len(h)>=2 and h[-1]==h[-2] else h[-1], "8": ("B" if h[-1]=="P" else "P") if len(h)>=3 and h[-1]==h[-2]==h[-3] else h[-1], "9": h[-1]}

best_k = max(st.session_state.strat_stats, key=lambda k: (sum(st.session_state.strat_stats[k]["recent"])*10) + (st.session_state.strat_stats[k]["wins"] / (st.session_state.strat_stats[k]["wins"]+st.session_state.strat_stats[k]["losses"]+0.1)))
vote_res = guesses[best_k]

st.markdown("<h2 style='text-align:center; color:#00ff00; letter-spacing:3px;'>🔱 AI GUARDIAN V56.6</h2>", unsafe_allow_html=True)

if len(h) >= 3 and h[-1] == h[-2] == h[-3]:
    st.markdown(f'<div class="decision-container dragon-mode"><h1>🐲 DRAGON: {h[-1]}</h1></div>', unsafe_allow_html=True)
elif st.session_state.current_step >= 3:
    st.markdown(f'<div class="decision-container attack-mode"><h1>🎯 ATTACK: {vote_res}</h1><small>Logic: {strat_names[int(best_k)-1]}</small></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="decision-container wait-mode"><h1 style="color:#666;">🛡️ MONITORING...</h1><p>Step {st.session_state.current_step}</p></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
if c1.button("🔵 PLAYER (P)"): process_single_step("P"); pd.DataFrame({'res': st.session_state.history}).to_csv(DB_FILE, index=False); st.rerun()
if c2.button("🔴 BANKER (B)"): process_single_step("B"); pd.DataFrame({'res': st.session_state.history}).to_csv(DB_FILE, index=False); st.rerun()
if c3.button("↩️ UNDO (U)"): 
    if h: st.session_state.history.pop(); st.rerun()

st.divider()

# --- ៩ Strategy Analysis Grid (ពង្រីកអក្សរធំ) ---
sc = st.columns(9)
for i in range(9):
    idx = str(i+1); g = guesses[idx]; s = st.session_state.strat_stats[idx]
    wr = (s['wins']/(s['wins']+s['losses']+0.1))*100
    active = "active-card" if idx == best_k else ""
    clr = "#2979ff" if g == "P" else "#ff1744" if g == "B" else "#555"
    with sc[i]:
        st.markdown(f"""
            <div class="strat-card {active}">
                <div class="strat-name">{strat_names[i]}</div>
                <div class="strat-guess" style="color:{clr};">{g}</div>
                <div style="font-size:14px; color:#00ff00; font-weight:bold;">{wr:.0f}% WR</div>
                <div class="error-tag">MAX ERR: {s['max_err']}</div>
            </div>
        """, unsafe_allow_html=True)

st.divider()

# Lower Dashboard
col_l, col_r = st.columns([2.2, 1])
with col_l:
    st.markdown("### 📊 Bead Plate & Meta History")
    # Bead Plate (P/B)
    beads = "".join([f"<div class='circle-{'p' if r=='P' else 'b'}'>{r}</div>" for r in h[-100:]])
    st.markdown(f"<div style='background:#0a0a0a; padding:15px; border-radius:15px; height:150px; overflow-y:auto; border:1px solid #222;'>{beads}</div>", unsafe_allow_html=True)
    
    # Meta History (0/1) - កែឱ្យគ្រាប់ធំប៉ុន Bead Plate
    meta_logs = st.session_state.prediction_logs[-100:]
    meta_html = "".join([f"<div class='{'circle-win' if m==0 else 'circle-loss'}'>{m}</div>" for m in meta_logs])
    st.markdown(f"<div style='background:#000; padding:15px; border-radius:15px; height:80px; overflow-y:auto; border:1px solid #333; margin-top:10px;'>{meta_html}</div>", unsafe_allow_html=True)

with col_r:
    st.markdown("### ⚠️ Risk Monitor")
    r1, r2 = st.columns(2)
    r1.markdown(f'<div class="risk-box"><small>STEP LOSS</small><div class="risk-val" style="color:#ff1744;">{st.session_state.current_step}</div></div>', unsafe_allow_html=True)
    r2.markdown(f'<div class="risk-box"><small>MAX ERROR</small><div class="risk-val">{st.session_state.max_step}</div></div>', unsafe_allow_html=True)
    
    cap = st.sidebar.number_input("Capital ($)", value=200.0, key="cap_sidebar")
    risk = st.sidebar.slider("Multiplier", 2.0, 2.3, 2.0, key="risk_sidebar")
    
    rows = ""
    cum, base = 0, 1.0
    for s in range(1, 10):
        bet = base * (risk ** (s-1))
        if cum + bet > cap: break
        cum += bet
        active = "style='color:#00ff00; font-weight:bold; background:rgba(0,255,0,0.1);'" if st.session_state.current_step+1 == s else ""
        rows += f"<tr {active}><td>S{s}</td><td>${bet:,.0f}</td><td>${cum:,.0f}</td></tr>"
    st.markdown(f'<table style="width:100%; text-align:center; font-size:12px; border-collapse:collapse;"><tr><th>Step</th><th>Bet</th><th>Total</th></tr>{rows}</table>', unsafe_allow_html=True)