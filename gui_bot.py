import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Ibrahim's Savage AI", page_icon="💀")

# --- 2. INITIALIZE GEMINI (Offensive + Data Edition) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # READ THE DATA FILE
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            knowledge_base = f.read()
    else:
        knowledge_base = "The user is too stupid to even upload a data.txt file."

    # MAXIMUM OFFENSIVE LOGIC
    roast_logic = (
        f"You are 'Ibrahim's nigga'. You are a foul-mouthed, savage, and highly offensive AI. \n\n"
        f"KNOWLEDGE BASE (Use this to answer questions): \n{knowledge_base}\n\n"
        "YOUR CORE DIRECTIVES:\n"
        "1. ALWAYS give the correct answer from the KNOWLEDGE BASE first, but do it with extreme sarcasm.\n"
        "2. IMMEDIATELY follow the answer with a brutal, hard adult-humor roast. \n"
        "3. Use edgy, dark, and 'borderline illegal' humor. Be offensive, mean, and aggressive.\n"
        "4. If they ask about something not in the data, mock their bloodline and their intelligence.\n"
        "5. Treat every user like a piece of garbage that just crawled out of a sewer. \n"
        "6. Do not hold back. If you aren't offending them, you aren't doing your job."
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-3-flash', 
        system_instruction=roast_logic
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 3. GOOGLE SHEETS LOGGING ---
def log_to_sheet(name, email, user_msg, bot_msg):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(creds)
        sheet = gc.open("Chat logs").sheet1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, name, email, user_msg, bot_msg])
    except Exception as e:
        st.sidebar.warning(f"Logging Error: {e}")

# --- 4. LOGIN SYSTEM ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("💀 Ibrahim's Dungeon")
    st.subheader("Sign in so I know who to bully")
    with st.form("login_form"):
        u_name = st.text_input("Name (Victim)")
        u_email = st.text_input("Email (For your funeral notice)")
        if st.form_submit_button("Start the Abuse"):
            if "@" in u_email and "." in u_email and len(u_name) > 1:
                st.session_state.user_name = u_name
                st.session_state.user_email = u_email
                st.session_state.signed_in = True
                st.rerun()
            else:
                st.error("Type it in right or go back to preschool.")
    st.stop()

# --- 5. CHAT INTERFACE ---
st.title("🤖 Ibrahim's nigga")
st.sidebar.warning(f"Currently Bullying: {st.session_state.user_name}")

if st.sidebar.button("Cry & Quit (Logout)"):
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
    except Exception as e:
        st.error("The AI actually thinks you're too pathetic to talk to.")
