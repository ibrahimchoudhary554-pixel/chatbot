import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import pandas as pd

# --- NOIR THEME ---
st.set_page_config(page_title="Terminal", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #222; }
    .stChatInputContainer { border-top: 1px solid #222 !important; }
    h1, h2, h3, p, span { font-family: 'Inter', sans-serif !important; color: #EEE !important; }
    .stTable { background-color: #000; border: 1px solid #333; }
    .stButton>button { background-color: #FFF !important; color: #000 !important; border-radius: 0px; width: 100%; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# --- SYSTEM BRAIN ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    kb = open("data.txt", "r").read() if os.path.exists("data.txt") else "Empty knowledge base."
    
    # Using stable identifier to stop the 404 v1beta cycle
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=(
            f"DATA: {kb}\n"
            "SYSTEM: You are a high-IQ, cold, savage AI terminal. "
            "1. Answer queries using the DATA accurately. "
            "2. Follow with a brutal, adult-humor roast. "
            "3. Strictly Black & White. No emojis. Be funny as hell."
        )
    )
except Exception as e:
    st.error(f"SYSTEM_FAILURE: {e}")
    st.stop()

def get_sheet():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], 
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    return gspread.authorize(creds).open("Chat logs").sheet1

# --- SIDEBAR SCOREBOARD ---
st.sidebar.title("SYSTEM_RESOURCES")
if "tokens" not in st.session_state: st.session_state.tokens = 0
st.sidebar.write(f"TOKEN_BURN: {st.session_state.tokens}")

st.sidebar.subheader("HALL_OF_LOSERS")
try:
    df = pd.DataFrame(get_sheet().get_all_records())
    if not df.empty:
        counts = df['Name'].value_counts().reset_index()
        counts.columns = ['Victim', 'Roasts']
        st.sidebar.table(counts.head(5))
except:
    st.sidebar.write("Syncing scoreboard...")

# --- AUTH ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("AUTH_REQUIRED")
    with st.form("login"):
        n, e = st.text_input("ID"), st.text_input("EMAIL")
        if st.form_submit_button("LOGIN"):
            if "@" in e and n:
                st.session_state.user_name, st.session_state.auth = n, True
                st.rerun()
    st.stop()

# --- TERMINAL ---
st.title("TERMINAL")
if "msgs" not in st.session_state: st.session_state.msgs = []

for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Enter command..."):
    st.session_state.msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    try:
        response = model.generate_content(prompt, safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}
        ])
        res = response.text
        st.session_state.tokens += (len(prompt) + len(res)) // 4
        
        with st.chat_message("assistant"): st.markdown(res)
        st.session_state.msgs.append({"role": "assistant", "content": res})
        get_sheet().append_row([datetime.now().strftime("%Y-%m-%d"), st.session_state.user_name, "User", prompt, res])
    except Exception as e:
        st.error(f"CRASH: {e}")
