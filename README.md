# 🌾 Kisan Sahayak - AI Agricultural Assistant

> An intelligent, multilingual agricultural assistant inspired by PMFBY portal design, powered by Groq LLM + FAISS offline search. Works online AND offline for rural connectivity.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA3-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Features

| Feature | Description | Offline? |
|---------|-------------|---------|
| 🤖 AI Chatbot | Natural language Q&A via Groq LLaMA3 | ✅ Partial |
| 🌿 Disease ID | Symptom-based disease diagnosis | ✅ Yes |
| 🐛 Pest Control | Organic + chemical control advice | ✅ Yes |
| 🧪 Fertilizer | Crop/soil/stage-based recommendations | ✅ Yes |
| 📋 Govt Schemes | PM-KISAN, PMFBY, KCC and more | ✅ Yes |
| 🌤 Weather | Real-time advisory + farming alerts | ❌ Needs API |
| 📊 Market Prices | Mandi prices + MSP data | ✅ MSP offline |
| 🌱 Crop Suggestion | AI-powered seasonal crop planning | ✅ Partial |
| 📚 Farmer Learning | Mini-courses on modern farming | ✅ Partial |
| 📈 Dashboard | Query analytics and insights | ✅ Yes |
| 🌍 Multi-Language | English, Hindi, Telugu | ✅ Yes |

---

## 🛠️ Quick Setup

### Prerequisites
- Python 3.9+
- Git
- A free [Groq API key](https://console.groq.com)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/kisan-sahayak.git
cd kisan-sahayak
```

### 2. Create Virtual Environment
```bash
# Create environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your keys
# On Windows: notepad .env
# On Linux/Mac: nano .env
```

Add your keys:
```env
GROQ_API_KEY=your_groq_api_key_here
WEATHER_API_KEY=your_openweathermap_key_here  # Optional
```

**Get free Groq API key:** https://console.groq.com (sign up, go to API Keys)

### 5. Run the App
```bash
streamlit run app.py
```

The app will open at: **http://localhost:8501**

---

## 📁 Project Structure

```
kisan-sahayak/
│
├── app.py                    # 🏠 Main Streamlit application
├── requirements.txt          # 📦 Python dependencies
├── .env.example             # 🔑 API keys template
├── .env                     # 🔑 Your actual API keys (never commit!)
├── .gitignore               # 🚫 Files to exclude from git
├── README.md                # 📖 This file
│
├── utils/                   # 🛠️ Utility modules
│   ├── __init__.py
│   ├── translations.py      # 🌍 Multi-language support (EN/HI/TE)
│   ├── groq_client.py       # 🤖 Groq LLM API client
│   ├── offline_search.py    # 💾 FAISS + keyword offline search
│   ├── weather.py           # 🌤 Weather API integration
│   ├── market_prices.py     # 📊 Mandi price data
│   └── query_logger.py      # 📝 Query logging for analytics
│
├── static/                  # 🎨 CSS and assets
│   └── style.css            # Government portal inspired styles
│
├── knowledge_base/          # 📚 Offline knowledge storage
│   └── agricultural_kb.json # Expandable Q&A database
│
├── data/                    # 📊 App data
│   └── query_logs.json      # Analytics logs (auto-created)
│
└── offline_data/            # 💾 Offline fallback data
    └── (CSV/JSON datasets)
```

---

## 🌍 Language Support

The entire UI switches language when you select:
- **English** - Default
- **हिंदी (Hindi)** - Complete translation
- **తెలుగు (Telugu)** - Complete translation

To add more languages, add entries in `utils/translations.py`.

---

## ⚙️ Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Groq LLaMA3 inference |
| `WEATHER_API_KEY` | ❌ No | OpenWeatherMap (mock data used without it) |

---

## 📴 Offline Mode

Toggle **Offline Mode** in the sidebar. In offline mode:
- Answers come from the local `OFFLINE_KB` in `utils/offline_search.py`
- No API calls made
- Works without internet for ~20 common agricultural topics

To expand offline knowledge:
```python
# In utils/offline_search.py, add to OFFLINE_KB:
{"q": "your question keywords", "a": "your detailed answer"}
```

---

## 🚀 Deployment

### Deploy to Streamlit Cloud (Free)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repo
4. Add secrets in Streamlit dashboard:
   ```
   GROQ_API_KEY = "your_key"
   WEATHER_API_KEY = "your_key"
   ```
5. Deploy!

### Deploy to Local Network (Village Kiosk)
```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```
Access from any device on network: `http://[your-IP]:8501`

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/add-language`
3. Make changes and test
4. Commit: `git commit -m 'Add Kannada language support'`
5. Push: `git push origin feature/add-language`
6. Open a Pull Request

---

## 📞 Support

- **Kisan Helpline:** 1800-180-1551 (Toll Free)
- **PM-KISAN:** https://pmkisan.gov.in
- **PMFBY:** https://pmfby.gov.in

---

## ⚠️ Disclaimer

This tool is for educational and informational purposes. Always consult local agricultural officers (KVK/Agriculture Department) for critical farming decisions.

---

## 📄 License

MIT License - feel free to use and modify for agricultural empowerment!

---

*Built with ❤️ for Indian farmers | जय जवान जय किसान*
