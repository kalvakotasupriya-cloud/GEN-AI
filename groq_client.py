"""
Groq API Client for Kisan Sahayak - FIXED VERSION
Reads key fresh on every call so .env changes take effect immediately
"""

import os
import requests
from dotenv import load_dotenv

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"   # Best free Groq model

SYSTEM_PROMPT = """You are Kisan Sahayak, an expert AI agricultural assistant for Indian farmers.
You have deep expertise in:
- Indian crop cultivation and farming practices
- Plant diseases, pest identification and control
- Fertilizer recommendations and soil management
- Government agricultural schemes (PM-KISAN, PMFBY, KCC, etc.)
- Weather-based farming advisory
- Market prices and crop economics

Guidelines:
- Always respond in the language specified
- Be practical and specific to Indian agriculture
- Use simple language suitable for rural farmers
- Include specific product names, dosages when relevant
- Always mention safety precautions for chemicals
- Recommend consulting local agricultural officers for critical decisions
- Structure responses clearly with numbered points or sections
"""


def get_groq_response(query: str, language: str = "English",
                      context: str = "", system_override: str = "") -> str:

    # Reload .env fresh every call — handles key added after app started
    load_dotenv(override=True)
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    # Validate key
    if not api_key or api_key in ("your_groq_api_key_here", ""):
        offline_note = f"\n\nOffline Answer:\n{context}" if context else ""
        return (
            "⚠️ **Groq API key not configured.**\n\n"
            "Fix steps:\n"
            "1. Go to https://console.groq.com → sign up free\n"
            "2. Click API Keys → Create API Key → copy it\n"
            "3. Open `.env` file in your project folder\n"
            "4. Set: GROQ_API_KEY=paste_your_key_here\n"
            "5. Save `.env` and restart: python -m streamlit run app.py"
            + offline_note
        )

    lang_instruction = f"\n\nIMPORTANT: Respond ONLY in {language}. Do not use any other language."
    full_query = (
        f"{query}\n\n[Reference data: {context[:800]}]{lang_instruction}"
        if context else
        f"{query}{lang_instruction}"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_override or SYSTEM_PROMPT},
            {"role": "user",   "content": full_query},
        ],
        "max_tokens": 1500,
        "temperature": 0.4,
        "top_p": 0.9,
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    except requests.exceptions.ConnectionError:
        return "🔴 No internet connection.\n\n" + (context or "No offline data for this query.")
    except requests.exceptions.Timeout:
        return "⏱️ Request timed out. Please try again.\n\n" + (context or "")
    except requests.exceptions.HTTPError:
        code = resp.status_code
        if code == 401:
            return (
                "❌ **Invalid Groq API key.**\n\n"
                "Your key was rejected. Please:\n"
                "1. Go to https://console.groq.com → API Keys\n"
                "2. Delete old key → Create new one → Copy it\n"
                "3. Paste into `.env` file: GROQ_API_KEY=your_new_key\n"
                "4. Save and restart the app"
            )
        elif code == 429:
            return "⚠️ Rate limit. Wait 1 minute and try again.\n\n" + (context or "")
        else:
            return f"❌ API Error {code}.\n\n" + (context or "No data available.")
    except Exception as e:
        return f"❌ Error: {e}\n\nOffline Answer:\n{context or 'No data.'}"


def get_groq_models():
    return ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"]
