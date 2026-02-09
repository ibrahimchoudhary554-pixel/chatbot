import streamlit as st
from openai import OpenAI
import os

# --- 1. UI & WATERMARK SETTINGS ---
st.set_page_config(page_title="Ibrahim's Roast Dungeon", page_icon="🔥", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ff4b4b; }
    .watermark-top { position: fixed; top: 10px; right: 10px; opacity: 0.4; color: white; font-size: 14px; z-index: 99; }
    .watermark-bottom { position: fixed; bottom: 10px; right: 10px; opacity: 0.4; color: white; font-size: 14px; z-index: 99; }
    .sidebar-watermark { text-align: center; opacity: 0.8; color: #ff4b4b; font-size: 16px; font-weight: bold; margin-top: 50px; }
    .model-box { border: 2px solid #ff0000; padding: 15px; border-radius: 10px; background-color: #1a0000; margin-bottom: 20px; }
    h1 { color: #ff4b4b !important; text-shadow: 0 0 10px #ff0000; }
    </style>
    <div class="watermark-top">@ibrahimchoudhary__</div>
    <div class="watermark-bottom">@ibrahimchoudhary__</div>
    """, unsafe_allow_html=True)

# --- 2. THE SAFE LIST (ADD NAMES HERE) ---
# Anyone in this list will NOT be roasted.
SAFE_LIST = ["Ibrahim", "Owner", "Zainab", "ibrahim", "zainab"] 

# --- 3. HEADER & EMERGENCY SWITCHER ---
st.title("🤖 Ibrahim's Roast Bot")

with st.container():
    st.markdown('<div class="model-box">', unsafe_allow_html=True)
    st.error("🚨 **CRASH PROTECTION SYSTEM**")
    st.write("If the bot crashes, **SWITCH THE MODEL** below. Report issues to **[ibrahimchoudhary__](https://instagram.com/ibrahimchoudhary__)**")
    model_choice = st.selectbox(
        "ACTIVE MODEL (WEAPON):",
        ["meta-llama/Llama-3.1-8B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3"],
        help="If it stops talking, flip the switch!"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. DATA LOADING ---
if os.path.exists("data.txt"):
    with open("data.txt", "r") as f:
        kb = f.read()
else:
    kb = "Data file missing."

# --- 5. CHAT LOGIC ---
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
        
        # --- LOGIC GATE: HARD SEPARATION OF SYSTEM PROMPTS ---
        is_safe_detected = any(name.lower() in prompt.lower() for name in SAFE_LIST)
        
        if is_safe_detected:
            # LOYAL MODE: Savage logic is completely removed
            active_system_prompt = (
                f"KNOWLEDGE: {kb}\n"
                "You are Ibrahim's loyal assistant. A VIP is mentioned. "
                "Be extremely polite, formal, and helpful. DO NOT use insults, "
                "DO NOT use CAPS, and DO NOT roast anyone in this conversation."
            )
        else:
            # SAVAGE MODE: Full power roast
            active_system_prompt = (
                f"KNOWLEDGE: {kb}\n"
                "You are Ibrahim's savage assistant. "
                "Be a total menace. Use hard adult humor, CAPS, and brutal insults. "
                "Target Hamza (pot-head runner), Mohid (narcissist), and Qasim (Princess)."
            )

        try:
            client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=st.secrets["HF_TOKEN"])
            response = client.chat.completions.create(
                model=model_choice,
                messages=[{"role": "system", "content": active_system_prompt}, {"role": "user", "content": prompt}],
                max_tokens=450,
                temperature=0.8
            )
            answer = response.choices[0].message.content
            response_box.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"SYSTEM OVERLOAD. Switch models or wait 5 mins. Report to @ibrahimchoudhary__")
