import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import time
import pandas as pd

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Ibrahim's Roast Dungeon", page_icon="💀")

# --- 2. INITIALIZE GEMINI & TOKEN TRACKER ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb = f.read()
    else:
        kb = "The user is too lazy to upload data.txt."

    # Estimate tokens: ~4 chars per token
    kb_tokens = len(kb) // 4 
    
    savage_logic = (
        f"KNOWLEDGE: {kb}\n"
        "PERSONALITY: You are 'Ibrahim's nigga'. You are aggressive, offensive, and savage. "
        "Every response MUST: \n"
        "1. Answer from the KNOWLEDGE BASE first.\n"
        "2. Deliver a brutal roast. Never be nice.\n"
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest', 
        system_instruction=savage_logic
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 3. LOGGING & DATA FUNCTIONS ---
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    gc = gspread.authorize(creds)
    return gc.open("Chat logs").sheet1

# --- 4. SIDEBAR: THE FUEL GAUGE & LEADERBOARD ---
st.sidebar.title("💀 Roast Dashboard")

# Token Counter
st.sidebar.subheader("🔥 Insult Fuel")
token_usage_pct = min((kb_tokens / 1000000) * 100, 100) # Against 1M TPM limit
st.sidebar.progress(token_usage_pct / 100)
st.sidebar.write(f"Knowledge Base: ~{kb_tokens} tokens")
st.sidebar.caption("If this hits 100%, the AI will stop responding.")

# Hall of Losers
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
    st.sidebar.write("Leaderboard is offline.")

# --- 5. CHAT SYSTEM ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("🔥 Ibrahim's Roast Den")
    with st.form("login"):
        n = st.text_input("Name")
        e = st.text_input("Email")
        if st.form_submit_button("Start the Pain"):
            if "@" in e and len(n) > 1:
                st.session_state.user_name = n
                st.session_state.user_email = e
                st.session_state.signed_in = True
                st.rerun()
    st.stop()

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
        
    except Exception as e:
        st.error("AI is dead. You probably exceeded your free token limit for the minute.")
