import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import re

# ==========================================
# 1. CLIENT CONFIGURATION (From Client Brief)
# ==========================================
CLIENT_NAME = "Outsource Development Studio Inc."
CLIENT_LOCATION = "Roseau, Dominica"
CLIENT_PHONE = "+1 (767) 225-8606"
CLIENT_EMAIL = "admin@outsourcejobsda.com"
CLIENT_WEBSITE = "https://outsourcedevelopment.org"

# ==========================================
# 2. MULTI-COLOR THEME ENGINE (Black, Grey, Red, White)
# ==========================================
THEMES = [
    {
        "name": "Dark Monochrome & Red (Default)",
        "bg_primary": "#121212",       # Pure black/dark grey
        "bg_sidebar": "#1a1a1a",       # Slightly lighter black for sidebar
        "bg_secondary": "#242424",     # Input fields / headers
        "bg_tertiary": "#2d2d2d",      # Subtle background elements
        "text_primary": "#ffffff",     # Pure white text
        "text_secondary": "#a3a3a3",   # Light grey text
        "accent_primary": "#ef4444",   # Vibrant red for buttons/user bubbles
        "card_bg": "#242424",          # Bot chat bubble background
        "border_color": "#404040"      # Subtle grey borders
    },
    {
        "name": "Light Monochrome & Red",
        "bg_primary": "#ffffff",       # Pure white
        "bg_sidebar": "#f4f4f5",       # Very light grey
        "bg_secondary": "#e4e4e7",     # Input fields
        "bg_tertiary": "#f4f4f5",      # Chat background
        "text_primary": "#18181b",     # Near-black text
        "text_secondary": "#52525b",   # Medium grey text
        "accent_primary": "#dc2626",   # Deep red for buttons/user bubbles
        "card_bg": "#ffffff",          # Bot chat bubble background
        "border_color": "#d4d4d8"      # Light grey borders
    },
    {
        "name": "Slate & Crimson",
        "bg_primary": "#0f172a",       # Deep slate grey/black
        "bg_sidebar": "#1e293b",       # Slate sidebar
        "bg_secondary": "#334155",     # Slate secondary
        "bg_tertiary": "#1e293b",      # Slate tertiary
        "text_primary": "#f8fafc",     # Off-white text
        "text_secondary": "#94a3b8",   # Slate grey text
        "accent_primary": "#991b1b",   # Deep crimson red
        "card_bg": "#334155",          # Slate bot bubble
        "border_color": "#475569"      # Slate border
    }
]

# Initialize theme in session state
if "theme_index" not in st.session_state:
    st.session_state.theme_index = 0

current_theme = THEMES[st.session_state.theme_index]

# Inject Custom CSS to match the HTML Template
st.markdown(f"""
<style>
    :root {{
        --bg-primary: {current_theme['bg_primary']};
        --bg-sidebar: {current_theme['bg_sidebar']};
        --bg-secondary: {current_theme['bg_secondary']};
        --bg-tertiary: {current_theme['bg_tertiary']};
        --text-primary: {current_theme['text_primary']};
        --text-secondary: {current_theme['text_secondary']};
        --accent-primary: {current_theme['accent_primary']};
        --card-bg: {current_theme['card_bg']};
        --border-color: {current_theme['border_color']};
    }}
    /* Global Overrides */
    .stApp {{ background-color: var(--bg-primary) !important; color: var(--text-primary) !important; }}
    section[data-testid="stSidebar"] {{ background-color: var(--bg-sidebar) !important; border-right: 1px solid var(--border-color); }}
    section[data-testid="stSidebar"] * {{ color: var(--text-primary) !important; }}
    
    /* Custom ODS Logo Badge */
    .ods-badge {{ 
        width: 56px; height: 56px; border-radius: 9999px; 
        display: flex; align-items: center; justify-content: center; 
        color: white; font-weight: bold; font-size: 1.125rem; 
        background-color: var(--accent-primary); margin-right: 1rem;
        border: 2px solid var(--text-primary);
    }}
    
    /* Chat Input Styling */
    .stChatInput {{ background-color: var(--bg-secondary) !important; border: 1px solid var(--border-color) !important; }}
    .stChatInput input {{ color: var(--text-primary) !important; }}
    
    /* Custom Chat Bubbles (Matching HTML Template) */
    .chat-bubble-user {{ 
        display: flex; justify-content: flex-end; margin-bottom: 1rem; 
        animation: fadeIn 0.3s ease-out; 
    }}
    .chat-bubble-user > div {{ 
        max-width: 80%; padding: 0.75rem 1rem; border-radius: 1rem 1rem 0.25rem 1rem; 
        background-color: var(--accent-primary); color: white; font-size: 0.95rem; font-weight: 500;
    }}
    .chat-bubble-bot {{ 
        display: flex; justify-content: flex-start; margin-bottom: 1rem; 
        animation: fadeIn 0.3s ease-out; 
    }}
    .chat-bubble-bot > div {{ 
        max-width: 80%; padding: 0.75rem 1rem; border-radius: 1rem 1rem 1rem 0.25rem; 
        background-color: var(--card-bg); color: var(--text-primary); font-size: 0.95rem; 
        border: 1px solid var(--border-color);
    }}
    
    /* Buttons & Links */
    .stButton>button {{ 
        background-color: var(--accent-primary) !important; color: white !important; 
        border: none !important; border-radius: 0.5rem !important; font-weight: 500 !important; width: 100%;
    }}
    .stButton>button:hover {{ opacity: 0.9 !important; }}
    a.custom-link {{ color: var(--accent-primary) !important; text-decoration: none; font-weight: 500; }}
    a.custom-link:hover {{ text-decoration: underline; }}
    
    /* Hide default Streamlit branding for a clean, custom-app look */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    .viewerBadge_container__1QSob {{ display: none; }}
    
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. PRIVACY & SECURITY GUARDRAILS (Day 9/11)
# ==========================================
def redact_pii(text):
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[REDACTED:EMAIL]', text)
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED:PHONE]', text)
    text = re.sub(r'\b\d{9}\b', '[REDACTED:NIN]', text)
    return text

def check_authority(user_message):
    triggers = ["price", "cost", "fee", "salary", "contract terms", "my personal file", "my cv", "my application status", "am i eligible"]
    if any(word in user_message.lower() for word in triggers):
        return False
    return True

# ==========================================
# 4. AI & MOCK FALLBACK (Day 7/8 + Demo Life Raft)
# ==========================================
def generate_response(messages, web_context):
    system_prompt = f"""
    [TASK] You are the official AI Assistant for {CLIENT_NAME}, a people-centered consultancy in {CLIENT_LOCATION}.
    [CONTEXT] You help private/public sectors, small businesses, and entrepreneurs with BPO, recruitment, corporate training (UWI Cave Hill partnership), and logistics. 
    Website context: {web_context}
    [RULES] 
    1. NEVER quote pricing, fees, or contract terms. Say: "Our team will provide a custom quote. Please email {CLIENT_EMAIL}."
    2. NEVER ask for or store personal candidate data. 
    3. Be warm, professional, and helpful. The bot is the GPS; the human is the driver.
    """
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=full_messages, temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        # DEMO DAY LIFE RAFT: Graceful degradation if API quota is exceeded
        error_msg = str(e).lower()
        last_user_msg = messages[-1]["content"].lower()
        
        if "insufficient_quota" in error_msg or "429" in error_msg:
            if any(word in last_user_msg for word in ["service", "offer", "do", "bpo", "training", "uwi"]):
                return "Outsource Development Studio offers Business Process Outsourcing (BPO), recruitment and talent matching, corporate training (including our quarterly seminars with UWI Cave Hill), logistics, and strategic business development. How can I direct you today?"
            elif any(word in last_user_msg for word in ["book", "appointment", "contact", "email"]):
                return f"I would be happy to help you get started. Please email {CLIENT_EMAIL} with your preferred dates, or click the 'Visit Website' button in the sidebar."
            else:
                return f"Thank you for your inquiry! As the AI assistant for {CLIENT_NAME}, I can help guide you to our BPO, recruitment, or training services. For specific consulting engagements, our human team will provide the best support. Please reach out to {CLIENT_EMAIL}."
        else:
            return f"I'm experiencing a technical difficulty. Please contact our team at {CLIENT_EMAIL}."

# ==========================================
# 5. STREAMLIT FRONTEND (Custom HTML/CSS UI)
# ==========================================
st.set_page_config(page_title=f"{CLIENT_NAME} Assistant", page_icon="🇩🇲", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR (Matches HTML Template) ---
with st.sidebar:
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
        <div class="ods-badge">ODS</div>
        <div>
            <h3 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: var(--text-primary);">Outsource Development Studio</h3>
            <p style="margin: 0; font-size: 0.8rem; color: var(--accent-primary); font-weight: 600;">Online • Ready to help</p>
        </div>
    </div>
    
    <div style="margin-bottom: 1.5rem; font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
        <p style="margin: 0 0 0.5rem 0;">📍 {CLIENT_LOCATION}</p>
        <p style="margin: 0 0 0.5rem 0;">📞 {CLIENT_PHONE}</p>
        <p style="margin: 0 0 1rem 0;">✉️ {CLIENT_EMAIL}</p>
    </div>

    <div style="border-top: 1px solid var(--border-color); padding-top: 1rem;">
        <p style="font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary);">📅 Book a Consultation</p>
        <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">Ready to grow your business? Reach out to our team directly.</p>
        <a href="mailto:{CLIENT_EMAIL}?subject=Consultation%20Request" target="_blank" style="display: block; text-align: center; padding: 0.6rem; background-color: var(--accent-primary); color: white; text-decoration: none; border-radius: 0.5rem; font-weight: 500; font-size: 0.9rem; margin-bottom: 0.5rem;">Send Email</a>
        <a href="{CLIENT_WEBSITE}" target="_blank" style="display: block; text-align: center; padding: 0.6rem; background-color: var(--bg-secondary); color: var(--text-primary); text-decoration: none; border-radius: 0.5rem; font-weight: 500; font-size: 0.9rem; border: 1px solid var(--border-color);">Visit Website</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Multi-Color Theme Toggle
    st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;'>🎨 App Theme</p>", unsafe_allow_html=True)
    if st.button("Cycle Colors 🔄"):
        st.session_state.theme_index = (st.session_state.theme_index + 1) % len(THEMES)
        st.rerun()
    
    st.markdown(f"<p style='font-size: 0.8rem; color: var(--text-secondary); text-align: center; margin-top: 0.5rem;'>Current: <b>{current_theme['name']}</b></p>", unsafe_allow_html=True)

# --- MAIN CHAT AREA ---
st.markdown(f"<h2 style='color: var(--text-primary); margin-bottom: 0.5rem;'>🤖 Welcome to {CLIENT_NAME}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: var(--text-secondary); margin-bottom: 1.5rem; font-size: 0.95rem;'>Your AI guide to BPO, Recruitment, Training, and Business Excellence in Dominica.</p>", unsafe_allow_html=True)

# Render Chat History with Custom HTML Bubbles
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user"><div>{message["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-bot"><div>{message["content"]}</div></div>', unsafe_allow_html=True)

# Chat Input Logic
if prompt := st.chat_input("Ask about our services, UWI seminars, or recruitment..."):
    # 1. Check Authority (Guardrail)
    if not check_authority(prompt):
        st.session_state.messages.append({"role": "user", "content": prompt})
        escalation_msg = f"For questions regarding pricing, contracts, or personal candidate files, our human team must assist you to ensure accuracy and privacy. Please reach out to **{CLIENT_EMAIL}**."
        st.session_state.messages.append({"role": "assistant", "content": escalation_msg})
        st.rerun()

    # 2. Redact PII (Privacy)
    safe_prompt = redact_pii(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 3. Generate AI Response
    with st.spinner("Consulting the knowledge base..."):
        # Mock web context for the demo (prevents scraping errors during presentation)
        web_context = "Outsource Development Studio offers BPO, recruitment, corporate training (UWI Cave Hill partnership), and logistics in Dominica."
        
        # Rebuild messages for API with redacted last prompt
        api_messages = [{"role": "system", "content": f"You are the assistant for {CLIENT_NAME}. {web_context} NEVER quote pricing or handle personal data."}]
        for msg in st.session_state.messages[:-1]:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
        api_messages.append({"role": "user", "content": safe_prompt})
        
        response_text = generate_response(api_messages, web_context)
        
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.rerun()
