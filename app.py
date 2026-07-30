import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import re

# ==========================================
# 1. CLIENT CONFIGURATION (Day 1-4 Concepts)
# ==========================================
CLIENT_NAME = "Outsource Development Studio Inc."
CLIENT_LOCATION = "Roseau, Dominica"
CLIENT_EMAIL = "admin@outsourcejobsda.com"
CLIENT_WEBSITE = "https://outsourcedevelopment.org"

# ==========================================
# 2. WEBSITE INTEGRATION (Day 11/12 Concepts)
# ==========================================
def get_website_context(url):
    """
    BACKEND EXPLANATION: This function acts as the bot's 'research assistant'. 
    We use 'requests' to download the client's website, and 'BeautifulSoup' to 
    strip away the HTML code, leaving only the readable text. We feed this text 
    to the AI so it has up-to-date facts about services and UWI partnerships.
    """
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text and limit to 2500 characters to save AI memory (tokens)
        text = soup.get_text(separator=' ', strip=True)
        return text[:2500] 
    except Exception:
        return "Standard Outsource Development Studio services: BPO, recruitment, corporate training, and logistics."

# ==========================================
# 3. PRIVACY & SECURITY GUARDRAILS (Day 9/11 Concepts)
# ==========================================
def redact_pii(text):
    """
    BACKEND EXPLANATION: Outsource Development handles recruitment and personal data. 
    We CANNOT send personal info to the AI. This function acts as a 'security guard', 
    using Regular Expressions (regex) to find emails and phone numbers and replacing 
    them with [REDACTED] BEFORE the message is sent to the AI.
    """
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[REDACTED:EMAIL]', text)
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED:PHONE]', text)
    text = re.sub(r'\b\d{9}\b', '[REDACTED:NIN]', text) # 9-digit National Insurance
    return text

def check_authority(user_message):
    """
    BACKEND EXPLANATION: This is 'Axis 1: Authority'. The client brief strictly states 
    the bot must NEVER quote pricing, contract terms, or handle sensitive candidate data. 
    If the user asks for these, we block the AI and escalate to a human.
    """
    triggers = ["price", "cost", "fee", "salary", "contract terms", "my personal file", "my cv", "my application status", "am i eligible"]
    if any(word in user_message.lower() for word in triggers):
        return False # Trigger human escalation
    return True

# ==========================================
# 4. PROMPT ENGINEERING & AI CALL (Day 7/8 Concepts - TCRDEI)
# ==========================================
def generate_response(messages, web_context):
    """
    BACKEND EXPLANATION: This is the 'Brain'. We use the TCRDEI method to build a 
    System Prompt. We inject the client's mission, the scraped website data, and 
    strict guardrails. Then we send the whole chat history to OpenAI's API.
    """
    system_prompt = f"""
    [TASK] You are the official AI Assistant for {CLIENT_NAME}, a people-centered consultancy in {CLIENT_LOCATION}.
    [CONTEXT] You help private/public sectors, small businesses, and entrepreneurs with BPO, recruitment, corporate training (UWI Cave Hill partnership), and logistics. 
    Here is information directly from their website to help you answer accurately:
    ---
    {web_context}
    ---
    [RULES/GUARDRAILS] 
    1. NEVER quote pricing, fees, or contract terms. If asked, say: "Our team will provide a custom quote. Please email {CLIENT_EMAIL} to book a consultation."
    2. NEVER ask for or store personal candidate data (like CVs or national insurance numbers). 
    3. If the user wants to book a consultation, direct them to the website or email {CLIENT_EMAIL}.
    4. Be warm, professional, and helpful. The bot is the GPS; the human is the driver.
    """
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=api_messages,
                    temperature=0.5
        )
                response_text = response.choices[0].message.content
                
        except Exception as e:
                # TEMPORARY DEBUG: This will print the EXACT error on your screen
                response_text = f"🚨 DEBUG ERROR: {str(e)}"
# ==========================================
# 5. STREAMLIT FRONTEND (Day 6/10 Concepts)
# ==========================================
st.set_page_config(page_title=f"{CLIENT_NAME} Assistant", page_icon="🇩🇲", layout="wide")

# Initialize Session State (Memory)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: Client Info & Call to Action
with st.sidebar:
    st.title("Outsource Development Studio")
    st.markdown(f"**Location:** {CLIENT_LOCATION}")
    st.markdown(f"**Email:** {CLIENT_EMAIL}")
    st.divider()
    st.markdown("### 📅 Book a Consultation")
    st.markdown(f"Ready to grow your business? Email us at **{CLIENT_EMAIL}** or visit our website to book a service appointment.")
    st.link_button("Visit Our Website", CLIENT_WEBSITE)

# Main Chat UI
st.title(f"🤖 Welcome to {CLIENT_NAME}")
st.caption("Your AI guide to BPO, Recruitment, Training, and Business Excellence in Dominica.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input Logic
if prompt := st.chat_input("Ask about our services, UWI seminars, or recruitment..."):
    # 1. Check Authority (Guardrail)
    if not check_authority(prompt):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        escalation_msg = (f"For questions regarding pricing, contracts, or personal candidate files, "
                          f"our human team needs to assist you to ensure accuracy and privacy. "
                          f"Please reach out directly to **{CLIENT_EMAIL}**.")
        st.session_state.messages.append({"role": "assistant", "content": escalation_msg})
        with st.chat_message("assistant"): st.markdown(escalation_msg)
        st.stop()

    # 2. Redact PII (Privacy)
    safe_prompt = redact_pii(prompt)
    
    # 3. Add to UI and History (We show the user's original prompt, but send the safe one to AI)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # 4. Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("Consulting the Outsource Development knowledge base..."):
            web_context = get_website_context(CLIENT_WEBSITE)
            
            # Create a temporary message list with the redacted prompt for the AI
            ai_messages = full_messages_for_ai = [{"role": "system", "content": f"You are the assistant for {CLIENT_NAME}."}] 
            # Actually, let's just rebuild the messages list with the redacted last message for the API call
            api_messages = [{"role": "system", "content": f"You are the official AI Assistant for {CLIENT_NAME}. {web_context} NEVER quote pricing or handle personal data."}]
            for msg in st.session_state.messages[:-1]:
                api_messages.append({"role": msg["role"], "content": msg["content"]})
            api_messages.append({"role": "user", "content": safe_prompt})
            
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=api_messages,
                    temperature=0.5
                )
                response_text = response.choices[0].message.content
            except Exception as e:
                response_text = f"I'm sorry, I'm experiencing a technical difficulty. Please contact us at {CLIENT_EMAIL}."
            
    st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
