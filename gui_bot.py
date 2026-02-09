import streamlit as st
from openai import OpenAI
import os

# --- 1. UI & WATERMARK SETTINGS ---
st.set_page_config(page_title="Ibrahim's Roast Dungeon", page_icon="🔥", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ff4b4b; }
    .watermark { position: fixed; opacity: 0.4; color: white; font-size: 14px; z-index: 99; }
    .top-r { top: 10px; right: 10px; }
    .bot-r { bottom: 10px; right: 10px; }
    .model-box { border: 2px solid #ff0000; padding: 15px; border-radius: 10px; background-color: #1a0000; margin-bottom: 20px; }
    .disclaimer-box { 
        border: 1px dashed #ffffff; 
        padding: 10px; 
        border-radius: 5px; 
        background-color: #330000; 
        color: #ffffff; 
        text-align: center;
        font-size: 14px;
        margin-bottom: 15px;
    }
    </style>
    <div class="watermark top-r">@ibrahimchoudhary__</div>
    <div class="watermark bot-r">@ibrahimchoudhary__</div>
    """, unsafe_allow_html=True)

# --- 2. ENTERTAINMENT DISCLAIMER ---
st.markdown("""
    <div class="disclaimer-box">
        <strong>⚠️ ENTERTAINMENT ONLY:</strong> This chatbot is for comedic and entertainment purposes only. 
        The roasts generated are randomized AI humor and Ibrahim holds no personal ill-will or 
        malice toward any of the individuals mentioned. It's just a joke!
    </div>
    """, unsafe_allow_html=True)

# --- 3. HARD-CODED SAFE LIST ---
SAFE_NAMES = ["ibrahim", "owner", "zainab", "king", "boss"]

# --- 4. UI & MODEL SWITCHER ---
st.title("🤖 Ibrahim's Roast Bot")

with st.container():
    st.markdown('<div class="model-box">', unsafe_allow_html=True)
    st.error("🚨 **CRASH PROTECTION & MODEL CONTROL**")
    model_choice = st.selectbox(
        "SWITCH MODEL IF BOT ACTS UP:",
        ["meta-llama/Llama-3.1-8B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3"]
    )
    st.info("Report bugs/complaints to Instagram: **[ibrahimchoudhary__](https://instagram.com/ibrahimchoudhary__)**")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. DATA LOADING ---
if os.path.exists("data.txt"):
    with open("data.txt", "r") as f:
        kb = f.read()
else:
    kb = "No data.txt found."

# --- 6. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Enter a name..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_box = st.empty()
        
        # --- THE HARD FILTER ---
        is_safe = any(name in prompt.lower() for name in SAFE_NAMES)
        
        if is_safe:
            # LOYAL BUTLER MODE
            system_instruction = (
                f"KNOWLEDGE: {kb}\n"
                "ROLE: You are Ibrahim's loyal bodyguard. Ibrahim or a VIP is speaking. "
                "Be extremely polite, humble, and helpful. DO NOT ROAST. "
                "Speak like a professional assistant. No CAPS, no insults."
            )
        else:
            # SAVAGE ROAST MODE
            system_instruction = (
                f"KNOWLEDGE: {kb}\n"
                "ROLE: You are Ibrahim's brutal roast bot. Be savage. Use adult humor. "
                "Roast everyone NOT in the safe list. Focus on Hamza, Mohid, and Qasim (Princess)."
            )

        try:
            client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=st.secrets["HF_TOKEN"])
            response = client.chat.completions.create(
                model=model_choice,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.85
            )
            answer = response.choices[0].message.content
            response_box.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"System Overload. Switch models or wait 5 mins. Report: @ibrahimchoudhary__")
