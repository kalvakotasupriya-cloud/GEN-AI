"""
utils/voice.py - STT + TTS for Kisan Sahayak (FIXED)
STT: Google Speech Recognition (free, no API key needed)
TTS: gTTS - Google Text to Speech (free)
"""

import io
import re


STT_LANG_MAP = {
    "English":            "en-IN",
    "हिंदी (Hindi)":      "hi-IN",
    "తెలుగు (Telugu)":    "te-IN",
    "தமிழ் (Tamil)":      "ta-IN",
    "ಕನ್ನಡ (Kannada)":    "kn-IN",
    "मराठी (Marathi)":    "mr-IN",
    "ਪੰਜਾਬੀ (Punjabi)":   "pa-IN",
    "বাংলা (Bengali)":    "bn-IN",
    "ગુજરાતી (Gujarati)": "gu-IN",
    "മലയാളം (Malayalam)": "ml-IN",
}

TTS_LANG_MAP = {
    "English":            "en",
    "हिंदी (Hindi)":      "hi",
    "తెలుగు (Telugu)":    "te",
    "தமிழ் (Tamil)":      "ta",
    "ಕನ್ನಡ (Kannada)":    "kn",
    "मराठी (Marathi)":    "mr",
    "ਪੰਜਾਬੀ (Punjabi)":   "pa",
    "বাংলা (Bengali)":    "bn",
    "ગુજરાતી (Gujarati)": "gu",
    "മലയാളം (Malayalam)": "ml",
}


def transcribe(wav_bytes: bytes, language: str = "English"):
    """
    WAV bytes → (transcript_text, error_string)
    Uses Google Speech Recognition — free, no API key needed.
    """
    try:
        import speech_recognition as sr
    except ImportError:
        return "", "SpeechRecognition not installed. Run: pip install SpeechRecognition"

    lang_code = STT_LANG_MAP.get(language, "en-IN")
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.pause_threshold  = 1.0

    try:
        with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language=lang_code)
        return text.strip(), ""
    except sr.UnknownValueError:
        return "", "Could not understand speech. Please speak clearly and try again."
    except sr.RequestError as e:
        return "", f"Speech service unavailable: {e}. Check internet connection."
    except Exception as e:
        return "", f"Transcription error: {e}"


def speak(text: str, language: str = "English"):
    """
    Text → (mp3_bytes, error_string)
    Uses gTTS — free Google TTS, no API key needed.
    """
    try:
        from gtts import gTTS
    except ImportError:
        return None, "gTTS not installed. Run: pip install gtts"

    lang_code = TTS_LANG_MAP.get(language, "en")

    # Clean markdown so it reads naturally
    clean = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    clean = re.sub(r'\*(.+?)\*',     r'\1', clean)
    clean = re.sub(r'#+\s*',         '',    clean)
    clean = re.sub(r'\n{2,}',        '. ', clean)
    clean = re.sub(r'\n',            ' ',  clean)
    clean = clean.strip()

    # Keep TTS short for speed (first 800 chars)
    if len(clean) > 800:
        clean = clean[:800] + "."

    try:
        tts = gTTS(text=clean, lang=lang_code, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read(), ""
    except Exception as e:
        return None, f"TTS error: {e}"
