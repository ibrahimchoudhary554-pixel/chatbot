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
    /* High Contrast Black & White */
    .stApp { background-color: #000000; color: #FFFFFF; }
    section[data-testid="stSidebar"] { 
        background-color: #050505 !important; 
        border-right: 1px solid #1A1A1A; 
    }
    .stChatInputContainer { border-top: 1px solid #1A1A1A !important; }
    
    /* Clean Typography */
    h1, h2, h3, p, span, label { 
        font-family: 'Inter', sans-serif !important;
        color: #FFFFFF !important;
    }

    /* Scoreboard Styling */
    .stTable { 
        background-color: #000000; 
        border: 1px solid #333333;
    }

    /* Modern Minimalist Button */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 0px;
        border: none;
        width: 100%;
        font-weight: 900;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE BRAIN (404 FIX) ---
try:
    # We use the standard config to avoid v1beta errors
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb_content = f.read()
    else:
        kb_content = "The data file is missing, just like the user's brain cells."

    # Using the stable model identifier
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=(
            f"KNOWLEDGE_BASE: {kb_content}\n"
            "ROLE: You are an elite, professional, yet absolutely savage AI terminal. "
            "1. Answer queries accurately using the KNOWLEDGE_BASE. "
            "2. Follow every answer with a high-IQ, brutal roast. "
            "3. Zero emojis. Strictly black-and-white humor. Be hilarious but mean."
        )
    )
except Exception as e:
    st.error(f"FATAL_ERROR: {e}")
    st.stop()

def get_sheet():
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    return gspread.authorize(creds).open("Chat logs").sheet1

# --- 3. SIDEBAR (LOGS & TOKENS) ---
st.sidebar.title("SYSTEM_RESOURCES")

# Token Counter (Simulated)
if "tokens" not in st.session_state:
    st.session_state.tokens = 0
st.sidebar.write(f"TOKENS_BURNED: {st.session_state.tokens}")
st.sidebar.progress(min(st.session_state.tokens / 50000, 1.0))

# Roast Scoreboard (Hall of Losers)
st.sidebar.subheader("VICTIM_RANKING")
try:
    data = get_sheet().get_all_records()
    if data:
        df = pd.DataFrame(data)
        counts = df['Name'].value_counts().reset_index()
        counts.columns = ['Victim', 'Roasts']
        st.sidebar.table(counts.head(5))
except:
    st.sidebar.write("Leaderboard currently offline.")

# --- 4. AUTH ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("AUTHENTICATION_REQUIRED")
    with st.form("login"):
        n = st.text_input("IDENTIFIER (NAME)")
        e = st.text_input("CREDENTIAL (EMAIL)")
        if st.form_submit_button("ESTABLISH_CONNECTION"):
            if "@" in e and n:
                st.session_state.user_name = n
                st.session_state.user_email = e
                st.session_state.signed_in = True
                st.rerun()
    st.stop()

# --- 5. CHAT TERMINAL ---
st.title("COMMAND_LINE_INTERFACE")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Enter command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Safety settings to allow the roast to happen
        safety = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        ]
        
        response = model.generate_content(prompt, safety_settings=safety)
        answer = response.text
        
        # Update Tokens (Approximate)
        st.session_state.tokens += (len(prompt) + len(answer)) // 4
        
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Log to Sheet
        get_sheet().append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.user_name, st.session_state.user_email, prompt, answer])
        
    except Exception as e:
        st.error(f"TERMINAL_CRASH: {e}")
