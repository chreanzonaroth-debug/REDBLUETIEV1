import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# កំណត់ការភ្ជាប់ទៅ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def check_access():
    st.sidebar.title("🔐 ប្រព័ន្ធត្រួតពិនិត្យសិទ្ធិ")
    user_input = st.sidebar.text_input("បញ្ចូលលេខកូដប្រើប្រាស់ (License Key):", type="password")
    
    if not user_input:
        st.warning("សូមបញ្ចូលលេខកូដ ដើម្បីដំណើរការកម្មវិធី!")
        st.stop()

    # អានទិន្នន័យពី Google Sheets
    df = conn.read(worksheet="Sheet1", ttl=0) # Sheet1 គឺជាឈ្មោះ Tab ខាងក្រោម
    
    # ឆែកមើលឈ្មោះអ្នកប្រើក្នុងតារាង
    user_row = df[df['username'] == user_input]

    now = datetime.now()

    if user_row.empty:
        # បើគ្មានឈ្មោះនេះទេ បង្កើតថ្មីចូលក្នុង Sheet
        new_data = pd.DataFrame([{"username": user_input, "start_time": now.strftime("%Y-%m-%d %H:%M:%S"), "is_active": "Yes"}])
        updated_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(worksheet="Sheet1", data=updated_df)
        st.sidebar.success("គណនីថ្មីត្រូវបានបង្កើត! អ្នកអាចប្រើបាន ២៤ម៉ោង។")
        return True
    else:
        # បើមានឈ្មោះហើយ គណនាពេលវេលា
        start_time = datetime.strptime(user_row.iloc[0]['start_time'], "%Y-%m-%d %H:%M:%S")
        deadline = start_time + timedelta(hours=24)
        
        if now > deadline:
            st.error(f"❌ លេខកូដនេះបានផុតកំណត់កាលពី៖ {deadline}")
            st.stop()
        else:
            remaining = deadline - now
            st.sidebar.info(f"⏳ ពេលវេលានៅសល់៖ {str(remaining).split('.')[0]}")
            return True

# ហៅមកប្រើនៅដើមកម្មវិធី
if check_access():
    # --- ដាក់កូដចាស់របស់អ្នកទាំងអស់ចូលក្នុងនេះ ---
    st.title("🔱 AI GUARDIAN PRO V56.6")
# --- ១. UI & LUXURY MOBILE CSS ---
st.set_page_config(page_title="AI Guardian Pro V56.6", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* Top Stats Style */
    .stat-card { background: #111; border: 1px solid #333; border-radius: 12px; padding: 10px; text-align: center; }
    .stat-label { font-size: 11px; color: #888; text-transform: uppercase; }
    .stat-val { font-size: 26px; font-weight: 900; color: #00ff00; line-height: 1; }

    /* Decision Area */
    .decision-container { padding: 20px 10px; border-radius: 20px; text-align: center; margin: 10px 0; border: 1px solid rgba(255,255,255,0.1); }
    .attack-mode { background: linear-gradient(135deg, #00c853, #004d40); border: 2px solid #00ff00; }
    .dragon-mode { background: linear-gradient(135deg, #d50000, #b71c1c); border: 2px solid #ff0000; }
    .wait-mode { background: #111; border: 1px solid #444; }

    /* Custom Buttons Styling */
    div.stButton > button {
        height: 85px !important; 
        font-size: 500px !important; 
        font-weight: 900 !important; 
        border-radius: 15px !important;
        color: white !important;
        border: none !important;
    }
    /* P-Blue, B-Red, Undo-Yellow */
    .btn-p button { background-color: #2979ff !important; }
    .btn-b button { background-color: #ff1744 !important; }
    .btn-u button { background-color: #ffab00 !important; color: black !important; }

    /* Strategy Grid Settings */
    .strat-card { background: #111; border: 1px solid #333; border-radius: 10px; padding: 8px 2px; text-align: center; margin-bottom: 8px; }
    .strat-name { font-size: 11px; color: #aaa; font-weight: bold; margin-bottom: 2px; }
    .res-p { color: #2979ff; font-size: 40px; font-weight: 900; line-height: 1; }
    .res-b { color: #ff1744; font-size: 40px; font-weight: 900; line-height: 1; }
    .res-wait { color: #ffeb3b; font-size: 32px; font-weight: 900; line-height: 1; }
    .active-card { border: 2px solid #00ff00 !important; background: rgba(0, 255, 0, 0.05) !important; }

    /* Meta 0101 Colors */
    .circle-win { height: 26px; width: 26px; background: #00c853; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: white; border: 1px solid #00ff00; }
    .circle-loss { height: 26px; width: 26px; background: #d50000; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: white; border: 1px solid #ff1744; }

    /* Big Road */
    .road-wrapper { display: flex; gap: 4px; overflow-x: auto; background: #000; padding: 12px; border: 1px solid #222; border-radius: 12px; min-height: 150px; }
    .road-column { display: flex; flex-direction: column; gap: 4px; }
    .circle-p { height: 22px; width: 22px; background: radial-gradient(circle, #2979ff, #0d47a1); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold; color: white; }
    .circle-b { height: 22px; width: 22px; background: radial-gradient(circle, #ff1744, #880e4f); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- ២. CORE ENGINE ---
DB_FILE = "ai_master_database_v55.csv"
if 'history' not in st.session_state:
    if os.path.exists(DB_FILE): st.session_state.history = pd.read_csv(DB_FILE)['res'].tolist()
    else: st.session_state.history = []
    st.session_state.prediction_logs, st.session_state.current_step, st.session_state.max_step = [], 0, 0
    st.session_state.strat_stats = {f"{i+1}": {"wins": 0, "losses": 0, "recent": [], "cur_err": 0, "max_err": 0} for i in range(9)}

strat_names = ["Dragon", "Ping-Pong", "2-Cut", "Reverse", "Big Side", "Inverse", "Twin Master", "3-Cut", "Deep AI"]

def get_guesses(history):
    h = history
    if len(h) < 1: return {str(i+1): "WAIT" for i in range(9)}
    return {
        "1": h[-1], "2": "B" if h[-1]=="P" else "P",
        "3": ("B" if h[-1]=="P" else "P") if len(h)>=2 and h[-1]==h[-2] else h[-1],
        "4": "P" if h[-1]=="B" else "B",
        "5": "P" if h.count('P')>=h.count('B') else "B",
        "6": "B" if h.count('P')>=h.count('B') else "P",
        "7": ("B" if h[-1]=="P" else "P") if len(h)>=2 and h[-1]==h[-2] else h[-1],
        "8": ("B" if h[-1]=="P" else "P") if len(h)>=3 and h[-1]==h[-2]==h[-3] else h[-1],
        "9": h[-1] if len(h) >= 2 and h[-1] == h[-2] else ("B" if h[-1]=="P" else "P")
    }

def process_single_step(res):
    res = res.upper()
    if res not in ['P', 'B']: return
    h = st.session_state.history
    if len(h) >= 1:
        guesses = get_guesses(h)
        best_idx = max(st.session_state.strat_stats, key=lambda k: (sum(st.session_state.strat_stats[k]["recent"]) * 15) + (st.session_state.strat_stats[k]["wins"] / (st.session_state.strat_stats[k]["wins"]+st.session_state.strat_stats[k]["losses"]+0.1)) - (st.session_state.strat_stats[k]["cur_err"] * 5))
        if res == guesses[best_idx]:
            st.session_state.prediction_logs.append(0); st.session_state.current_step = 0
        else:
            st.session_state.prediction_logs.append(1); st.session_state.current_step += 1
            if st.session_state.current_step > st.session_state.max_step: st.session_state.max_step = st.session_state.current_step
        for i in range(1, 10):
            idx = str(i); win = 1 if guesses[idx] == res else 0
            st.session_state.strat_stats[idx]["wins"] += win
            st.session_state.strat_stats[idx]["losses"] += (1-win)
            if win: st.session_state.strat_stats[idx]["cur_err"] = 0
            else:
                st.session_state.strat_stats[idx]["cur_err"] += 1
                if st.session_state.strat_stats[idx]["cur_err"] > st.session_state.strat_stats[idx]["max_err"]: st.session_state.strat_stats[idx]["max_err"] = st.session_state.strat_stats[idx]["cur_err"]
            st.session_state.strat_stats[idx]["recent"].append(win)
            if len(st.session_state.strat_stats[idx]["recent"]) > 6: st.session_state.strat_stats[idx]["recent"].pop(0)
    st.session_state.history.append(res)

# --- ៣. TOP STATS ---
h = st.session_state.history
acc = (1 - (sum(st.session_state.prediction_logs[-10:]) / 10)) * 100 if len(st.session_state.prediction_logs) >= 10 else 0
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="stat-card"><div class="stat-label">Total</div><div class="stat-val">{len(h)}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="stat-card"><div class="stat-label">Step</div><div class="stat-val" style="color:#ff1744;">{st.session_state.current_step}</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="stat-card"><div class="stat-label">Max</div><div class="stat-val" style="color:#ff1744;">{st.session_state.max_step}</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="stat-card"><div class="stat-label">Health</div><div class="stat-val" style="color:#ffab00;">{acc:.0f}%</div></div>', unsafe_allow_html=True)

# --- ៤. MAIN DECISION ---
guesses = get_guesses(h)
best_k = max(st.session_state.strat_stats, key=lambda k: (sum(st.session_state.strat_stats[k]["recent"]) * 15) + (st.session_state.strat_stats[k]["wins"] / (st.session_state.strat_stats[k]["wins"]+st.session_state.strat_stats[k]["losses"]+0.1)) - (st.session_state.strat_stats[k]["cur_err"] * 5))
mode = "dragon-mode" if len(h) >= 3 and h[-1] == h[-2] == h[-3] else ("wait-mode" if st.session_state.current_step >= 3 else "attack-mode")
st.markdown(f'<div class="decision-container {mode}"><h1>{guesses[best_k] if len(h)>0 else "WAIT"}</h1><small>Logic: {strat_names[int(best_k)-1]}</small></div>', unsafe_allow_html=True)

# --- ៥. BUTTON ROW (P, B, UNDO) ---
b1, b2, b3 = st.columns([1, 1, 1])
with b1:
    st.markdown('<div class="btn-p">', unsafe_allow_html=True)
    if st.button("P", use_container_width=True): 
        process_single_step("P"); pd.DataFrame({'res': st.session_state.history}).to_csv(DB_FILE, index=False); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with b2:
    st.markdown('<div class="btn-b">', unsafe_allow_html=True)
    if st.button("B", use_container_width=True): 
        process_single_step("B"); pd.DataFrame({'res': st.session_state.history}).to_csv(DB_FILE, index=False); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with b3:
    st.markdown('<div class="btn-u">', unsafe_allow_html=True)
    if st.button("↩", use_container_width=True):
        if h: st.session_state.history.pop(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ៦. STRATEGY GRID ---
st.markdown("### 🧬 AI STRATEGIES")
sc = st.columns(3)
for i in range(9):
    idx = str(i+1); active = "active-card" if idx == best_k else ""
    g = guesses[idx]
    res_class = "res-p" if g == "P" else "res-b" if g == "B" else "res-wait"
    with sc[i % 3]:
        st.markdown(f'<div class="strat-card {active}"><div class="strat-name">{strat_names[i]}</div><div class="{res_class}">{g}</div></div>', unsafe_allow_html=True)

# --- ៧. BIG ROAD ---
st.divider()
st.markdown("### 📊 BIG ROAD")
def get_big_road_html(history):
    if not history: return ""
    columns, current_col = [], [history[0]]
    for i in range(1, len(history)):
        if history[i] == history[i-1]: current_col.append(history[i])
        else: columns.append(current_col); current_col = [history[i]]
    columns.append(current_col)
    html = '<div class="road-wrapper">'
    for col in columns:
        html += '<div class="road-column">'
        for item in col: html += f'<div class="circle-{"p" if item == "P" else "b"}">{item}</div>'
        html += '</div>'
    html += '</div>'
    return html
st.markdown(get_big_road_html(h), unsafe_allow_html=True)

# --- ៨. META 0101 HISTORY ---
st.markdown("### 🧬 0101 META HISTORY")
meta_logs = st.session_state.prediction_logs[-60:]
meta_html = "".join([f"<div class='{'circle-win' if m==0 else 'circle-loss'}'>{m}</div>" for m in meta_logs])
st.markdown(f"<div style='background:#111; padding:10px; border-radius:10px; display:flex; flex-wrap:wrap; gap:4px; border:1px solid #333;'>{meta_html}</div>", unsafe_allow_html=True)

if st.sidebar.button("🧹 RESET"):
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.history, st.session_state.prediction_logs, st.session_state.current_step, st.session_state.max_step = [], [], 0, 0
    st.rerun()