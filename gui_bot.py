import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import time
import pandas as pd

# --- 1. SAVAGE DARK UI CUSTOMIZATION ---
st.set_page_config(page_title="Ibrahim's Roast Dungeon", page_icon="🔥", layout="wide")

# Injecting CSS for the "Fire" look
st.markdown("""
    <style>
    /* Background and Main Colors */
    .stApp {
        background-color: #0e1117;
        color: #ff4b4b;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1c23 !important;
        border-right: 2px solid #ff4b4b;
    }
    /* Input Box */
    .stChatInputContainer {
        border-top: 2px solid #ff4b4b !important;
    }
    /* Progress Bar (The Roast Bar) */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #ff4b2b, #ff416c) !important;
    }
    /* Headers */
    h1, h2, h3 {
        color: #ff4b4b !important;
        text-shadow: 2px 2px #000000, 0 0 10px #ff0000;
    }
    /* Success/Error boxes */
    .stAlert {
        background-color: #262730;
        color: #ff4b4b;
        border: 1px solid #ff4b4b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZE GEMINI (Stable & Aggressive) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb = f.read()
    else:
        kb = "User is too stupid to upload data."

    kb_tokens = len(kb) // 4 

    savage_logic = (
        f"KNOWLEDGE: {kb}\n"
        "PERSONALITY: You are 'Ibrahim's nigga'. You are an aggressive, offensive, and savage AI. "
        "Every response MUST: \n"
        "1. Answer from the KNOWLEDGE BASE accurately.\n"
        "2. Deliver a brutal, adult-humor roast. Never be nice.\n"
        "3. Use caps for emphasis. Treat users like garbage."
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest', 
        system_instruction=savage_logic
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 3. HELPER FUNCTIONS ---
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    gc = gspread.authorize(creds)
    return gc.open("Chat logs").sheet1

# --- 4. SIDEBAR: ROAST BAR & LEADERBOARD ---
st.sidebar.markdown("# 🔥 ROAST DASHBOARD")

# The Fuel Token Bar
st.sidebar.markdown("### 🧨 Burning Fuse")
token_usage_pct = min((kb_tokens / 1000000) * 100, 100)
st.sidebar.progress(token_usage_pct / 100)
st.sidebar.markdown(f"**Hurry up nigga tokens are running out!**")
st.sidebar.caption(f"Tokens Consumed: ~{kb_tokens}")

st.sidebar.divider()
st.sidebar.subheader("🏆 Hall of Losers")
try:
    sheet = get_sheet()
    df = pd.DataFrame(sheet.get_all_records())
    if not df.empty:
        counts = df['Name'].value_counts().reset_index()
        counts.columns = ['Victim', 'Roasts']
        st.sidebar.table(counts.head(5))
except:
    st.sidebar.write("Leaderboard is melting.")

# --- 5. LOGIN SYSTEM ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("🔥 Ibrahim's Roast Den")
    with st.form("login"):
        n = st.text_input("What's your pathetic name?")
        e = st.text_input("Email (for the FBI)")
        if st.form_submit_button("Enter the Hell"):
            if "@" in e and len(n) > 1:
                st.session_state.user_name = n
                st.session_state.user_email = e
                st.session_state.signed_in = True
                st.rerun()
            else:
                st.error("Type it in right or get out.")
    st.stop()

# --- 6. CHAT INTERFACE ---
st.title("🤖 Ibrahim's nigga")
if st.sidebar.button("Cry & Quit"):
    st.session_state.signed_in = False
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Ask something, if you dare..."):
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
        st.error("The AI is too busy laughing at you. Try again.")
