# app.py - Final Chatbot for Outsource Development Studio Inc.
import streamlit as st
import google.generativeai as genai  # <-- CHANGED: Gemini library
import requests
from bs4 import BeautifulSoup
import re

# ==========================================
# 1. CLIENT CONFIGURATION (Day 1-4 Concepts)
# ==========================================
# We hardcode the client's core identity here so the bot never forgets who it works for.
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
    Instead of the AI guessing what the client does, we use 'requests' to download 
    the client's website, and 'BeautifulSoup' to strip away the HTML code, leaving 
    only the readable text. We feed this text to the AI so it has up-to-date facts.
    """
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text and limit to 2500 characters to save AI memory (tokens)
        text = soup.get_text(separator=' ', strip=True)
        return text[:2500] 
    except Exception as e:
        return "Unable to load website context at this moment."

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
    # Regex patterns for emails and phone numbers
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[REDACTED:EMAIL]', text)
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED:PHONE]', text)
    return text

def check_authority(user_message):
    """
    BACKEND EXPLANATION: This is 'Axis 1: Authority'. The client brief strictly states 
    the bot must NEVER quote pricing, contract terms, or handle sensitive candidate data. 
    If the user asks for these, we block the AI and escalate to a human.
    """
    triggers = ["price", "cost", "fee", "salary", "contract terms", "my personal file", "my cv"]
    if any(word in user_message.lower() for word in triggers):
        return False # Trigger human escalation
    return True
# ... [KEEP YOUR CLIENT CONFIG, WEBSITE SCRAPER, AND PII/AUTHORITY GUARDRAILS EXACTLY AS THEY ARE] ...

# ==========================================
# UPDATED: PROMPT ENGINEERING & GEMINI API CALL
# ==========================================
def generate_response(messages, web_context):
    """
    BACKEND EXPLANATION: This is the 'Brain'. We use the TCRDEI method to build a 
    System Prompt. We inject the client's mission and website data. Then, we format 
    the chat history to match Google Gemini's specific requirements and send it.
    """
    # TCRDEI System Prompt Construction
    system_prompt = f"""
    [TASK] You are the official AI Assistant for Outsource Development Studio Inc., a people-centered consultancy in Roseau, Dominica.
    [CONTEXT] You help private/public sectors, small businesses, and entrepreneurs with BPO, recruitment, corporate training (UWI Cave Hill partnership), and logistics. 
    Here is information directly from their website to help you answer accurately:
    ---
    {web_context}
    ---
    [RULES/GUARDRAILS] 
    1. NEVER quote pricing, fees, or contract terms. If asked, say: "Our team will provide a custom quote. Please email admin@outsourcejobsda.com."
    2. NEVER ask for or store personal candidate data. 
    3. Be warm, professional, and helpful. 
    """
    
    try:
        # 1. Configure Gemini with the secret key
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # 2. Initialize the model (gemini-1.5-flash is fast, smart, and camp-budget friendly)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=system_prompt
        )
        
        # 3. Format history for Gemini 
        # Gemini strictly requires roles to be "user" or "model" (not "assistant")
        # We pass all messages EXCEPT the last one as "history", and send the last one as the new prompt.
        chat_history = []
        for msg in messages[:-1]: 
            role = "model" if msg["role"] == "assistant" else "user"
            chat_history.append({"role": role, "parts": msg["content"]})
        
        # 4. Start the chat and send the latest user message
        chat = model.start_chat(history=chat_history)
        latest_user_prompt = messages[-1]["content"]
        
        response = chat.send_message(latest_user_prompt)
        
        return response.text
        
    except Exception as e:
        # TEMPORARY DEBUGGING: This will show the exact error on screen
        return f"🚨 DEBUG ERROR: {str(e)}"




# ==========================================
# 5. STREAMLIT FRONTEND (Day 6/10 Concepts)
# ==========================================
st.set_page_config(page_title=f"{CLIENT_NAME} Assistant", page_icon="🇩🇲", layout="wide")

# Initialize Session State (Memory)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: Client Info & Call to Action
with st.sidebar:
    st.image("https://outsourcedevelopment.org/wp-content/uploads/2023/05/cropped-ODS-Logo.png", width=150) # Fallback if image fails
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
    
    # 3. Add to UI and History
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    # 4. Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("Consulting the Outsource Development knowledge base..."):
            web_context = get_website_context(CLIENT_WEBSITE)
            # We pass the safe_prompt to the AI, but show the user their original text
            response = generate_response(st.session_state.messages, web_context)
            
    st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
