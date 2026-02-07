import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import time
import pandas as pd

# --- 1. MODERN NOIR UI ---
st.set_page_config(page_title="Dungeon", layout="wide")

st.markdown("""
    <style>
    /* Black and White Theme */
    .stApp { background-color: #000000; color: #FFFFFF; }
    section[data-testid="stSidebar"] { 
        background-color: #0A0A0A !important; 
        border-right: 1px solid #333333; 
    }
    .stChatInputContainer { border-top: 1px solid #333333 !important; }
    
    /* Clean Typography */
    h1, h2, h3, p { 
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.5px;
    }
    
    /* Hide Streamlit Cringe */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Modern Buttons */
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 2px;
        border: none;
        font-size: 12px;
        text-transform: uppercase;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE LOGIC ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb = f.read()
    else:
        kb = "Knowledge base missing."

    savage_logic = (
        f"KNOWLEDGE: {kb}\n"
        "SYSTEM: You are a professional, savage AI. "
        "Provide factual answers from the knowledge base, then deliver a brutal roast. "
        "No emojis. No fluff. Just cold, hard facts and colder insults."
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest', 
        system_instruction=savage_logic
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    gc = gspread.authorize(creds)
    return gc.open("Chat logs").sheet1

# --- 3. SIDEBAR ---
st.sidebar.title("SYSTEM")
if st.sidebar.button("WIPE SESSION"):
    st.session_state.messages = []
    st.rerun()

# --- 4. LOGIN ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("AUTHENTICATION")
    with st.form("login"):
        n = st.text_input("NAME")
        e = st.text_input("EMAIL")
        if st.form_submit_button("ACCESS"):
            if "@" in e and len(n) > 1:
                st.session_state.user_name = n
                st.session_state.user_email = e
                st.session_state.signed_in = True
                st.rerun()
            else:
                st.error("Invalid credentials.")
    st.stop()

# --- 5. CHAT ---
st.title("TERMINAL")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Enter query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        safety = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        ]
        response = model.generate_content(prompt, safety_settings=safety)
        
        if response.text:
            answer = response.text
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            # Async logging
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            get_sheet().append_row([timestamp, st.session_state.user_name, st.session_state.user_email, prompt, answer])
    except Exception as e:
        st.error(f"Status: {e}")
