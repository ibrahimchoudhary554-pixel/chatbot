import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import pandas as pd

# --- 1. NOIR MODERN UI ---
st.set_page_config(page_title="Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    section[data-testid="stSidebar"] { 
        background-color: #050505 !important; 
        border-right: 1px solid #222222; 
    }
    .stChatInputContainer { border-top: 1px solid #222222 !important; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -1px; }
    .stTable { background-color: #000000; color: #FFFFFF; }
    /* Modern Button */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 0px;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE BRAIN ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Load your data file
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb_content = f.read()
    else:
        kb_content = "No data provided."

    # FIXED MODEL NAME: use 'gemini-1.5-flash' instead of 'latest' strings that break
    savage_logic = (
        f"DATA_FILE_CONTENT: {kb_content}\n"
        "INSTRUCTIONS: You are a savage, hilarious AI roaster. "
        "1. Always answer the user's question accurately using the DATA_FILE_CONTENT.\n"
        "2. After the answer, deliver a brutal, adult-humor roast.\n"
        "3. No emojis. Keep it cold, black-and-white, and mean."
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash', 
        system_instruction=savage_logic
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

def get_sheet():
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    return gspread.authorize(creds).open("Chat logs").sheet1

# --- 3. SIDEBAR (SCOREBOARD & TOKENS) ---
st.sidebar.title("VICTIM LOGS")

# Token Counter (Simulated based on text length)
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
st.sidebar.write(f"TOKENS CONSUMED: {st.session_state.total_tokens}")
st.sidebar.progress(min(st.session_state.total_tokens / 10000, 1.0))

# Roast Scoreboard
st.sidebar.subheader("HALL OF LOSERS")
try:
    sheet = get_sheet()
    data = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        scoreboard = df['Name'].value_counts().reset_index()
        scoreboard.columns = ['Victim', 'Roasts']
        st.sidebar.table(scoreboard.head(5))
except:
    st.sidebar.write("Leaderboard offline.")

# --- 4. LOGIN ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("AUTH_REQUIRED")
    with st.form("login"):
        n = st.text_input("NAME")
        e = st.text_input("EMAIL")
        if st.form_submit_button("PROCEED"):
            if "@" in e and n:
                st.session_state.user_name = n
                st.session_state.user_email = e
                st.session_state.signed_in = True
                st.rerun()
    st.stop()

# --- 5. CHAT TERMINAL ---
st.title("TERMINAL")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        safety = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        ]
        
        response = model.generate_content(prompt, safety_settings=safety)
        answer = response.text
        
        # Update token count
        st.session_state.total_tokens += (len(prompt) + len(answer)) // 4
        
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Log to Sheet
        get_sheet().append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.user_name, st.session_state.user_email, prompt, answer])
        
    except Exception as e:
        st.error(f"SYSTEM_FAILURE: {e}")
