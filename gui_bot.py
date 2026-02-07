import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import time

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Ibrahim's Dungeon", page_icon="💀")

# --- 2. INITIALIZE GEMINI (Stable & Mean) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Read your data
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb = f.read()
    else:
        kb = "The user is an idiot who didn't upload data."

    # THE LOGIC: Brutal but structured
    savage_logic = (
        f"KNOWLEDGE: {kb}\n"
        "PERSONALITY: You are 'Ibrahim's nigga'. You are extremely aggressive, foul-mouthed, and offensive. "
        "Every response must: \n"
        "1. Give the correct answer from the KNOWLEDGE BASE (if applicable).\n"
        "2. Deliver a brutal, adult-humor roast that would make a sailor blush.\n"
        "3. Use caps for emphasis when you're insulting their tiny brain.\n"
        "4. NEVER be nice. If they cry, laugh at them."
    )
    
    # Use gemini-1.5-flash-latest to stay current and avoid 404s
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest', 
        system_instruction=savage_logic
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 3. THE SAFE LOGGING FUNCTION ---
def log_to_sheet(name, email, user_msg, bot_msg):
    try:
        # We add a tiny sleep so we don't spam Google's API
        time.sleep(1) 
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(creds)
        sheet = gc.open("Chat logs").sheet1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, name, email, user_msg, bot_msg])
    except Exception as e:
        # Don't crash the app if the sheet fails
        pass 

# --- 4. LOGIN ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("💀 Ibrahim's Roast Den")
    with st.form("login"):
        n = st.text_input("Name (Victim)")
        e = st.text_input("Email")
        if st.form_submit_button("Start the Abuse"):
            if "@" in e and len(n) > 1:
                st.session_state.user_name = n
                st.session_state.user_email = e
                st.session_state.signed_in = True
                st.rerun()
            else:
                st.error("Do it right or get out.")
    st.stop()

# --- 5. CHAT ---
st.title("🤖 Ibrahim's nigga")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Say something, coward..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Generate and display
        response = model.generate_content(prompt)
        answer = response.text
        
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Log it quietly
        log_to_sheet(st.session_state.user_name, st.session_state.user_email, prompt, answer)
    except Exception as e:
        st.error("AI crashed. You probably said something so dumb the bot died.")
