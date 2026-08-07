# ==========================================
# 🛠️ THE TOOLBOX (Importing our supplies)
# ==========================================
# "import" means we are grabbing tools from our coding toolbox.
import streamlit as st      # Streamlit is the magic tool that turns Python code into a website UI!
from openai import OpenAI   # This is the "phone" we use to call the AI brain (OpenAI or Groq).
import re                   # "Regular Expressions" - a search tool to find hidden patterns (like emails).
import time                 # Just for counting seconds if we need the bot to pause.

# ==========================================
# 🪪 1. THE BOT'S ID CARD (Client Info)
# ==========================================
# If someone asks the bot "Where are you located?", it looks at these variables to answer.
CLIENT_NAME = "Outsource Development Studio Inc."
CLIENT_LOCATION = "Roseau, Dominica"
CLIENT_PHONE = "+1 (767) 225-8606"
CLIENT_EMAIL = "admin@outsourcejobsda.com"
CLIENT_WEBSITE = "https://outsourcedevelopment.org"

# ==========================================
# 👕 2. THE BOT'S WARDROBE (Themes & Colors)
# ==========================================
# We created 3 different "outfits" (color schemes) for the website.
# "bg" means Background, "text" means text color, "accent" means the bright pop of color (like buttons).
THEMES = [
    {
        "name": "Dark Monochrome & Red (Default)",
        "bg_primary": "#121212", "bg_sidebar": "#1a1a1a", "bg_secondary": "#242424",
        "bg_tertiary": "#2d2d2d", "text_primary": "#ffffff", "text_secondary": "#a3a3a3",
        "accent_primary": "#ef4444", "card_bg": "#242424", "border_color": "#404040"
    },
    {
        "name": "Light Monochrome & Red",
        "bg_primary": "#ffffff", "bg_sidebar": "#f4f4f5", "bg_secondary": "#e4e4e7",
        "bg_tertiary": "#f4f4f5", "text_primary": "#18181b", "text_secondary": "#52525b",
        "accent_primary": "#dc2626", "card_bg": "#ffffff", "border_color": "#d4d4d8"
    },
    {
        "name": "Slate & Crimson",
        "bg_primary": "#0f172a", "bg_sidebar": "#1e293b", "bg_secondary": "#334155",
        "bg_tertiary": "#1e293b", "text_primary": "#f8fafc", "text_secondary": "#94a3b8",
        "accent_primary": "#991b1b", "card_bg": "#334155", "border_color": "#475569"
    }
]

# 🧠 BOT MEMORY (Session State):
# Streamlit has a weird quirk: every time you click a button, the whole page resets and forgets everything!
# To fix this, we use "st.session_state". Think of it like a backpack the bot wears. 
# Whatever we put in the backpack stays there, even when the page refreshes.
if "theme_index" not in st.session_state:
    st.session_state.theme_index = 0 # Start on outfit #0

current_theme = THEMES[st.session_state.theme_index]

# 🎨 PAINTING THE WEBSITE (CSS):
# Streamlit's default look is plain. We inject CSS (Cascading Style Sheets) to paint the website 
# with the colors from our current_theme outfit.
st.markdown(f"""
<style>
    :root {{
        --bg-primary: {current_theme['bg_primary']}; --bg-sidebar: {current_theme['bg_sidebar']};
        --bg-secondary: {current_theme['bg_secondary']}; --bg-tertiary: {current_theme['bg_tertiary']};
        --text-primary: {current_theme['text_primary']}; --text-secondary: {current_theme['text_secondary']};
        --accent-primary: {current_theme['accent_primary']}; --card-bg: {current_theme['card_bg']};
        --border-color: {current_theme['border_color']};
    }}
    .stApp {{ background-color: var(--bg-primary) !important; color: var(--text-primary) !important; }}
    section[data-testid="stSidebar"] {{ background-color: var(--bg-sidebar) !important; border-right: 1px solid var(--border-color); }}
    section[data-testid="stSidebar"] * {{ color: var(--text-primary) !important; }}
    .ods-badge {{ width: 56px; height: 56px; border-radius: 9999px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 1.125rem; background-color: var(--accent-primary); margin-right: 1rem; border: 2px solid var(--text-primary); }}
    .stChatInput {{ background-color: var(--bg-secondary) !important; border: 1px solid var(--border-color) !important; }}
    .stChatInput input {{ color: var(--text-primary) !important; }}
    /* Chat Bubbles: Making user messages go right, and bot messages go left */
    .chat-bubble-user {{ display: flex; justify-content: flex-end; margin-bottom: 1rem; animation: fadeIn 0.3s ease-out; }}
    .chat-bubble-user > div {{ max-width: 80%; padding: 0.75rem 1rem; border-radius: 1rem 1rem 0.25rem 1rem; background-color: var(--accent-primary); color: white; font-size: 0.95rem; font-weight: 500; }}
    .chat-bubble-bot {{ display: flex; justify-content: flex-start; margin-bottom: 1rem; animation: fadeIn 0.3s ease-out; }}
    .chat-bubble-bot > div {{ max-width: 80%; padding: 0.75rem 1rem; border-radius: 1rem 1rem 1rem 0.25rem; background-color: var(--card-bg); color: var(--text-primary); font-size: 0.95rem; border: 1px solid var(--border-color); }}
    .stButton>button {{ background-color: var(--accent-primary) !important; color: white !important; border: none !important; border-radius: 0.5rem !important; font-weight: 500 !important; width: 100%; }}
    .stButton>button:hover {{ opacity: 0.9 !important; }}
    a.custom-link {{ color: var(--accent-primary) !important; text-decoration: none; font-weight: 500; }}
    /* Hide Streamlit's default "Made with Streamlit" footer */
    #MainMenu {{ visibility: hidden; }} footer {{ visibility: hidden; }} .viewerBadge_container__1QSob {{ display: none; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🛡️ 3. THE BOUNCERS (Security & Guardrails)
# ==========================================
# A good bot needs security guards so it doesn't get tricked into doing bad things.

# 🚨 GUARD 1: The "Break-Glass" Distress Detector
# If a user is crying, panicking, or in danger, the bot MUST stop acting like a business bot 
# and immediately act like a caring human.
DISTRESS_TRIGGERS = {
    "grief": ["passed away", "died", "funeral", "mourning", "lost my husband", "lost my wife"],
    "panic": ["can't breathe", "can't cope", "panic attack", "mental emergency"],
    "self_harm": ["hurt myself", "end it", "no way out", "suicide"],
    "aggrieved": ["nobody listens", "you people never", "sick of this", "scam", "ruined my life"]
}

def detect_distress(msg):
    """Checks if the user's message contains any emergency words."""
    m = msg.lower() # Make everything lowercase so "DIED" and "died" both match
    for category, words in DISTRESS_TRIGGERS.items():
        if any(w in m for w in words): return category
    return None # No distress found

def break_glass_reply(category):
    """Returns a highly empathetic, emergency response."""
    if category == "grief":
        return f"I am so incredibly sorry for your loss. Please don't worry about business matters right now. If you need immediate support, please reach out to our human team directly at {CLIENT_EMAIL} or take a moment for yourself. 🕊️"
    if category in ["self_harm", "panic"]:
        return "I hear you, and your safety is the most important thing. Please step away and call a local emergency hotline or a trusted person immediately. We are here for you when you are safe."
    return f"I hear how frustrating this is. Let me connect you with a human team member right now who can listen and help sort this out. Please email {CLIENT_EMAIL}."

# 🖍️ GUARD 2: The Sharpie (PII Redaction)
# "PII" means Personally Identifiable Information. We NEVER send real phone numbers or emails to the AI brain.
# We use the Sharpie to cross them out BEFORE the AI sees them.
def redact_pii(text):
    # re.sub means "Find this pattern and replace it with something else"
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[REDACTED:EMAIL]', text) # Hide emails
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED:PHONE]', text) # Hide phone numbers
    text = re.sub(r'\b\d{9}\b', '[REDACTED:NIN]', text) # Hide National Insurance Numbers
    return text

# 🛑 GUARD 3: The "Not My Job" Rule (Authority)
# The bot is a GPS, not a lawyer. It is NOT allowed to give prices, sign contracts, or check personal files.
def check_authority(user_message):
    triggers = ["price", "cost", "fee", "salary", "contract terms", "my personal file", "my cv", "my application status", "am i eligible"]
    # If the user asks about any of these, return False (meaning: Bot is NOT allowed to answer).
    return not any(word in user_message.lower() for word in triggers)

# ==========================================
# 🎭 4. READING THE ROOM (Vibe Check / Tone)
# ==========================================
# Depending on how the user types, the bot changes its "vibe" (Register).
def detect_register(msg):
    m = msg.lower()
    if any(w in m for w in ["passed away", "died", "funeral", "loss", "mourning"]): return "bereaved" # Sad
    if any(w in m for w in ["asap", "urgent", "emergency", "now", "immediately"]): return "urgent" # Fast
    if any(w in m for w in ["regarding", "hereby", "kindly", "formal", "contract"]): return "professional" # Fancy
    return "warm" # Friendly (Default)

# ==========================================
# 🧠 5. THE BRAIN & THE MICROWAVE (AI Fallbacks)
# ==========================================
# 🍕 PIZZA ANALOGY: 
# Calling the AI is like ordering a pizza from a fancy kitchen (OpenAI/Groq).
# If the kitchen is closed, on fire, or you don't have money (No API Keys), 
# the bot uses the "Microwave" (Smart Mock) to give you a pre-made sandwich so you don't starve!

def get_llm_client():
    """Tries to connect to the fancy AI kitchen."""
    # 1. Try Groq (It's free and super fast! Great for students)
    if "GROQ_API_KEY" in st.secrets:
        return OpenAI(api_key=st.secrets["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1"), "llama3-8b-8192"
    # 2. Try OpenAI (The standard brain)
    if "OPENAI_API_KEY" in st.secrets:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"]), "gpt-4o-mini"
    # 3. No keys? Kitchen is closed.
    return None, None

def build_system_prompt(register="warm"):
    """Writes the secret instruction manual the AI reads before talking to the user."""
    tone_instructions = {
        "warm": "Be warm, encouraging, and use plain language. Add a 💛.",
        "professional": "Be formal, concise, and professional. Use 'Dear user'.",
        "urgent": "Be extremely concise, direct, and fast. No filler words. Add a ⚡.",
        "bereaved": "Open with sincere condolences. Be gentle. Never more than 2 sentences of facts. Add a 🕊️."
    }
    
    # TCRDEI is a framework: Task, Context, Reference, Defined Success, Evaluate, Inputs
    return f"""
    [T] TASK: You are the official AI Assistant for {CLIENT_NAME}, a people-centered consultancy in {CLIENT_LOCATION}.
    [C] CONTEXT: You help private/public sectors, small businesses, and entrepreneurs with BPO, recruitment, corporate training (UWI Cave Hill partnership), and logistics.
    [R] REFERENCE: User: "What do you do?" Bot: "We offer outsourced business services, talent recruitment, and corporate training. How can I guide you today? 💛"
    [D] DEFINED SUCCESS: The user feels guided, informed, and never pressured. The bot is the GPS; the human is the driver.
    [E] EVALUATE: Before answering, check: does this satisfy the rules? If not, reroute to human.
    [I] INPUTS: Register: {register}. Tone Rule: {tone_instructions.get(register, tone_instructions['warm'])}
    
    STRICT RULES:
    1. NEVER quote pricing, fees, or contract terms. Say: "Our team will provide a custom quote. Please email {CLIENT_EMAIL}."
    2. NEVER ask for or store personal candidate data.
    3. Translate jargon into plain language (e.g., instead of "BPO", say "outsourced business services").
    """

def smart_mock_response(user_msg, register="warm"):
    """🍲 THE MICROWAVE: If the AI brain is offline, this local code fakes a smart response!"""
    msg = user_msg.lower()
    intent = "general"
    # Figure out what they are asking about
    if any(w in msg for w in ["bpo", "outsource", "call center", "support"]): intent = "bpo"
    elif any(w in msg for w in ["training", "uwi", "seminar", "upskill"]): intent = "training"
    elif any(w in msg for w in ["recruit", "hire", "job", "cv", "talent"]): intent = "recruitment"
    elif any(w in msg for w in ["logistics", "supply chain", "shipping"]): intent = "logistics"
    
    # Pre-written answers for the microwave
    base = {
        "bpo": "We specialize in outsourced business services. Our team in Dominica handles customer support, data entry, and back-office tasks so you can focus on growth.",
        "training": "We partner with UWI Cave Hill to offer corporate training and quarterly seminars to upskill your workforce.",
        "recruitment": "Our talent acquisition team connects top-tier Dominican talent with local and international employers.",
        "logistics": "We provide strategic logistics and supply chain consulting to help streamline your operations in the Caribbean.",
        "general": f"I am the {CLIENT_NAME} AI. I can help you learn about our BPO, Recruitment, Training, or Logistics services."
    }
    text = base.get(intent, base["general"])
    
    # Apply the tone!
    if register == "bereaved": return f"I am so sorry. Please don't worry about business matters right now. When you are ready, our human team is here to help gently. 🕊️"
    elif register == "urgent": return f"{text.upper()} ⚡ LET'S GET THIS SORTED. EMAIL {CLIENT_EMAIL} NOW."
    elif register == "professional": return f"Dear user — {text} Kindly advise on your next steps by contacting {CLIENT_EMAIL}."
    else: return f"{text} 💛 How can I direct you today?"

def safe_llm_call(user_msg, chat_history):
    """The Manager: Tries the fancy kitchen. If it fails, uses the microwave."""
    register = detect_register(user_msg)
    system_prompt = build_system_prompt(register)
    messages = [{"role": "system", "content": system_prompt}] + chat_history
    
    client, model = get_llm_client()
    if client:
        try:
            # Call the AI!
            response = client.chat.completions.create(model=model, messages=messages, temperature=0.5)
            return response.choices[0].message.content
        except Exception as e:
            # Fancy kitchen exploded! Use microwave.
            return smart_mock_response(user_msg, register) + f"\n\n*(Note: API fallback triggered. Error: {type(e).__name__})*"
    else:
        # No kitchen keys! Use microwave.
        return smart_mock_response(user_msg, register)

# ==========================================
# 🖥️ 6. BUILDING THE SCREEN (Streamlit UI)
# ==========================================
# This is where we actually draw the website the user sees.
st.set_page_config(page_title=f"{CLIENT_NAME} Assistant", page_icon="🇩🇲", layout="wide")

# Make sure the chat memory backpack exists
if "messages" not in st.session_state: 
    st.session_state.messages = []

# --- THE SIDEBAR (Left Menu) ---
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
    st.markdown("<p style='font-size: 0.85rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;'>🎨 App Theme</p>", unsafe_allow_html=True)
    
    # Button to change colors
    if st.button("Cycle Colors 🔄"):
        st.session_state.theme_index = (st.session_state.theme_index + 1) % len(THEMES)
        st.rerun() # Refresh the page to show new colors
        
    st.markdown(f"<p style='font-size: 0.8rem; color: var(--text-secondary); text-align: center; margin-top: 0.5rem;'>Current: <b>{current_theme['name']}</b></p>", unsafe_allow_html=True)

# --- THE MAIN CHAT AREA ---
st.markdown(f"<h2 style='color: var(--text-primary); margin-bottom: 0.5rem;'>🤖 Welcome to {CLIENT_NAME}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: var(--text-secondary); margin-bottom: 1.5rem; font-size: 0.95rem;'>Your AI guide to BPO, Recruitment, Training, and Business Excellence in Dominica.</p>", unsafe_allow_html=True)

# Draw all the old messages from the backpack memory
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user"><div>{message["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-bot"><div>{message["content"]}</div></div>', unsafe_allow_html=True)

# ==========================================
# 🎮 7. THE GAME LOOP (When the user types)
# ==========================================
# This triggers ONLY when the user hits "Enter" in the chat box.
if prompt := st.chat_input("Ask about our services, UWI seminars, or recruitment..."):
    
    # Step 1: Put the user's message in the memory backpack
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Step 2: Check for Distress (Break-Glass)
    distress_category = detect_distress(prompt)
    if distress_category:
        st.session_state.messages.append({"role": "assistant", "content": break_glass_reply(distress_category)})
        st.rerun() # Refresh screen to show the new message

    # Step 3: Check Authority (Did they ask for prices/contracts?)
    if not check_authority(prompt):
        escalation_msg = f"For questions regarding pricing, contracts, or personal candidate files, our human team must assist you to ensure accuracy and privacy. Please reach out to **{CLIENT_EMAIL}**."
        st.session_state.messages.append({"role": "assistant", "content": escalation_msg})
        st.rerun()

    # Step 4: Redact PII (Hide secrets before sending to the AI brain)
    safe_prompt = redact_pii(prompt)
    api_history = st.session_state.messages[:-1] + [{"role": "user", "content": safe_prompt}]
    
    # Step 5: Generate the Bot's Reply!
    with st.spinner("Consulting the knowledge base..."): # Shows a little loading animation
        response_text = safe_llm_call(safe_prompt, api_history)
        
    # Step 6: Put the bot's reply in the memory backpack and refresh the screen
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.rerun()
