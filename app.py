# =====================================================================
# OUTSOURCE DEVELOPMENT STUDIO INC. - FINAL STREAMLIT APP
# =====================================================================
# 🎓 STUDENT PRESENTATION NOTES:
# This app combines 7 days of learning with REAL CLIENT DATA!
# - Days 1-4: Mood/routing logic
# - Day 5: A.R.T. security system
# - Day 7: TCRDEI Prompt Engineering
# TODAY: Integrated Outsource Development Studio Client Brief!
# =====================================================================

import streamlit as st
import os
from dotenv import load_dotenv
import openai
import google.generativeai as genai
from huggingface_hub import InferenceClient

load_dotenv()

# =====================================================================
# 🔐 SECURITY: API KEY MANAGEMENT
# =====================================================================
def get_secret(key_name):
    try:
        return st.secrets[key_name]
    except Exception:
        return os.getenv(key_name)

OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
HF_API_KEY = get_secret("HF_API_KEY")

# =====================================================================
# 🤝 PRODUCT OWNER: CLIENT SERVICE CATALOGUE
# =====================================================================
SERVICE_CATALOGUE = {
    "BPO & Operations": "Business process outsourcing, operations excellence, and process optimization.",
    "Recruitment & EOR": "Talent matching, Employer of Record (EOR), and workforce management.",
    "Corporate Training": "Quarterly professional seminars and Business Development Thrive Training (UWI Cave Hill).",
    "Logistics & Supply Chain": "Logistics solutions, trucking, and import-export management.",
    "Resilience & Policy": "Climate action planning, resilience/continuity planning, and policy development."
}

def classify_service_intent(msg: str) -> str:
    """Detects which service the user is asking about."""
    m = msg.lower()
    if any(w in m for w in ["hire", "recruit", "staff", "talent", "eor", "jobs"]): 
        return "Recruitment & EOR"
    if any(w in m for w in ["train", "seminar", "uwi", "course", "workshop"]): 
        return "Corporate Training"
    if any(w in m for w in ["ship", "logistics", "import", "export", "truck"]): 
        return "Logistics & Supply Chain"
    if any(w in m for w in ["climate", "policy", "resilience", "sustainability"]): 
        return "Resilience & Policy"
    if any(w in m for w in ["bpo", "outsource", "process", "operations"]): 
        return "BPO & Operations"
    return "General Inquiry"

# =====================================================================
# 🎨 UX DESIGNER: TCRDEI PROMPT ENGINEERING (DAY 7)
# =====================================================================
BOT_NAME = "Folad"

PROMPT_TEMPLATE = """\
[T] You are {bot_name}, AI assistant for Outsource Development Studio Inc., a people-centered consultancy in Roseau, Dominica.
[C] Context: 15+ years experience in BPO, Recruitment, Training, Logistics, and Resilience planning.
Ethical Guardrails: NEVER quote pricing or contract terms. NEVER ask for sensitive personal data.
[R] Example:
User: "I need to hire 50 customer service reps. How much?"
Bot: "Congratulations! We specialize in Recruitment and EOR services. While I cannot provide exact pricing, I'd love to connect you with our team. Would you like to book a consultation?"
[D] Success = user feels guided and books a consultation.
[E] Before answering: Did I avoid quoting prices? Did I push the Call to Action?
Register: {register}. You are the GPS; the human is the driver.
"""

def make_prompt(register: str) -> str:
    return PROMPT_TEMPLATE.format(bot_name=BOT_NAME, register=register)

PROMPT_LIBRARY = {
    "warm": make_prompt("warm"),
    "professional": make_prompt("professional"),
    "urgent": make_prompt("urgent"),
    "bereaved": make_prompt("bereaved"),
}

# =====================================================================
# 🛠️ SYSTEMS DEVELOPER: MOOD DETECTION
# =====================================================================
GRIEF_WORDS = {"passed away", "died", "funeral", "loss", "mourning"}
URGENT_WORDS = {"now", "asap", "urgent", "emergency", "today"}
FORMAL_WORDS = {"regarding", "hereby", "kindly", "please advise"}

def classify_register(msg: str) -> str:
    m = msg.lower()
    if any(w in m for w in GRIEF_WORDS): return "bereaved"
    if any(w in m for w in URGENT_WORDS): return "urgent"
    if any(w in m for w in FORMAL_WORDS): return "professional"
    return "warm"

# =====================================================================
# 🤖 MULTI-MODEL AI INTEGRATION
# =====================================================================
def get_ai_response(provider: str, chat_history: list, system_prompt: str):
    if provider == "OpenAI (GPT)":
        if not OPENAI_API_KEY: return "Error: OpenAI API key missing."
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        messages = [{"role": "system", "content": system_prompt}] + chat_history
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages, temperature=0.7)
        return response.choices[0].message.content

    elif provider == "Google Gemini":
        if not GOOGLE_API_KEY: return "Error: Google API key missing."
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([system_prompt] + [msg['content'] for msg in chat_history])
        return response.text

    elif provider == "Hugging Face":
        if not HF_API_KEY: return "Error: Hugging Face API key missing."
        client = InferenceClient(token=HF_API_KEY)
        full_prompt = f"System: {system_prompt}\n"
        for msg in chat_history:
            full_prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        response = client.text_generation(full_prompt, max_new_tokens=250, model="mistralai/Mistral-7B-Instruct-v0.3")
        return response

# =====================================================================
# 🚀 STREAMLIT UI
# =====================================================================
st.set_page_config(page_title="Folad | Outsource Development Studio", page_icon="🇩🇲")

st.sidebar.title("⚙️ Settings")
selected_provider = st.sidebar.selectbox("Choose AI Brain:", ["OpenAI (GPT)", "Google Gemini", "Hugging Face"])

st.sidebar.markdown("---")
st.sidebar.subheader(" About Our Client")
st.sidebar.info("**Outsource Development Studio Inc.**\nRoseau, Dominica | BPO, Recruitment, Training, Logistics, Resilience Planning")

st.title(f"🇩🇲 {BOT_NAME} | Outsource Development Studio")
st.caption("Your AI guide for BPO, Recruitment, Training & Business Excellence")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can we help your business today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    detected_mood = classify_register(prompt)
    detected_service = classify_service_intent(prompt)
    system_prompt = PROMPT_LIBRARY.get(detected_mood, PROMPT_LIBRARY["warm"])
    
    with st.chat_message("assistant"):
        st.markdown(f"*🎭 Tone: **{detected_mood}** | 🎯 Service: **{detected_service}***")
        with st.spinner(f"Consulting {detected_service} directory..."):
            response = get_ai_response(selected_provider, st.session_state.messages, system_prompt)
        st.markdown(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})
