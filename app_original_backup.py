import streamlit as st
import json
import os
from utils.translations import get_text, LANGUAGES
from utils.groq_client import get_groq_response
from utils.weather import get_weather
from utils.offline_search import search_offline
from utils.query_logger import log_query
from utils.market_prices import get_market_prices
import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kisan Sahayak | AI Agricultural Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Session State Defaults ────────────────────────────────────────────────────
if "language" not in st.session_state:
    st.session_state.language = "English"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "online_mode" not in st.session_state:
    st.session_state.online_mode = True
if "farmer_name" not in st.session_state:
    st.session_state.farmer_name = ""
if "farmer_location" not in st.session_state:
    st.session_state.farmer_location = ""
if "active_page" not in st.session_state:
    st.session_state.active_page = "home"

lang = st.session_state.language
t = lambda key: get_text(key, lang)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="gov-header">
    <div class="gov-header-left">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/200px-Emblem_of_India.svg.png" height="50" alt="Emblem">
        <div class="gov-title">
            <span class="gov-title-hindi">भारत सरकार | Government of India</span><br>
            <span class="gov-title-dept">Ministry of Agriculture &amp; Farmers Welfare</span>
        </div>
    </div>
    <div class="gov-header-right">
        <span class="helpline">📞 Kisan Call Centre: 1800-180-1551</span>
    </div>
</div>
<div class="main-banner">
    <div class="banner-logo">🌾</div>
    <div class="banner-text">
        <h1 class="banner-title">{t('app_title')}</h1>
        <p class="banner-subtitle">{t('app_subtitle')}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ Settings</div>', unsafe_allow_html=True)

    # Language selector
    st.markdown(f'<div class="sidebar-label">{t("select_language")}</div>', unsafe_allow_html=True)
    selected_lang = st.selectbox("", list(LANGUAGES.keys()), 
                                  index=list(LANGUAGES.keys()).index(lang),
                                  key="lang_select", label_visibility="collapsed")
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

    # Online/Offline toggle
    st.markdown("---")
    online = st.toggle(t("online_mode"), value=st.session_state.online_mode)
    st.session_state.online_mode = online
    if online:
        st.success(f"🟢 {t('online_active')}")
    else:
        st.warning(f"🔴 {t('offline_active')}")

    # Farmer info
    st.markdown("---")
    st.markdown(f'<div class="sidebar-label">👨‍🌾 {t("farmer_info")}</div>', unsafe_allow_html=True)
    st.session_state.farmer_name = st.text_input(t("your_name"), value=st.session_state.farmer_name)
    st.session_state.farmer_location = st.text_input(t("your_location"), value=st.session_state.farmer_location)

    # Navigation
    st.markdown("---")
    st.markdown(f'<div class="sidebar-label">📋 {t("navigation")}</div>', unsafe_allow_html=True)
    pages = {
        "home": f"🏠 {t('home')}",
        "chatbot": f"🤖 {t('ai_chatbot')}",
        "disease": f"🌿 {t('disease_id')}",
        "pest": f"🐛 {t('pest_control')}",
        "fertilizer": f"🧪 {t('fertilizer')}",
        "schemes": f"📋 {t('govt_schemes')}",
        "weather": f"🌤 {t('weather')}",
        "market": f"📊 {t('market_prices')}",
        "crops": f"🌱 {t('crop_suggest')}",
        "learning": f"📚 {t('learning')}",
        "dashboard": f"📈 {t('dashboard')}",
    }
    for page_key, page_label in pages.items():
        if st.button(page_label, key=f"nav_{page_key}", use_container_width=True):
            st.session_state.active_page = page_key
            st.rerun()

    st.markdown("---")
    if st.button(f"🗑️ {t('clear_chat')}", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ── Main Content ──────────────────────────────────────────────────────────────
active = st.session_state.active_page

# Navigation tabs display
nav_html = '<div class="nav-tabs">'
for page_key, page_label in pages.items():
    active_class = "active" if page_key == active else ""
    nav_html += f'<span class="nav-tab {active_class}" onclick="void(0)">{page_label}</span>'
nav_html += '</div>'
st.markdown(nav_html, unsafe_allow_html=True)

# ─────────────────────────── HOME PAGE ──────────────────────────────────────
if active == "home":
    st.markdown(f'<h2 class="section-title">{t("welcome_message")}</h2>', unsafe_allow_html=True)
    
    # Feature cards
    cards_data = [
        ("🤖", t("ai_chatbot"), t("chatbot_desc"), "chatbot", "#2d6a4f"),
        ("🌿", t("disease_id"), t("disease_desc"), "disease", "#40916c"),
        ("🐛", t("pest_control"), t("pest_desc"), "pest", "#52b788"),
        ("🧪", t("fertilizer"), t("fertilizer_desc"), "fertilizer", "#74c69d"),
        ("📋", t("govt_schemes"), t("schemes_desc"), "schemes", "#1b4332"),
        ("🌤", t("weather"), t("weather_desc"), "weather", "#081c15"),
        ("📊", t("market_prices"), t("market_desc"), "market", "#2d6a4f"),
        ("🌱", t("crop_suggest"), t("crop_desc"), "crops", "#40916c"),
        ("📚", t("learning"), t("learning_desc"), "learning", "#52b788"),
        ("📈", t("dashboard"), t("dashboard_desc"), "dashboard", "#1b4332"),
    ]

    cols = st.columns(5)
    for i, (icon, title, desc, page, color) in enumerate(cards_data):
        with cols[i % 5]:
            st.markdown(f"""
            <div class="feature-card" style="border-top: 4px solid {color}">
                <div class="card-icon">{icon}</div>
                <div class="card-title">{title}</div>
                <div class="card-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(t("explore"), key=f"card_{page}", use_container_width=True):
                st.session_state.active_page = page
                st.rerun()

    # Quick stats
    st.markdown("---")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("🌾 " + t("crops_covered"), "500+")
    with s2:
        st.metric("🐛 " + t("pests_database"), "200+")
    with s3:
        st.metric("📋 " + t("schemes_listed"), "25+")
    with s4:
        st.metric("🌍 " + t("languages"), "3")

# ─────────────────────────── CHATBOT PAGE ────────────────────────────────────
elif active == "chatbot":
    from utils.voice import transcribe_audio, text_to_speech_bytes

    # ── session defaults for voice ────────────────────────────────────────────
    if "voice_transcript" not in st.session_state:
        st.session_state.voice_transcript = ""
    if "last_audio_hash" not in st.session_state:
        st.session_state.last_audio_hash = None
    if "tts_audio_bytes" not in st.session_state:
        st.session_state.tts_audio_bytes = None

    st.markdown(f'<h2 class="section-title">🤖 {t("ai_chatbot")}</h2>', unsafe_allow_html=True)

    # ── Chat display ──────────────────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown(f"""
            <div class="chat-welcome">
                <div class="chat-welcome-icon">🌾</div>
                <h3>{t("chat_welcome")}</h3>
                <p>{t("chat_welcome_desc")}</p>
            </div>
            """, unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-msg user-msg">👨‍🌾 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-msg bot-msg">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    # ── TTS playback — shown right after chat history ─────────────────────────
    # Placed here so it appears immediately after the answer and auto-plays
    if st.session_state.tts_audio_bytes:
        st.info("🔊 Playing voice answer...")
        st.audio(st.session_state.tts_audio_bytes, format="audio/mp3", autoplay=True)
        if st.button("🔇 Stop / Clear Voice", key="clear_tts"):
            st.session_state.tts_audio_bytes = None
            st.rerun()

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    #  🎙️  VOICE INPUT  — record mic → transcribe → show text → get AI answer
    # ══════════════════════════════════════════════════════════════════════════
    try:
        from audio_recorder_streamlit import audio_recorder

        st.markdown("**🎙️ Voice Input** — click the mic icon below, speak your question, then click again to stop:")

        audio_bytes = audio_recorder(
            text="",                  # no label; icon only
            recording_color="#e74c3c",
            neutral_color="#2d6a4f",
            icon_name="microphone",
            icon_size="2x",
            pause_threshold=2.5,      # auto-stops after 2.5s silence
            sample_rate=16000,
            key="voice_recorder",
        )

        if audio_bytes:
            # Use a hash so we only process each new recording once
            import hashlib
            audio_hash = hashlib.md5(audio_bytes).hexdigest()

            if audio_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = audio_hash

                with st.spinner("🎧 Transcribing your voice..."):
                    transcript, err = transcribe_audio(audio_bytes, lang)

                if err:
                    st.error(err)
                elif transcript:
                    # Show what was heard
                    st.success(f"🎙️ **You said:** {transcript}")
                    st.session_state.voice_transcript = transcript

                    # ── Get AI answer ─────────────────────────────────────────
                    with st.spinner(t("thinking")):
                        offline_ans = search_offline(transcript)
                        if st.session_state.online_mode:
                            ans = get_groq_response(transcript, lang, context=offline_ans)
                        else:
                            ans = f"[{t('offline_mode')}]\n\n{offline_ans}"

                    # Add to chat history
                    st.session_state.chat_history.append({"role": "user",      "content": transcript})
                    st.session_state.chat_history.append({"role": "assistant", "content": ans})
                    log_query(st.session_state.farmer_name, st.session_state.farmer_location, transcript, "chatbot")

                    # ── Generate TTS audio ────────────────────────────────────
                    with st.spinner("🔊 Generating voice answer..."):
                        mp3_bytes, tts_err = text_to_speech_bytes(ans, lang)

                    if tts_err:
                        st.warning(tts_err)
                    else:
                        st.session_state.tts_audio_bytes = mp3_bytes

                    st.rerun()   # re-render chat + trigger audio playback
                else:
                    st.warning("⚠️ No speech detected. Please speak clearly and try again.")

    except ImportError:
        st.warning("⚠️ Voice input unavailable. Install it with: `pip install audio-recorder-streamlit`")

    st.markdown("---")

    # ── Sample queries ────────────────────────────────────────────────────────
    st.markdown(f'<div class="sample-queries-title">{t("sample_queries")}:</div>', unsafe_allow_html=True)
    sample_qs = [
        t("sample_q1"), t("sample_q2"), t("sample_q3"), t("sample_q4")
    ]
    sq_cols = st.columns(4)
    for i, sq in enumerate(sample_qs):
        with sq_cols[i]:
            if st.button(sq, key=f"sq_{i}", use_container_width=True):
                st.session_state.tts_audio_bytes = None
                st.session_state.chat_history.append({"role": "user", "content": sq})
                with st.spinner(t("thinking")):
                    offline_ans = search_offline(sq)
                    if st.session_state.online_mode:
                        ans = get_groq_response(sq, lang, context=offline_ans)
                    else:
                        ans = f"[{t('offline_mode')}]\n\n{offline_ans}"
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
                log_query(st.session_state.farmer_name, st.session_state.farmer_location, sq, "chatbot")
                # Generate TTS for sample query answer too
                mp3_bytes, _ = text_to_speech_bytes(ans, lang)
                if mp3_bytes:
                    st.session_state.tts_audio_bytes = mp3_bytes
                st.rerun()

    # ── Text input (unchanged) ────────────────────────────────────────────────
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input("", placeholder=t("type_query"), key="chat_input", label_visibility="collapsed")
    with col_send:
        send = st.button(f"📤 {t('send')}", use_container_width=True)

    if send and user_input:
        st.session_state.tts_audio_bytes = None
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner(t("thinking")):
            offline_ans = search_offline(user_input)
            if st.session_state.online_mode:
                ans = get_groq_response(user_input, lang, context=offline_ans)
            else:
                ans = f"[{t('offline_mode')}]\n\n{offline_ans}"
        st.session_state.chat_history.append({"role": "assistant", "content": ans})
        log_query(st.session_state.farmer_name, st.session_state.farmer_location, user_input, "chatbot")
        # TTS for typed queries too
        with st.spinner("🔊 Generating voice answer..."):
            mp3_bytes, _ = text_to_speech_bytes(ans, lang)
        if mp3_bytes:
            st.session_state.tts_audio_bytes = mp3_bytes
        st.rerun()

# ─────────────────────────── DISEASE PAGE ────────────────────────────────────
elif active == "disease":
    st.markdown(f'<h2 class="section-title">🌿 {t("disease_id")}</h2>', unsafe_allow_html=True)
    
    d1, d2 = st.columns([1, 1])
    with d1:
        crop_type = st.selectbox(t("select_crop"), [
            t("select_one"), "Wheat/गेहूं", "Rice/चावल", "Cotton/कपास", 
            "Tomato/टमाटर", "Potato/आलू", "Maize/मक्का", "Mustard/सरसों",
            "Brinjal/बैंगन", "Onion/प्याज", "Other/अन्य"
        ])
        symptoms = st.text_area(t("describe_symptoms"), height=120, 
                                 placeholder=t("symptom_placeholder"))
        uploaded_img = st.file_uploader(t("upload_crop_image"), 
                                         type=["jpg", "jpeg", "png"],
                                         help=t("image_help"))
    
    with d2:
        if uploaded_img:
            st.image(uploaded_img, caption=t("uploaded_image"), use_container_width=True)

    if st.button(f"🔍 {t('identify_disease')}", type="primary"):
        if symptoms or uploaded_img:
            query = f"Crop disease identification for {crop_type}. Symptoms: {symptoms}"
            with st.spinner(t("analyzing")):
                offline_ans = search_offline(query)
                if st.session_state.online_mode:
                    prompt = f"""You are an expert agricultural plant pathologist. A farmer describes symptoms on {crop_type} crop: "{symptoms}". 
                    
                    Provide in {lang}:
                    1. **Possible Disease(s)** - Name and scientific name
                    2. **Causes** - What causes this disease
                    3. **Treatment Methods** - Step-by-step treatment
                    4. **Preventive Measures** - How to prevent in future
                    5. **When to consult expert** - Severity assessment
                    
                    Also reference this offline data if relevant: {offline_ans[:500]}"""
                    result = get_groq_response(prompt, lang)
                else:
                    result = offline_ans
            
            st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
            log_query(st.session_state.farmer_name, st.session_state.farmer_location, query, "disease")
        else:
            st.warning(t("please_describe"))

# ─────────────────────────── PEST CONTROL PAGE ───────────────────────────────
elif active == "pest":
    st.markdown(f'<h2 class="section-title">🐛 {t("pest_control")}</h2>', unsafe_allow_html=True)
    
    p1, p2 = st.columns(2)
    with p1:
        pest_crop = st.selectbox(t("select_crop"), [
            t("select_one"), "Wheat", "Rice", "Cotton", "Tomato", "Potato", 
            "Maize", "Mustard", "Brinjal", "Onion", "Sugarcane", "Other"
        ])
        pest_query = st.text_area(t("describe_pest"), height=100, 
                                   placeholder=t("pest_placeholder"))
        control_pref = st.radio(t("control_preference"), 
                                 [t("organic_only"), t("chemical_only"), t("both_methods")])
    
    with p2:
        st.markdown(f'<div class="info-box"><b>💡 {t("common_pests")}:</b><br>• Aphids<br>• Whitefly<br>• Jassids<br>• Fruit Borer<br>• Stem Borer<br>• Thrips<br>• Mites</div>', unsafe_allow_html=True)

    if st.button(f"🔍 {t('get_pest_advice')}", type="primary"):
        if pest_query:
            query = f"Pest control for {pest_crop}: {pest_query}. Preference: {control_pref}"
            with st.spinner(t("fetching_advice")):
                offline_ans = search_offline(query)
                if st.session_state.online_mode:
                    prompt = f"""Agricultural pest control expert. Farmer has pest problem on {pest_crop}: "{pest_query}". They prefer {control_pref}.
                    
                    Respond in {lang} with:
                    1. **Pest Identification** - Name and characteristics
                    2. **Organic Control** - Natural remedies, neem oil, etc.
                    3. **Chemical Control** - Pesticide names and dosage
                    4. **Application Method** - How and when to apply
                    5. **Safety Precautions** - PPE and safety
                    6. **Cost Estimate** - Approximate cost per acre
                    
                    Offline reference data: {offline_ans[:500]}"""
                    result = get_groq_response(prompt, lang)
                else:
                    result = offline_ans
            st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
            log_query(st.session_state.farmer_name, st.session_state.farmer_location, query, "pest")

# ─────────────────────────── FERTILIZER PAGE ─────────────────────────────────
elif active == "fertilizer":
    st.markdown(f'<h2 class="section-title">🧪 {t("fertilizer")}</h2>', unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns(3)
    with f1:
        fert_crop = st.selectbox(t("crop_type"), [
            "Wheat", "Rice", "Cotton", "Tomato", "Potato", "Maize", 
            "Mustard", "Sugarcane", "Soybean", "Other"
        ])
        growth_stage = st.selectbox(t("growth_stage"), [
            t("stage_sowing"), t("stage_germination"), t("stage_vegetative"),
            t("stage_flowering"), t("stage_fruiting"), t("stage_harvest")
        ])
    with f2:
        soil_type = st.selectbox(t("soil_type"), [
            t("soil_clay"), t("soil_loamy"), t("soil_sandy"), 
            t("soil_black"), t("soil_red"), t("soil_alluvial")
        ])
        area_acres = st.number_input(t("area_acres"), min_value=0.5, max_value=100.0, value=1.0, step=0.5)
    with f3:
        last_fertilizer = st.text_input(t("last_fertilizer_used"), placeholder="e.g., Urea, DAP")
        deficiency_symptoms = st.text_area(t("deficiency_symptoms"), height=80, placeholder=t("deficiency_placeholder"))

    if st.button(f"🧪 {t('get_recommendation')}", type="primary"):
        query = f"Fertilizer recommendation for {fert_crop}, {soil_type} soil, {growth_stage} stage, {area_acres} acres"
        with st.spinner(t("calculating")):
            offline_ans = search_offline(query)
            if st.session_state.online_mode:
                prompt = f"""Agricultural fertilizer expert. Farmer needs fertilizer recommendation:
                - Crop: {fert_crop}
                - Growth Stage: {growth_stage}
                - Soil Type: {soil_type}
                - Area: {area_acres} acres
                - Last fertilizer used: {last_fertilizer}
                - Deficiency symptoms: {deficiency_symptoms}
                
                Respond in {lang} with:
                1. **Recommended Fertilizers** - NPK ratio and types
                2. **Dosage per Acre** - Exact quantities
                3. **Total Quantity for {area_acres} Acres** - Calculated amounts
                4. **Application Method** - Broadcasting, foliar, drip
                5. **Application Timing** - Best time to apply
                6. **Cost Estimate** - Approx price
                7. **Precautions** - Do's and Don'ts
                
                Reference: {offline_ans[:400]}"""
                result = get_groq_response(prompt, lang)
            else:
                result = offline_ans
        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
        log_query(st.session_state.farmer_name, st.session_state.farmer_location, query, "fertilizer")

# ─────────────────────────── SCHEMES PAGE ────────────────────────────────────
elif active == "schemes":
    st.markdown(f'<h2 class="section-title">📋 {t("govt_schemes")}</h2>', unsafe_allow_html=True)
    
    schemes = [
        {
            "name": "PM-KISAN Samman Nidhi",
            "icon": "💰",
            "benefit": "₹6,000/year in 3 installments",
            "eligibility": "All small/marginal farmers with cultivable land",
            "link": "https://pmkisan.gov.in",
            "color": "#2d6a4f"
        },
        {
            "name": "PM Fasal Bima Yojana (PMFBY)",
            "icon": "🌾",
            "benefit": "Crop insurance at subsidized premium",
            "eligibility": "All farmers growing notified crops",
            "link": "https://pmfby.gov.in",
            "color": "#40916c"
        },
        {
            "name": "Kisan Credit Card (KCC)",
            "icon": "💳",
            "benefit": "Short-term credit up to ₹3 lakh at 4% interest",
            "eligibility": "Farmers, fishermen, poultry farmers",
            "link": "https://www.nabard.org",
            "color": "#52b788"
        },
        {
            "name": "PM Krishi Sinchayee Yojana",
            "icon": "💧",
            "benefit": "Subsidy for irrigation equipment",
            "eligibility": "All categories of farmers",
            "link": "https://pmksy.gov.in",
            "color": "#1b4332"
        },
        {
            "name": "eNAM - National Agriculture Market",
            "icon": "🏪",
            "benefit": "Online mandi for better crop prices",
            "eligibility": "All farmers",
            "link": "https://enam.gov.in",
            "color": "#2d6a4f"
        },
        {
            "name": "Soil Health Card Scheme",
            "icon": "🌱",
            "benefit": "Free soil testing and crop advisory",
            "eligibility": "All farmers",
            "link": "https://soilhealth.dac.gov.in",
            "color": "#40916c"
        },
    ]

    # Search scheme
    scheme_search = st.text_input(f"🔍 {t('search_scheme')}", placeholder=t("scheme_search_placeholder"))
    
    for scheme in schemes:
        if scheme_search.lower() in scheme["name"].lower() or not scheme_search:
            with st.expander(f"{scheme['icon']} {scheme['name']}", expanded=False):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**💰 {t('benefit')}:** {scheme['benefit']}")
                with c2:
                    st.markdown(f"**✅ {t('eligibility')}:** {scheme['eligibility']}")
                with c3:
                    st.markdown(f"**🔗 {t('website')}:** [{scheme['link']}]({scheme['link']})")
                
                if st.button(f"❓ {t('ask_ai_about')} {scheme['name']}", key=f"scheme_{scheme['name']}"):
                    query = f"How to apply for {scheme['name']}? What documents are needed? What is the process?"
                    with st.spinner(t("fetching_info")):
                        if st.session_state.online_mode:
                            result = get_groq_response(query, lang)
                        else:
                            result = search_offline(query)
                    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

# ─────────────────────────── WEATHER PAGE ────────────────────────────────────
elif active == "weather":
    st.markdown(f'<h2 class="section-title">🌤 {t("weather")}</h2>', unsafe_allow_html=True)
    
    location_input = st.text_input(t("enter_location"), 
                                    value=st.session_state.farmer_location or "Hyderabad",
                                    placeholder="e.g., Hyderabad, Delhi, Mumbai")
    
    if st.button(f"🌦 {t('get_weather')}", type="primary") or location_input:
        weather_data = get_weather(location_input)
        if weather_data:
            w1, w2, w3, w4 = st.columns(4)
            with w1:
                st.metric("🌡️ " + t("temperature"), f"{weather_data.get('temp', 'N/A')}°C")
            with w2:
                st.metric("💧 " + t("humidity"), f"{weather_data.get('humidity', 'N/A')}%")
            with w3:
                st.metric("🌬️ " + t("wind_speed"), f"{weather_data.get('wind', 'N/A')} km/h")
            with w4:
                st.metric("⛅ " + t("condition"), weather_data.get('condition', 'N/A'))
            
            # Farming advisory based on weather
            if st.session_state.online_mode:
                with st.spinner(t("generating_advisory")):
                    advisory_prompt = f"""Based on current weather in {location_input}: 
                    Temperature {weather_data.get('temp')}°C, Humidity {weather_data.get('humidity')}%, 
                    Condition: {weather_data.get('condition')}.
                    
                    Provide farming advisory in {lang}:
                    1. Irrigation recommendation
                    2. Pesticide/spraying advice (suitable time)
                    3. Harvesting advice
                    4. Crop protection measures
                    5. Next 3 days outlook for farming activities"""
                    advisory = get_groq_response(advisory_prompt, lang)
                st.markdown(f"### 🌾 {t('farming_advisory')}")
                st.markdown(f'<div class="result-box">{advisory}</div>', unsafe_allow_html=True)
        else:
            st.info(t("weather_offline_msg"))

# ─────────────────────────── MARKET PRICES PAGE ──────────────────────────────
elif active == "market":
    st.markdown(f'<h2 class="section-title">📊 {t("market_prices")}</h2>', unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    with m1:
        market_state = st.selectbox(t("select_state"), [
            "Andhra Pradesh", "Telangana", "Maharashtra", "Punjab", 
            "Haryana", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Other"
        ])
    with m2:
        market_crop = st.selectbox(t("select_crop_price"), [
            "Wheat", "Rice", "Cotton", "Tomato", "Onion", "Potato", 
            "Maize", "Sugarcane", "Soybean", "Mustard"
        ])

    prices = get_market_prices(market_state, market_crop)
    
    st.markdown(f"### 📈 {t('current_prices')} - {market_crop} in {market_state}")
    
    if prices:
        for mandi, price_info in prices.items():
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric(f"🏪 {mandi}", f"₹{price_info['modal_price']}/quintal")
            with col_b:
                st.metric(t("min_price"), f"₹{price_info['min_price']}")
            with col_c:
                st.metric(t("max_price"), f"₹{price_info['max_price']}")
    else:
        st.info(t("market_data_offline"))
        # Show MSP data from offline knowledge base
        st.markdown(f"### 📋 {t('msp_prices')} 2024-25")
        msp_data = {
            "Wheat": "₹2,275/quintal", "Rice (Common)": "₹2,300/quintal",
            "Cotton": "₹7,121/quintal", "Maize": "₹2,225/quintal",
            "Mustard": "₹5,950/quintal", "Soybean": "₹4,892/quintal"
        }
        for crop, msp in msp_data.items():
            st.markdown(f"• **{crop}**: {msp}")

# ─────────────────────────── CROP SUGGESTION PAGE ────────────────────────────
elif active == "crops":
    st.markdown(f'<h2 class="section-title">🌱 {t("crop_suggest")}</h2>', unsafe_allow_html=True)
    
    cs1, cs2 = st.columns(2)
    with cs1:
        cs_state = st.selectbox(t("your_state"), [
            "Telangana", "Andhra Pradesh", "Maharashtra", "Punjab", 
            "Haryana", "Uttar Pradesh", "Karnataka", "Tamil Nadu"
        ])
        cs_soil = st.selectbox(t("soil_type"), [
            t("soil_black"), t("soil_red"), t("soil_alluvial"), 
            t("soil_loamy"), t("soil_sandy"), t("soil_clay")
        ])
        cs_season = st.selectbox(t("current_season"), [
            "Kharif (June-October)", "Rabi (November-April)", "Zaid (March-June)"
        ])
    with cs2:
        cs_water = st.selectbox(t("water_availability"), [
            t("water_rainfed"), t("water_canal"), t("water_borewell"), t("water_drip")
        ])
        cs_budget = st.selectbox(t("investment_budget"), [
            "Low (< ₹10,000/acre)", "Medium (₹10,000-25,000/acre)", "High (> ₹25,000/acre)"
        ])
        cs_market = st.multiselect(t("target_market"), [
            t("local_market"), t("export"), t("processing_industry"), t("contract_farming")
        ])

    if st.button(f"🌱 {t('suggest_crops')}", type="primary"):
        query = f"Crop suggestion for {cs_state}, {cs_soil} soil, {cs_season} season, {cs_water} water, {cs_budget} budget"
        with st.spinner(t("analyzing")):
            if st.session_state.online_mode:
                prompt = f"""Agricultural expert for Indian farming. Suggest best crops for:
                - State: {cs_state}
                - Soil: {cs_soil}
                - Season: {cs_season}
                - Water: {cs_water}
                - Budget: {cs_budget}
                - Target market: {', '.join(cs_market) if cs_market else 'Local'}
                
                Respond in {lang} with:
                1. **Top 5 Recommended Crops** with profitability ranking
                2. **Expected Income** per acre
                3. **Investment Required** per acre
                4. **Market Demand** - current trends
                5. **Risks** - weather and market risks
                6. **Intercropping Options** - complementary crops"""
                result = get_groq_response(prompt, lang)
            else:
                result = search_offline(query)
        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
        log_query(st.session_state.farmer_name, st.session_state.farmer_location, query, "crop_suggestion")

# ─────────────────────────── LEARNING PAGE ───────────────────────────────────
elif active == "learning":
    st.markdown(f'<h2 class="section-title">📚 {t("learning")}</h2>', unsafe_allow_html=True)
    
    topics = [
        ("🌿", t("learn_organic"), t("learn_organic_desc"), "organic farming techniques, crop rotation, composting"),
        ("💧", t("learn_drip"), t("learn_drip_desc"), "drip irrigation setup, water saving, micro irrigation"),
        ("🌱", t("learn_sustainable"), t("learn_sustainable_desc"), "sustainable farming, soil health, biodiversity"),
        ("🐄", t("learn_integrated"), t("learn_integrated_desc"), "integrated farming, livestock and crops together"),
        ("💊", t("learn_ipm"), t("learn_ipm_desc"), "integrated pest management, biological control"),
        ("📱", t("learn_digital"), t("learn_digital_desc"), "digital tools for farming, mobile apps, precision agriculture"),
    ]

    for i in range(0, len(topics), 3):
        cols = st.columns(3)
        for j, (icon, title, desc, query_topic) in enumerate(topics[i:i+3]):
            with cols[j]:
                st.markdown(f"""
                <div class="learn-card">
                    <div class="card-icon">{icon}</div>
                    <div class="card-title">{title}</div>
                    <div class="card-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"📖 {t('start_learning')}", key=f"learn_{i}_{j}", use_container_width=True):
                    with st.spinner(t("loading_content")):
                        if st.session_state.online_mode:
                            prompt = f"""Create a beginner-friendly mini-course on {query_topic} for Indian farmers.
                            
                            Respond in {lang} with:
                            1. **Introduction** - What and Why
                            2. **Key Concepts** - 5 important points
                            3. **Step-by-Step Guide** - How to implement
                            4. **Benefits** - Economic and environmental
                            5. **Common Mistakes** - What to avoid
                            6. **Resources** - Where to learn more
                            
                            Keep it practical and simple for rural farmers."""
                            result = get_groq_response(prompt, lang)
                        else:
                            result = search_offline(query_topic)
                    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

# ─────────────────────────── DASHBOARD PAGE ──────────────────────────────────
elif active == "dashboard":
    st.markdown(f'<h2 class="section-title">📈 {t("dashboard")}</h2>', unsafe_allow_html=True)
    
    # Load query logs
    try:
        with open("data/query_logs.json", "r") as f:
            logs = json.load(f)
    except:
        logs = []

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.metric("📊 " + t("total_queries"), len(logs))
    with d2:
        disease_q = sum(1 for l in logs if l.get("type") == "disease")
        st.metric("🌿 " + t("disease_queries"), disease_q)
    with d3:
        pest_q = sum(1 for l in logs if l.get("type") == "pest")
        st.metric("🐛 " + t("pest_queries"), pest_q)
    with d4:
        fert_q = sum(1 for l in logs if l.get("type") == "fertilizer")
        st.metric("🧪 " + t("fertilizer_queries"), fert_q)

    st.markdown(f"### 📋 {t('recent_queries')}")
    if logs:
        import pandas as pd
        df = pd.DataFrame(logs[-20:])
        st.dataframe(df, use_container_width=True)
    else:
        st.info(t("no_queries_yet"))

    # Query type distribution
    if logs:
        st.markdown(f"### 📊 {t('query_distribution')}")
        import pandas as pd
        type_counts = {}
        for l in logs:
            qtype = l.get("type", "other")
            type_counts[qtype] = type_counts.get(qtype, 0) + 1
        df_chart = pd.DataFrame(list(type_counts.items()), columns=["Type", "Count"])
        st.bar_chart(df_chart.set_index("Type"))

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    <div class="footer-content">
        <div>🌾 {t('app_title')} | {t('footer_ministry')}</div>
        <div>📞 Kisan Helpline: 1800-180-1551 | 🌐 kisanportal.gov.in</div>
        <div class="footer-note">{t('footer_note')}</div>
    </div>
</div>
""", unsafe_allow_html=True)
