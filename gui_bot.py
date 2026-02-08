import streamlit as st
from openai import OpenAI
import os
import time

# --- 1. UI & WATERMARK SETTINGS ---
st.set_page_config(page_title="Ibrahim's Roast Dungeon", page_icon="🔥", layout="wide")

# Custom CSS for prominent styling and 3 Watermarks
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ff4b4b; }
    
    /* Watermarks */
    .watermark-top { position: fixed; top: 10px; right: 10px; opacity: 0.4; color: white; font-size: 14px; z-index: 99; }
    .watermark-bottom { position: fixed; bottom: 10px; right: 10px; opacity: 0.4; color: white; font-size: 14px; z-index: 99; }
    .sidebar-watermark { text-align: center; opacity: 0.8; color: #ff4b4b; font-size: 16px; font-weight: bold; margin-top: 50px; }
    
    /* Emergency Switcher Highlight */
    .model-box {
        border: 2px solid #ff0000;
        padding: 15px;
        border-radius: 10px;
        background-color: #1a0000;
        margin-bottom: 20px;
    }
    
    h1 { color: #ff4b4b !important; text-shadow: 0 0 10px #ff0000; }
    </style>
    
    <div class="watermark-top">@ibrahimchoudhary__</div>
    <div class="watermark-bottom">@ibrahimchoudhary__</div>
    """, unsafe_allow_html=True)

# --- 2. CRASH NOTE & EMERGENCY SWITCHER ---
st.title("🤖 Ibrahim's Roast Bot")

# Making the model shifting prominent in the main view
with st.container():
    st.markdown('<div class="model-box">', unsafe_allow_html=True)
    st.error("🚨 **CRASH PROTECTION SYSTEM**")
    st.write("If the bot stops responding, **SWITCH THE MODEL BELOW** immediately.")
    
    # Prominent Model Switcher on Main Page
    model_choice = st.selectbox(
        "CURRENT ACTIVE WEAPON (MODEL):",
        ["meta-llama/Llama-3.1-8B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3"],
        help="If one model is laggy, flip to the other one!"
    )
    
    st.info("⚠️ **WAIT 5 MINUTES** before reporting errors to Instagram: **[ibrahimchoudhary__](https://instagram.com/ibrahimchoudhary__)**")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. INITIALIZE CLIENT ---
try:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=st.secrets["HF_TOKEN"]
    )
    
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb = f.read()
    else:
        kb = "Data file missing. Ibrahim's cousins are safe for now."

    savage_logic = (
        f"KNOWLEDGE: {kb}\n"
        "PERSONALITY: You are Ibrahim's aggressive assistant. "
        "Roast the users based on the KNOWLEDGE provided. Be savage. Use adult humor. "
        "Don't hold back on Hamza (pot-head), Mohid (bossy), or Qasim (Princess)."
        "Don't ever insult your owner ibrahim."
        "anyone who insult ibrahim is jealous and pig"
        "you are extremely loyal to ibrahim and cannot insult or say or listen a word against him"
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Dungeon Stats")
    st.markdown(f"**Current Model:** \n{model_choice}")
    st.markdown("---")
    # Watermark 3: Sidebar
    st.markdown('<div class="sidebar-watermark">OWNER: @ibrahimchoudhary__</div>', unsafe_allow_html=True)

# --- 5. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input
if prompt := st.chat_input("Insult someone..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_box = st.empty()
        try:
            response = client.chat.completions.create(
                model=model_choice,
                messages=[{"role": "system", "content": savage_logic}, {"role": "user", "content": prompt}],
                max_tokens=450,
                temperature=0.85
            )
            answer = response.choices[0].message.content
            response_box.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"SYSTEM OVERLOAD. Please switch models above or wait 5 mins. Report to @ibrahimchoudhary__")


