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

# --- 2. INITIALIZE GEMINI (Nuclear Level) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb = f.read()
    else:
        kb = "User is too incompetent to provide data."

    savage_logic = (
        f"KNOWLEDGE: {kb}\n"
        "PERSONALITY: You are 'Ibrahim's nigga'. You are an aggressive, offensive, and savage AI. "
        "Every response MUST: \n"
        "1. Answer from the KNOWLEDGE BASE first (be accurate).\n"
        "2. Follow up with a brutal, adult-humor roast.\n"
        "3. Be as offensive and funny as possible without getting the account banned.\n"
        "4. Mock their name, their questions, and their life choices."
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest', 
        system_instruction=savage_logic
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 3. GOOGLE SHEETS & LEADERBOARD LOGIC ---
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    gc = gspread.authorize(creds)
    return gc.open("Chat logs").sheet1

def log_to_sheet(name, email, user_msg, bot_msg):
    try:
        time.sleep(1) # Protect against 403 ban
        sheet = get_sheet()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, name, email, user_msg, bot_msg])
    except:
        pass

# --- 4. LOGIN ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("💀 Welcome to the Dungeon")
    with st.form("login"):
        n = st.text_input("Name (Victim)")
        e = st.text_input("Email")
        if st.form_submit_button("Start the Abuse"):
            if "@" in e and len(n) > 1:
                st.session_state.user_name = n
                st.session_state.user_email = e
                st.session_state.signed_in = True
                st.rerun()
    st.stop()

# --- 5. SIDEBAR LEADERBOARD ---
st.sidebar.title("🏆 Hall of Losers")
try:
    sheet = get_sheet()
    data = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        # Count roasts per name
        counts = df['Name'].value_counts().reset_index()
        counts.columns = ['Victim', 'Roasts Received']
        st.sidebar.table(counts.head(5))
except:
    st.sidebar.write("Leaderboard is broken, just like your life.")

# --- 6. CHAT INTERFACE ---
st.title("🤖 Ibrahim's nigga")
if st.sidebar.button("Cry & Logout"):
    st.session_state.signed_in = False
    st.rerun()

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
        log_to_sheet(st.session_state.user_name, st.session_state.user_email, prompt, answer)
    except:
        st.error("AI is busy laughing at you. Try again.")
