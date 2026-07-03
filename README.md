# 🌊 Bangladesh Flood Early Warning AI Agent

> *"In Bangladesh, the difference between life and loss is not the flood — it is the 20 hours of warning that never came."*

An autonomous AI agent that monitors river water levels and rainfall in real-time, reasons about flood risk using Gemini AI, and sends Bangla-language SMS alerts to community leaders — automatically, every hour, with no human involvement.

**Kaggle AI Agents Intensive — Vibe Coding Capstone 2026**
**Track:** Agents for Good | **SDG:** 13 · 11 · 3

---

## 🎯 The Problem

Every monsoon season, 20–25% of Bangladesh floods. Over 170 million people are at risk. Existing warning systems issue broad regional alerts too late — families in rural Sunamganj or Sylhet often get 2 hours notice or less. You cannot evacuate a family with elderly members and livestock in 2 hours. You need 22.

## ✅ The Solution

An AI agent that:
- 🔍 **Perceives** — reads river sensor data + 24hr rainfall forecasts every hour
- 🧠 **Reasons** — sends all data to Gemini AI for multi-variable flood risk classification
- 📊 **Decides** — classifies each district: SAFE / WATCH / WARNING / DANGER
- 📱 **Acts** — automatically sends Bangla SMS to village leaders for at-risk districts

No human presses a button. The agent runs at 3 AM on a Monday in August and nobody needs to be watching.

---

## 🏗️ Architecture

```
IoT Sensors (Water Level)  +  OpenWeather API (Rainfall)
                    ↓
            AI Reasoning Agent
          (Gemini 1.5 Flash)
                    ↓
     ┌──────────────┬──────────────┐
     ↓              ↓              ↓
Firebase DB    Bangla SMS      Dashboard
(data store)  (Twilio API)   (Flask + Leaflet)
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| AI Reasoning | Google Gemini 1.5 Flash |
| Database | Firebase Realtime Database |
| Weather Data | OpenWeather API |
| SMS Alerts | Twilio |
| Web Dashboard | Flask + Leaflet.js |
| Language | Python 3.11 |

---

## 📁 Project Structure

```
flood_agent/
├── agent.py              ← Main AI agent (runs every hour)
├── dashboard.py          ← Flask web dashboard
├── setup_contacts.py     ← One-time village leader contact setup
├── flood_dashboard.html  ← Standalone dashboard (open in browser)
├── firebase_key.json     ← Firebase credentials (not committed)
├── .env                  ← API keys (not committed)
├── requirements.txt      ← Python dependencies
└── logs/
    └── agent.log         ← Agent activity log
```

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/arifinalak/Flood-AI-Agent-Bangladesh.git
cd Flood-AI-Agent-Bangladesh
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
pip install google-genai
```

### 3. Set up API keys
Copy `.env.example` to `.env` and fill in your keys:
```
GEMINI_API_KEY=your_gemini_key
FIREBASE_DB_URL=https://your-project.firebasedatabase.app
OPENWEATHER_API_KEY=your_openweather_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE=+1xxxxxxxxxx
```

### 4. Add Firebase credentials
Place your `firebase_key.json` in the project root.

### 5. Add village leader contacts (run once)
```bash
python setup_contacts.py
```

### 6. Run the agent
```bash
python agent.py
```

### 7. Open the dashboard (in a second terminal)
```bash
python dashboard.py
```
Then open `http://localhost:5000` in your browser.

---

## 🔑 API Keys Required

| API | Where to get | Cost |
|---|---|---|
| Gemini API | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Free |
| Firebase | [console.firebase.google.com](https://console.firebase.google.com) | Free |
| OpenWeather | [openweathermap.org](https://home.openweathermap.org/api_keys) | Free |
| Twilio SMS | [twilio.com](https://www.twilio.com/try-twilio) | Free trial |

---

## 🤖 How the Agent Works

Every 60 minutes, the agent runs a 6-step cycle:

```
[1] Fetch water levels    → River sensor stations (BWDB / simulated)
[2] Fetch rainfall        → OpenWeather 24hr forecast per district
[3] Gemini AI reasons     → Risk classification + Bangla SMS generation
[4] Save to Firebase      → Powers live dashboard
[5] Send SMS alerts       → Twilio → village leaders (WARNING/DANGER only)
[6] Log results           → Audit trail for accuracy tracking
```

---

## 📊 Risk Classification

| Level | Condition | Action |
|---|---|---|
| 🟢 SAFE | Water < 70% · Rain < 30mm | Log only |
| 🟡 WATCH | Water 70–85% OR Rain 30–60mm | Leaders notified |
| 🟠 WARNING | Water 85–95% OR Rain 60–100mm | SMS sent |
| 🔴 DANGER | Water > 95% OR Rain > 100mm | SMS + DDMC alerted |

---

## 💬 Sample Bangla Alert

```
সুনামগঞ্জে আগামী ১৮ ঘণ্টায় বন্যার উচ্চ ঝুঁকি।
গবাদি পশু সরান এবং পরিবারসহ নিরাপদ স্থানে যান।
```
*"High flood risk in Sunamganj in next 18 hours. Move livestock and relocate family to safe ground."*

---

## 🌍 SDG Impact

- **SDG 13** (Climate Action) — Builds adaptive capacity in one of the world's most climate-vulnerable nations
- **SDG 11** (Sustainable Cities) — Reduces disaster risk for rural and urban communities
- **SDG 3** (Good Health) — Reduces flood mortality through preventive evacuation

---

## ⚠️ Important Notes

- `firebase_key.json` and `.env` are **not committed** to this repo — never share these publicly
- Sensor data is **simulated** for the Kaggle demo — production would use live BWDB telemetry
- Twilio free trial can only SMS **verified numbers** — upgrade for unrestricted Bangladesh SMS

---

## 👤 Author

**Sayed Arifin Ahmed Alak** — CSE Student, Brac University, Bangladesh.
Kaggle AI Agents Intensive Capstone 2026

---

## 📄 License

MIT License — free to use, modify, and deploy for humanitarian purposes.
