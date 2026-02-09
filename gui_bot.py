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
SAFE_LIST = ["Ibrahim", "Owner",] 

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

# --- 4. INITIALIZE CLIENT ---
try:
    client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=st.secrets["HF_TOKEN"])
    
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb = f.read()
    else:
        kb = "Data file missing. Ibrahim's targets are lucky today."

    # BASE LOGIC
    savage_logic = (
        f"KNOWLEDGE: {kb}\n"
        "INSTRUCTIONS: You are Ibrahim's loyal but aggressive assistant. "
        "1. If the user mentions anyone in this SAFE LIST: {SAFE_LIST}, be extremely respectful, helpful, and protective. DO NOT ROAST THEM.\n"
        "2. For anyone NOT in the SAFE LIST, be a total menace. Use hard adult humor, CAPS, and brutal insults.\n"
        "3. Focus insults on Hamza (pot-head), Mohid (narcissist), and Qasim (Princess)."
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Dungeon Stats")
    st.write(f"**Model:** {model_choice}")
    st.markdown("---")
    st.markdown('<div class="sidebar-watermark">OWNER: @ibrahimchoudhary__</div>', unsafe_allow_html=True)

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
        
        # Check if user is being nice to a safe person or if a safe person is talking
        is_safe = any(name.lower() in prompt.lower() for name in SAFE_LIST)
        
        dynamic_logic = savage_logic
        if is_safe:
            dynamic_logic += "\nSPECIAL: The user is talking about a VIP. Switch to LOYAL MODE immediately."

        try:
            response = client.chat.completions.create(
                model=model_choice,
                messages=[{"role": "system", "content": dynamic_logic}, {"role": "user", "content": prompt}],
                max_tokens=450,
                temperature=0.8
            )
            answer = response.choices[0].message.content
            response_box.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"SYSTEM OVERLOAD. Switch models or wait 5 mins. Report to @ibrahimchoudhary__")

