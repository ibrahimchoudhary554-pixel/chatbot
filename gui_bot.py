#import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import time
import pandas as pd --- 6. CHAT ---
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
        # 🔓 BYPASS SAFETY FILTERS so the roast actually works
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        ]

        response = model.generate_content(prompt, safety_settings=safety_settings)
        
        if response.text:
            answer = response.text
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            # Log to Sheet
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            get_sheet().append_row([timestamp, st.session_state.user_name, st.session_state.user_email, prompt, answer])
        else:
            st.warning("The AI was so offended by your face it stayed silent. Try a different prompt.")

    except Exception as e:
        # ⚠️ THIS WILL SHOW THE ACTUAL ERROR MESSAGE
        st.error(f"SYSTEM OVERLOAD: {e}")

