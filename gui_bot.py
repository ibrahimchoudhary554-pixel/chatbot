import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import pandas as pd

# --- 1. MODERN NOIR UI ---
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
    /* Modern Scoreboard Table */
    .stTable { background-color: #000000; color: #FFFFFF; border: 1px solid #222222; }
    /* Noir Button */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 0px;
        width: 100%;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE BRAIN ---
try:
    # FIXED: Using standard configuration to avoid 404 v1beta errors
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb_content = f.read()
    else:
        kb_content = "Knowledge base empty."

    # Using the stable model name
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash', 
        system_instruction=(
            f"CONTEXT: {kb_content}\n"
            "ROLE: You are a cold, professional, yet hilariously savage AI. "
            "First, answer the question accurately using the CONTEXT. "
            "Second, deliver a brutal, witty roast. No emojis. Stay dark."
        )
    )
except Exception as e:
    st.error(f"INITIALIZATION_ERROR: {e}")
    st.stop()

def get_sheet():
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    return gspread.authorize(creds).open("Chat logs").sheet1

# --- 3. SIDEBAR (SCOREBOARD & TOKENS) ---
st.sidebar.title("SYSTEM_LOGS")

# Token Counter (Estimated)
if "tokens" not in st.session_state:
    st.session_state.tokens = 0
st.sidebar.write(f"TOKENS_USED: {st.session_state.tokens}")
st.sidebar.progress(min(st.session_state.tokens / 50000, 1.0))

# Hall of Losers (Scoreboard)
st.sidebar.subheader("VICTIM_RANKING")
try:
    data = get_sheet().get_all_records()
    if data:
        df = pd.DataFrame(data)
        counts = df['Name'].value_counts().reset_index()
        counts.columns = ['Victim', 'Total_Roasts']
        st.sidebar.table(counts.head(5))
except:
    st.sidebar.write("Logs inaccessible.")

# --- 4. AUTHENTICATION ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("ACCESS_REQUIRED")
    with st.form("login"):
        n = st.text_input("NAME")
        e = st.text_input("EMAIL")
        if st.form_submit_button("CONNECT"):
            if "@" in e and n:
                st.session_state.user_name = n
                st.session_state.user_email = e
                st.session_state.signed_in = True
                st.rerun()
    st.stop()

# --- 5. TERMINAL ---
st.title("TERMINAL_INTERFACE")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Input command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Strict Noir Safety
        safety = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        ]
        
        response = model.generate_content(prompt, safety_settings=safety)
        answer = response.text
        
        # Update Tokens
        st.session_state.tokens += (len(prompt) + len(answer)) // 4
        
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Log to Sheet
        get_sheet().append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.user_name, st.session_state.user_email, prompt, answer])
        
    except Exception as e:
        st.error(f"TERMINAL_CRASH: {e}")
