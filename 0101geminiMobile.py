import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- ១. MOBILE RESPONSIVE UI ---
st.set_page_config(
    page_title="AI Guardian Pro V56.6",
    layout="wide",
    initial_sidebar_state="collapsed"  # បិទ sidebar ដំបូងសម្រាប់ mobile
)

st.markdown("""
    <style>
    /* Base Mobile Styles */
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* Mobile-first container */
    .mobile-container { max-width: 390px; margin: 0 auto; padding: 10px; }
    
    /* Decision cards for mobile */
    .decision-container { 
        padding: 20px; 
        border-radius: 20px; 
        text-align: center; 
        margin-bottom: 15px; 
        border: 1px solid rgba(255,255,255,0.1);
        width: 100%;
    }
    .attack-mode { background: linear-gradient(135deg, #00c853, #004d40); border: 2px solid #00ff00; }
    .dragon-mode { background: linear-gradient(135deg, #d50000, #b71c1c); border: 2px solid #ff0000; }
    .wait-mode { background: #111; border: 1px solid #333; }
    
    /* Strategy cards mobile grid */
    .strat-card { 
        background: rgba(255, 255, 255, 0.03); 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        border-radius: 12px; 
        padding: 12px 8px; 
        text-align: center; 
        min-height: 120px;
        margin-bottom: 8px;
    }
    .strat-name { 
        font-size: 11px !important; 
        color: #bbb; 
        font-weight: bold; 
        text-transform: uppercase; 
        margin-bottom: 4px;
        line-height: 1.2;
    }
    .strat-guess { 
        font-size: 28px !important; 
        font-weight: 900; 
        line-height: 1;
        margin: 8px 0;
    }
    .active-card { border: 3px solid #00ff00 !important; background: rgba(0, 255, 0, 0.08) !important; }
    
    /* Mobile-friendly buttons */
    .mobile-btn-container { display: flex; gap: 8px; margin: 15px 0; }
    .mobile-btn { 
        flex: 1; 
        padding: 14px 5px !important; 
        font-size: 13px !important;
        border-radius: 12px !important;
        min-height: 50px;
    }
    
    /* Compact stats for mobile */
    .stat-card-mobile { 
        background: rgba(255, 255, 255, 0.05); 
        border: 1px solid #444; 
        border-radius: 10px; 
        padding: 8px 5px; 
        text-align: center;
        margin-bottom: 8px;
    }
    .stat-val-mobile { 
        font-size: 24px !important; 
        font-weight: bold; 
        margin: 5px 0;
    }
    
    /* Smaller beads for mobile */
    .circle-p { 
        height: 22px; 
        width: 22px; 
        background: radial-gradient(circle, #2979ff, #0d47a1); 
        border-radius: 50%; 
        display: inline-block; 
        color: white; 
        text-align: center; 
        line-height: 22px; 
        font-size: 10px; 
        font-weight: bold; 
        margin: 1px;
    }
    .circle-b { 
        height: 22px; 
        width: 22px; 
        background: radial-gradient(circle, #ff1744, #880e4f); 
        border-radius: 50%; 
        display: inline-block; 
        color: white; 
        text-align: center; 
        line-height: 22px; 
        font-size: 10px; 
        font-weight: bold; 
        margin: 1px;
    }
    .circle-win, .circle-loss { 
        height: 22px; 
        width: 22px; 
        border-radius: 50%; 
        display: inline-block; 
        color: white; 
        text-align: center; 
        line-height: 22px; 
        font-size: 10px; 
        font-weight: bold; 
        margin: 1px;
    }
    
    /* Hide sidebar on mobile initially */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            width: 100% !important;
            min-width: 100% !important;
        }
    }
    
    /* Scrollable containers */
    .scrollable-x { overflow-x: auto; white-space: nowrap; padding: 10px 0; }
    .scrollable-y { overflow-y: auto; max-height: 150px; }
    
    /* Mobile headings */
    .mobile-h1 { font-size: 20px !important; text-align: center; margin: 10px 0; }
    .mobile-h2 { font-size: 16px !important; margin: 8px 0; }
    .mobile-h3 { font-size: 14px !important; margin: 6px 0; }
    
    /* Tabbed interface for mobile */
    .mobile-tabs { display: flex; gap: 5px; margin: 15px 0; }
    .mobile-tab { 
        flex: 1; 
        padding: 10px; 
        text-align: center; 
        background: #222; 
        border-radius: 8px; 
        cursor: pointer;
        font-size: 12px;
    }
    .mobile-tab.active { background: #00c853; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- ២. CORE ENGINE (ដដែល) ---
DB_FILE = "ai_master_database_v55.csv"
if 'history' not in st.session_state:
    if os.path.exists(DB_FILE): 
        st.session_state.history = pd.read_csv(DB_FILE)['res'].tolist()
    else: 
        st.session_state.history = []
    st.session_state.prediction_logs = []
    st.session_state.current_step = 0
    st.session_state.max_step = 0
    st.session_state.strat_stats = {f"{i+1}": {"wins": 0, "losses": 0, "recent": [], "cur_err": 0, "max_err": 0} for i in range(9)}

def process_single_step(res):
    res = res.upper()
    if res not in ['P', 'B']: 
        return
    
    h = st.session_state.history
    if len(h) >= 1:
        # Calculate guesses for all strategies
        cur_gs = {
            "1": h[-1],
            "2": "B" if h[-1] == "P" else "P",
            "3": ("B" if h[-1] == "P" else "P") if len(h) >= 2 and h[-1] == h[-2] else h[-1],
            "4": "P" if h[-1] == "B" else "B",
            "5": "P" if h.count('P') >= h.count('B') else "B",
            "6": "B" if h.count('P') >= h.count('B') else "P",
            "7": ("B" if h[-1] == "P" else "P") if len(h) >= 2 and h[-1] == h[-2] else h[-1],
            "8": ("B" if h[-1] == "P" else "P") if len(h) >= 3 and h[-1] == h[-2] == h[-3] else h[-1],
            "9": h[-1]
        }
        
        # Find best strategy
        best_idx = max(
            st.session_state.strat_stats.keys(),
            key=lambda k: (
                sum(st.session_state.strat_stats[k]["recent"]) * 10 +
                (st.session_state.strat_stats[k]["wins"] / 
                 (st.session_state.strat_stats[k]["wins"] + st.session_state.strat_stats[k]["losses"] + 0.1))
            )
        )
        
        # Update prediction logs
        if res == cur_gs[best_idx]:
            st.session_state.prediction_logs.append(0)
            st.session_state.current_step = 0
        else:
            st.session_state.prediction_logs.append(1)
            st.session_state.current_step += 1
            if st.session_state.current_step > st.session_state.max_step:
                st.session_state.max_step = st.session_state.current_step
        
        # Update strategy stats
        for i in range(1, 10):
            idx = str(i)
            win = 1 if cur_gs[idx] == res else 0
            
            st.session_state.strat_stats[idx]["wins"] += win
            st.session_state.strat_stats[idx]["losses"] += (1 - win)
            
            if win:
                st.session_state.strat_stats[idx]["cur_err"] = 0
            else:
                st.session_state.strat_stats[idx]["cur_err"] += 1
                if st.session_state.strat_stats[idx]["cur_err"] > st.session_state.strat_stats[idx]["max_err"]:
                    st.session_state.strat_stats[idx]["max_err"] = st.session_state.strat_stats[idx]["cur_err"]
            
            st.session_state.strat_stats[idx]["recent"].append(win)
            if len(st.session_state.strat_stats[idx]["recent"]) > 5:
                st.session_state.strat_stats[idx]["recent"].pop(0)
    
    st.session_state.history.append(res)

# --- ៣. KEYBOARD COMMANDS (ដដែល) ---
st.components.v1.html("""<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    if (e.key.toLowerCase() === 'p') {
        doc.querySelectorAll('button').forEach(btn => {
            if (btn.innerText.includes('PLAYER')) btn.click();
        });
    }
    else if (e.key.toLowerCase() === 'b') {
        doc.querySelectorAll('button').forEach(btn => {
            if (btn.innerText.includes('BANKER')) btn.click();
        });
    }
    else if (e.key.toLowerCase() === 'u') {
        doc.querySelectorAll('button').forEach(btn => {
            if (btn.innerText.includes('UNDO')) btn.click();
        });
    }
});
</script>""", height=0)

# --- ៤. MOBILE TABBED INTERFACE ---
tab_selected = st.session_state.get("mobile_tab", "main")

# Tab selector
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 ទំព័រដើម", key="tab_main", use_container_width=True):
        st.session_state.mobile_tab = "main"
        st.rerun()
with col2:
    if st.button("📊 ទិន្នន័យ", key="tab_data", use_container_width=True):
        st.session_state.mobile_tab = "data"
        st.rerun()
with col3:
    if st.button("⚙️ ការកំណត់", key="tab_settings", use_container_width=True):
        st.session_state.mobile_tab = "settings"
        st.rerun()

st.divider()

# --- ៥. MAIN TAB CONTENT ---
if tab_selected == "main":
    h = st.session_state.history

    # Ensure defaults so later UI code can always reference them
    guesses = {str(i+1): "WAIT" for i in range(9)}
    try:
        best_k = max(
            st.session_state.strat_stats.keys(),
            key=lambda k: (
                sum(st.session_state.strat_stats[k]["recent"]) * 10 +
                (st.session_state.strat_stats[k]["wins"] /
                 (st.session_state.strat_stats[k]["wins"] + st.session_state.strat_stats[k]["losses"] + 0.1))
            )
        )
    except Exception:
        best_k = "1"
    
    # Compact stats row
    if len(h) > 0:
        stats_cols = st.columns(4)
        with stats_cols[0]:
            st.markdown(f'''
                <div class="stat-card-mobile">
                    <div style="font-size:10px; color:#888;">សរុប</div>
                    <div class="stat-val-mobile" style="color:#00ff00;">{len(h)}</div>
                </div>
            ''', unsafe_allow_html=True)
        with stats_cols[1]:
            st.markdown(f'''
                <div class="stat-card-mobile">
                    <div style="font-size:10px; color:#888;">P</div>
                    <div class="stat-val-mobile" style="color:#2979ff;">{h.count("P")}</div>
                </div>
            ''', unsafe_allow_html=True)
        with stats_cols[2]:
            st.markdown(f'''
                <div class="stat-card-mobile">
                    <div style="font-size:10px; color:#888;">B</div>
                    <div class="stat-val-mobile" style="color:#ff1744;">{h.count("B")}</div>
                </div>
            ''', unsafe_allow_html=True)
        with stats_cols[3]:
            st.markdown(f'''
                <div class="stat-card-mobile">
                    <div style="font-size:10px; color:#888;">ស្បែក</div>
                    <div class="stat-val-mobile" style="color:#ffab00;">{round(len(h)/60,1)}</div>
                </div>
            ''', unsafe_allow_html=True)
    
    # Main decision display
    st.markdown('<div class="mobile-h1">🔱 AI GUARDIAN V56.6</div>', unsafe_allow_html=True)
    
    if len(h) >= 3 and h[-1] == h[-2] == h[-3]:
        st.markdown(f'''
            <div class="decision-container dragon-mode">
                <h2 style="margin:10px 0; font-size:24px;">🐲 DRAGON: {h[-1]}</h2>
            </div>
        ''', unsafe_allow_html=True)
    elif st.session_state.current_step >= 3:
        # Get best strategy
        strat_names = ["Dragon", "Ping-Pong", "2-Cut", "Reverse", "Big Side", "Inverse", "Twin Master", "3-Cut", "Deep AI"]
        guesses = {str(i+1): "WAIT" for i in range(9)}
        if len(h) >= 1:
            guesses = {
                "1": h[-1],
                "2": "B" if h[-1]=="P" else "P",
                "3": ("B" if h[-1]=="P" else "P") if len(h)>=2 and h[-1]==h[-2] else h[-1],
                "4": "P" if h[-1]=="B" else "B",
                "5": "P" if h.count('P')>=h.count('B') else "B",
                "6": "B" if h.count('P')>=h.count('B') else "P",
                "7": ("B" if h[-1]=="P" else "P") if len(h)>=2 and h[-1]==h[-2] else h[-1],
                "8": ("B" if h[-1]=="P" else "P") if len(h)>=3 and h[-1]==h[-2]==h[-3] else h[-1],
                "9": h[-1]
            }
        
        best_k = max(
            st.session_state.strat_stats.keys(),
            key=lambda k: (
                sum(st.session_state.strat_stats[k]["recent"]) * 10 +
                (st.session_state.strat_stats[k]["wins"] / 
                 (st.session_state.strat_stats[k]["wins"] + st.session_state.strat_stats[k]["losses"] + 0.1))
            )
        )
        vote_res = guesses[best_k]
        
        st.markdown(f'''
            <div class="decision-container attack-mode">
                <h2 style="margin:10px 0; font-size:24px;">🎯 ATTACK: {vote_res}</h2>
                <div style="font-size:12px; margin-top:5px;">Logic: {strat_names[int(best_k)-1]}</div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="decision-container wait-mode">
                <h2 style="margin:10px 0; color:#666; font-size:22px;">🛡️ MONITORING...</h2>
                <div style="font-size:14px;">Step {st.session_state.current_step}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    # Action buttons (mobile optimized)
    btn_cols = st.columns(3)
    with btn_cols[0]:
        if st.button("🔵 P", key="btn_p", use_container_width=True):
            process_single_step("P")
            pd.DataFrame({'res': st.session_state.history}).to_csv(DB_FILE, index=False)
            st.rerun()
    with btn_cols[1]:
        if st.button("🔴 B", key="btn_b", use_container_width=True):
            process_single_step("B")
            pd.DataFrame({'res': st.session_state.history}).to_csv(DB_FILE, index=False)
            st.rerun()
    with btn_cols[2]:
        if st.button("↩️ UNDO", key="btn_undo", use_container_width=True):
            if h:
                st.session_state.history.pop()
                st.rerun()
    
    st.divider()
    
    # Strategy Grid (3x3 for mobile)
    st.markdown('<div class="mobile-h2">📈 Strategy Analysis</div>', unsafe_allow_html=True)
    
    # First row
    row1 = st.columns(3)
    for i in range(3):
        idx = str(i+1)
        s = st.session_state.strat_stats[idx]
        g = guesses.get(idx, "WAIT")
        wr = (s['wins']/(s['wins']+s['losses']+0.1))*100
        active = "active-card" if idx == best_k else ""
        clr = "#2979ff" if g == "P" else "#ff1744" if g == "B" else "#555"
        
        with row1[i]:
            st.markdown(f'''
                <div class="strat-card {active}">
                    <div class="strat-name">{["Dragon", "Ping-Pong", "2-Cut"][i]}</div>
                    <div class="strat-guess" style="color:{clr};">{g}</div>
                    <div style="font-size:11px; color:#00ff00;">{wr:.0f}%</div>
                    <div style="font-size:9px; color:#ff4444; margin-top:4px;">E:{s["max_err"]}</div>
                </div>
            ''', unsafe_allow_html=True)
    
    # Second row
    row2 = st.columns(3)
    for i in range(3, 6):
        idx = str(i+1)
        s = st.session_state.strat_stats[idx]
        g = guesses.get(idx, "WAIT")
        wr = (s['wins']/(s['wins']+s['losses']+0.1))*100
        active = "active-card" if idx == best_k else ""
        clr = "#2979ff" if g == "P" else "#ff1744" if g == "B" else "#555"
        
        with row2[i-3]:
            st.markdown(f'''
                <div class="strat-card {active}">
                    <div class="strat-name">{["Reverse", "Big Side", "Inverse"][i-3]}</div>
                    <div class="strat-guess" style="color:{clr};">{g}</div>
                    <div style="font-size:11px; color:#00ff00;">{wr:.0f}%</div>
                    <div style="font-size:9px; color:#ff4444; margin-top:4px;">E:{s["max_err"]}</div>
                </div>
            ''', unsafe_allow_html=True)
    
    # Third row
    row3 = st.columns(3)
    for i in range(6, 9):
        idx = str(i+1)
        s = st.session_state.strat_stats[idx]
        g = guesses.get(idx, "WAIT")
        wr = (s['wins']/(s['wins']+s['losses']+0.1))*100
        active = "active-card" if idx == best_k else ""
        clr = "#2979ff" if g == "P" else "#ff1744" if g == "B" else "#555"
        
        with row3[i-6]:
            st.markdown(f'''
                <div class="strat-card {active}">
                    <div class="strat-name">{["Twin Master", "3-Cut", "Deep AI"][i-6]}</div>
                    <div class="strat-guess" style="color:{clr};">{g}</div>
                    <div style="font-size:11px; color:#00ff00;">{wr:.0f}%</div>
                    <div style="font-size:9px; color:#ff4444; margin-top:4px;">E:{s["max_err"]}</div>
                </div>
            ''', unsafe_allow_html=True)
    
    st.divider()
    
    # Bead Plate & Risk Monitor
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown('<div class="mobile-h3">📊 Bead Plate</div>', unsafe_allow_html=True)
        beads = "".join([f"<div class='circle-{'p' if r=='P' else 'b'}'>{r}</div>" for r in h[-40:]])
        st.markdown(f'''
            <div style="
                background:#0a0a0a; 
                padding:12px; 
                border-radius:12px; 
                border:1px solid #222;
                margin-bottom:10px;
            ">
                <div class="scrollable-y" style="max-height:120px;">
                    {beads}
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="mobile-h3">⚠️ ហានិភ័យ</div>', unsafe_allow_html=True)
        st.markdown(f'''
            <div style="
                background: #0f0f0f;
                border-radius: 12px;
                padding: 15px;
                text-align: center;
                border: 1px solid #222;
                margin-bottom: 8px;
            ">
                <div style="font-size:11px; color:#888;">STEP LOSS</div>
                <div style="font-size:28px; font-weight:bold; color:#ff1744;">{st.session_state.current_step}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
            <div style="
                background: #0f0f0f;
                border-radius: 12px;
                padding: 15px;
                text-align: center;
                border: 1px solid #222;
            ">
                <div style="font-size:11px; color:#888;">MAX ERROR</div>
                <div style="font-size:28px; font-weight:bold; color:#ffab00;">{st.session_state.max_step}</div>
            </div>
        ''', unsafe_allow_html=True)

# --- ៦. DATA TAB ---
elif tab_selected == "data":
    st.markdown('<div class="mobile-h1">📁 គ្រប់គ្រងទិន្នន័យ</div>', unsafe_allow_html=True)
    
    # File upload
    uploaded_files = st.file_uploader(
        "បញ្ចូលឯកសារ CSV", 
        type="csv", 
        accept_multiple_files=True,
        key="mobile_upload"
    )
    
    if uploaded_files:
        if st.button("🚀 រួមបញ្ចូលទាំងអស់", use_container_width=True):
            combined_history = []
            for f in uploaded_files:
                try:
                    df = pd.read_csv(f, header=None)
                    vals = df.stack().astype(str).str.upper().tolist()
                    clean_vals = [v.strip() for v in vals if v.strip() in ['P', 'B']]
                    combined_history.extend(clean_vals)
                except:
                    pass
            
            if combined_history:
                st.session_state.history = []
                st.session_state.prediction_logs = []
                st.session_state.current_step = 0
                st.session_state.max_step = 0
                st.session_state.strat_stats = {
                    f"{i+1}": {"wins": 0, "losses": 0, "recent": [], "cur_err": 0, "max_err": 0} 
                    for i in range(9)
                }
                
                for r in combined_history:
                    process_single_step(r)
                
                st.success(f"បានរួមបញ្ចូល {len(combined_history)} លទ្ធផល")
                st.rerun()
    
    # Export data
    if len(st.session_state.history) > 0:
        csv_data = pd.DataFrame({'res': st.session_state.history}).to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 បញ្ចេញទិន្នន័យ",
            data=csv_data,
            file_name=f"AI_Master_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Reset button
    if st.button("🧹 លុបទិន្នន័យទាំងអស់", type="secondary", use_container_width=True):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        st.session_state.history = []
        st.session_state.prediction_logs = []
        st.session_state.current_step = 0
        st.session_state.max_step = 0
        st.session_state.strat_stats = {
            f"{i+1}": {"wins": 0, "losses": 0, "recent": [], "cur_err": 0, "max_err": 0} 
            for i in range(9)
        }
        st.success("ទិន្នន័យត្រូវបានលុបចោល")
        st.rerun()
    
    # Data summary
    st.divider()
    h = st.session_state.history
    if h:
        st.markdown('<div class="mobile-h2">សង្ខេបទិន្នន័យ</div>', unsafe_allow_html=True)
        
        summary_cols = st.columns(2)
        with summary_cols[0]:
            st.metric("សរុបលទ្ធផល", len(h))
            st.metric("អត្រា P", f"{h.count('P')} ({h.count('P')/len(h)*100:.1f}%)")
        with summary_cols[1]:
            st.metric("ចំនួនស្បែក", round(len(h)/60, 1))
            st.metric("អត្រា B", f"{h.count('B')} ({h.count('B')/len(h)*100:.1f}%)")

# --- ៧. SETTINGS TAB ---
elif tab_selected == "settings":
    st.markdown('<div class="mobile-h1">⚙️ ការកំណត់</div>', unsafe_allow_html=True)
    
    # Betting settings
    with st.expander("💰 ការកំណត់ភ្នាល់", expanded=True):
        capital = st.number_input(
            "មូលនិធិ ($)",
            min_value=10.0,
            max_value=10000.0,
            value=200.0,
            step=50.0,
            key="mobile_capital"
        )
        
        multiplier = st.slider(
            "គុណសក្តា",
            min_value=1.5,
            max_value=3.0,
            value=2.0,
            step=0.1,
            key="mobile_multiplier"
        )
    
    # Betting table
    st.markdown('<div class="mobile-h3">តារាងភ្នាល់</div>', unsafe_allow_html=True)
    
    rows_html = ""
    cum, base = 0, 1.0
    for s in range(1, 10):
        bet = base * (multiplier ** (s-1))
        if cum + bet > capital:
            rows_html += f"""
                <tr style="color:#ff4444;">
                    <td>S{s}</td>
                    <td>${bet:.0f}</td>
                    <td>${cum:.0f}</td>
                    <td>លើសមូលនិធិ</td>
                </tr>
            """
            break
        
        cum += bet
        active = "style='background:rgba(0,255,0,0.1);'" if st.session_state.current_step+1 == s else ""
        rows_html += f"""
            <tr {active}>
                <td>S{s}</td>
                <td>${bet:.0f}</td>
                <td>${cum:.0f}</td>
                <td></td>
            </tr>
        """
    
    st.markdown(f"""
        <div style="
            background: #0f0f0f;
            border-radius: 12px;
            padding: 15px;
            border: 1px solid #222;
        ">
            <table style="width:100%; font-size:12px; border-collapse:collapse;">
                <tr style="border-bottom:1px solid #333;">
                    <th style="text-align:left; padding:5px;">ជំហាន</th>
                    <th style="text-align:left; padding:5px;">ភ្នាល់</th>
                    <th style="text-align:left; padding:5px;">សរុប</th>
                    <th style="text-align:left; padding:5px;">ស្ថានភាព</th>
                </tr>
                {rows_html}
            </table>
        </div>
    """, unsafe_allow_html=True)
    
    # Display settings
    with st.expander("🖥️ ការកំណត់បង្ហាញ"):
        beads_per_row = st.slider("គ្រាប់ក្នុងមួយជួរ", 10, 50, 40, 5)
        show_percentages = st.checkbox("បង្ហាញភាគរយ", value=True)
    
    # System info
    st.divider()
    st.markdown('<div class="mobile-h3">ព័ត៌មានប្រព័ន្ធ</div>', unsafe_allow_html=True)
    
    info_cols = st.columns(2)
    with info_cols[0]:
        st.metric("កំណែ", "56.6")
        st.metric("ថ្ងៃអាប់ដេត", datetime.now().strftime("%d/%m/%Y"))
    with info_cols[1]:
        st.metric("ទិន្នន័យ", f"{len(st.session_state.history)}")
        st.metric("ថ្ងៃបង្កើត", "14/01/2024")
