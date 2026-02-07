import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import time
import pandas as pd

# --- 1. THE HELLFIRE UI (CUSTOM CSS) ---
st.set_page_config(page_title="Ibrahim's Roast Dungeon", page_icon="🔥", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ff4b4b; }
    section[data-testid="stSidebar"] { 
        background-color: #0a0a0a !important; 
        border-right: 3px solid #ff0000; 
    }
    .stChatInputContainer { border-top: 2px solid #ff4b4b !important; }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #ff0000, #ff8c00) !important;
    }
    h1, h2, h3 { 
        color: #ff4b4b !important; 
        text-shadow: 0 0 10px #ff0000;
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton>button {
        background-color: #ff0000 !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #8b0000 !important;
        box-shadow: 0 0 15px #ff0000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZE GEMINI 1.5 FLASH LATEST ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb = f.read()
    else:
        kb = "User is too incompetent to provide a knowledge base."

    kb_tokens = len(kb) // 4 

    savage_logic = (
        f"KNOWLEDGE: {kb}\n"
        "PERSONALITY: You are 'Ibrahim's nigga'. You are an aggressive, offensive, and savage AI. "
        "Every response MUST: \n"
        "1. Give the correct answer from the KNOWLEDGE BASE first.\n"
        "2. Deliver a brutal, adult-humor roast. Never be nice.\n"
        "3. Use caps for emphasis. If the user is a cousin or friend mentioned in data, destroy them."
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest', 
        system_instruction=savage_logic
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 3. GOOGLE SHEETS HELPER ---
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    gc = gspread.authorize(creds)
    return gc.open("Chat logs").sheet1

# --- 4. SIDEBAR DASHBOARD ---
st.sidebar.markdown("# 💀 SYSTEM STATUS")

# The Fuel Token Bar
st.sidebar.markdown("### 🧨 BURNING FUSE")
token_usage_pct = min((kb_tokens / 1000000) * 100, 100)
st.sidebar.progress(token_usage_pct / 100)
st.sidebar.markdown(f"<p style='color:#ff8c00; font-size:14px;'><b>Hurry up nigga tokens are running out!</b></p>", unsafe_allow_html=True)

# SELF-DESTRUCT BUTTON
st.sidebar.divider()
if st.sidebar.button("💥 SELF-DESTRUCT"):
    st.session_state.messages = []
    st.toast("EVIDENCE WIPED. SYSTEM CLEANSED.")
    time.sleep(1)
    st.rerun()

# Hall of Losers
st.sidebar.subheader("🏆 HALL OF LOSERS")
try:
    sheet = get_sheet()
    df = pd.DataFrame(sheet.get_all_records())
    if not df.empty:
        counts = df['Name'].value_counts().reset_index()
        counts.columns = ['Victim', 'Roasts']
        st.sidebar.table(counts.head(5))
except:
    st.sidebar.write("Leaderboard is ashes.")

# --- 5. LOGIN ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("🔥 Ibrahim's Roast Den")
    with st.form("login"):
        n = st.text_input("Name (Victim)")
        e = st.text_input("Email (Evidence)")
        if st.form_submit_button("ENTER THE FIRE"):
            if "@" in e and len(n) > 1:
                st.session_state.user_name = n
                st.session_state.user_email = e
                st.session_state.signed_in = True
                st.rerun()
            else:
                st.error("Fill it out right, you absolute donut.")
    st.stop()

# --- 6. CHAT ---
st.title("🤖 Ibrahim's nigga")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Say something stupid..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = model.generate_content(prompt)
        answer = response.text
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Log to Sheet
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        get_sheet().append_row([timestamp, st.session_state.user_name, st.session_state.user_email, prompt, answer])
    except:
        st.error("The AI is too busy laughing at you. Probably a safety filter triggered by your stupidity.")