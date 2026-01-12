import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- ១. UI & MOBILE OPTIMIZED CSS ---
# ប្តូរ layout មក centered ដើម្បីឱ្យវាស្អាតលើអេក្រង់តូច
st.set_page_config(page_title="AI Guardian Mobile", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* កែសម្រួលប្រអប់បង្ហាញលទ្ធផលធំៗងាយមើលលើទូរសព្ទ */
    .decision-container { 
        padding: 20px; 
        border-radius: 20px; 
        text-align: center; 
        margin-bottom: 15px; 
        border: 1px solid rgba(255,255,255,0.1);
    }
    .attack-mode { background: linear-gradient(135deg, #00c853, #004d40); border: 2px solid #00ff00; }
    .dragon-mode { background: linear-gradient(135deg, #d50000, #b71c1c); border: 2px solid #ff0000; }
    .wait-mode { background: #111; border: 1px solid #333; }
    
    /* រចនាប៊ូតុង P និង B ឱ្យធំងាយចុច (Mobile Friendly Buttons) */
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
    }
    
    /* កែសម្រួល Grid យុទ្ធសាស្ត្រឱ្យសមជាមួយអេក្រង់ទូរសព្ទ */
    .strat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr); /* បង្ហាញ ៣ ប្រអប់ក្នុង ១ ជួរលើទូរសព្ទ */
        gap: 8px;
    }
    .strat-card { 
        background: rgba(255, 255, 255, 0.05); 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        border-radius: 10px; 
        padding: 10px; 
        text-align: center;
    }
    .strat-guess { font-size: 24px; font-weight: 900; }
    .active-card { border: 2px solid #00ff00 !important; background: rgba(0, 255, 0, 0.1) !important; }

    /* បង្កើនទំហំគ្រាប់ P/B */
    .circle-p, .circle-b, .circle-win, .circle-loss {
        height: 30px; width: 30px; line-height: 30px; font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [Core Logic ទុកដដែលដូចកូដមុនរបស់អ្នក] ---
# (ចំណុច ២, ៣ ទុកដដែល ខ្ញុំសុំរំលងដើម្បីកុំឱ្យកូដវែងពេក)
if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.prediction_logs, st.session_state.current_step, st.session_state.max_step = [], 0, 0
    st.session_state.strat_stats = {f"{i+1}": {"wins": 0, "losses": 0, "recent": [], "cur_err": 0, "max_err": 0} for i in range(9)}

def process_single_step(res):
    # ... (Logic ដូចមុន)
    res = res.upper()
    st.session_state.history.append(res)
    # បន្ថែម Logic គណនា Prediction នៅទីនេះ...

# --- ៥. MOBILE DASHBOARD UI ---
st.markdown("<h3 style='text-align:center; color:#00ff00;'>🔱 AI GUARDIAN PRO</h3>", unsafe_allow_html=True)

# បង្ហាញ Decision ជាផ្ទាំងធំមុនគេ
h = st.session_state.history
if len(h) >= 3 and h[-1] == h[-2] == h[-3]:
    st.markdown(f'<div class="decision-container dragon-mode"><h2>🐲 DRAGON: {h[-1]}</h2></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="decision-container wait-mode"><h2 style="color:#888;">🛡️ MONITORING...</h2></div>', unsafe_allow_html=True)

# ប៊ូតុងបញ្ជា (ធំៗ ងាយចុច)
col_p, col_b = st.columns(2)
with col_p:
    if st.button("🔵 PLAYER"): process_single_step("P"); st.rerun()
with col_b:
    if st.button("🔴 BANKER"): process_single_step("B"); st.rerun()

if st.button("↩️ UNDO LAST"):
    if h: st.session_state.history.pop(); st.rerun()

st.divider()

# បង្ហាញយុទ្ធសាស្ត្រ ៣ ក្នុងមួយជួរ (សមនឹងអេក្រង់ទូរសព្ទ)
strat_names = ["Drag", "Ping", "2-Cut", "Rev", "Big", "Inv", "Twin", "3-Cut", "Deep"]
cols = st.columns(3)
for i in range(9):
    idx = str(i+1)
    with cols[i % 3]:
        st.markdown(f"""
            <div class="strat-card">
                <small style="font-size:10px;">{strat_names[i]}</small>
                <div class="strat-guess" style="color:#00ff00;">-</div>
            </div>
        """, unsafe_allow_html=True)

st.divider()

# បង្ហាញប្រវត្តិគ្រាប់ (Bead Plate)
st.write("📊 History Log")
beads = "".join([f"<div class='circle-{'p' if r=='P' else 'b'}'>{r}</div>" for r in h[-24:]]) # បង្ហាញត្រឹម ២៤ គ្រាប់ចុងក្រោយឱ្យស្អាតលើ Mobile
st.markdown(f"<div style='text-align:center;'>{beads}</div>", unsafe_allow_html=True)