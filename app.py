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
        return "Outsource Development Studio offers BPO, recruitment, corporate training (UWI Cave Hill partnership), and logistics in Dominica."

# ==========================================
# 3. PRIVACY & SECURITY GUARDRAILS (Day 9/11 Concepts)
# ==========================================
def redact_pii(text):
    """
    BACKEND EXPLANATION: Outsource Development handles recruitment and personal data. 
    We CANNOT send personal info to the AI. This function acts as a 'security guard', 
    using Regular Expressions (regex) to find emails, phone numbers, and 9-digit NINs, 
    replacing them with [REDACTED] BEFORE the message is sent to the AI.
    """
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[
