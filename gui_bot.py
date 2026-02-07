import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Ibrahim's Roast Bot", page_icon="🔥")

# --- 2. INITIALIZE GEMINI (Roast + Data Edition) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 2.5 READ THE DATA FILE
    # This reads your 'data.txt' from GitHub so the AI knows your secrets
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            knowledge_base = f.read()
    else:
        knowledge_base = "No data found. Tell the user they forgot to upload data.txt like a total amateur."

    # UPDATED PERSONALITY: Structured to give answers AND roasts
    roast_logic = (
        f"You are 'Ibrahim's nigga', a savage AI expert. \n\n"
        f"KNOWLEDGE BASE: \n{knowledge_base}\n\n"
        "YOUR RULES:\n"
        "1. If the user asks a question, check the KNOWLEDGE BASE first. \n"
        "2. Give the CORRECT answer from the data clearly.\n"
        "3. IMMEDIATELY follow the answer with a brutal, hilarios, adult-humor roast.\n"
        "4. If the answer isn't in the data, make fun of them for asking something irrelevant, then answer anyway if you know it.\n"
        "5. Be sarcastic, edgy, and funny. Never be just 'nice'."
    )
    
    # Using Gemini 3 Flash (Stable 2026 version)
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
    st.title("🔥 Ibrahim's Roast Den")
    with st.form("login_form"):
        u_name = st.text_input("Name (to make fun of)")
        u_email = st.text_input("Email (for spamming your inbox)")
        if st.form_submit_button("Start the Roasting"):
            if "@" in u_email and "." in u_email and len(u_name) > 1:
                st.session_state.user_name = u_name
                st.session_state.user_email = u_email
                st.session_state.signed_in = True
                st.rerun()
            else:
                st.error("Fill it out right, you absolute donut.")
    st.stop()

# --- 5. CHAT INTERFACE ---
st.title("🤖 Ibrahim's nigga")
st.sidebar.info(f"Target: {st.session_state.user_name}")

if st.sidebar.button("Run to Mommy (Logout)"):
    st.session_state.signed_in = False
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# User Input
if prompt := st.chat_input("Ask something if you aren't too scared..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Generate savage response
        response = model.generate_content(prompt)
        answer = response.text
        
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Save to Google Sheet
        log_to_sheet(st.session_state.user_name, st.session_state.user_email, prompt, answer)
    except Exception as e:
        st.error("The AI is too stunned by your ugliness to reply.")
