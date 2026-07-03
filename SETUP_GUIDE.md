# Bangladesh Flood Early Warning Agent — Setup Guide

## What You'll Build
An AI agent that:
- Reads river water levels + rainfall data every hour
- Uses Gemini AI to reason about flood risk
- Sends Bangla SMS alerts to village leaders automatically
- Shows a live map dashboard

---

## STEP 1 — Install VS Code
1. Go to https://code.visualstudio.com
2. Download and install for Windows
3. Open VS Code → open a new folder called `flood_agent`
4. Open the terminal: View → Terminal (or Ctrl + `)

---

## STEP 2 — Install Python
1. Go to https://www.python.org/downloads
2. Download Python 3.11 or newer
3. During install: CHECK "Add Python to PATH"
4. Verify in VS Code terminal:
   ```
   python --version
   ```

---

## STEP 3 — Install all packages
In VS Code terminal, run:
```bash
pip install google-generativeai firebase-admin twilio flask requests python-dotenv
```

---

## STEP 4 — Get Gemini AI API Key (Free)
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key — you'll need it soon

---

## STEP 5 — Set up Firebase (Free)
1. Go to: https://console.firebase.google.com
2. Click "Create a project" → name it "flood-agent-bd"
3. Go to "Realtime Database" → Create database → Start in test mode
4. Copy the database URL (looks like: https://flood-agent-bd-default-rtdb.firebaseio.com)
5. Go to Project Settings → Service Accounts
6. Click "Generate new private key" → download JSON file
7. Rename it to `firebase_key.json`
8. Place it in your `flood_agent` folder

---

## STEP 6 — Get OpenWeather API Key (Free)
1. Go to: https://openweathermap.org
2. Sign up for free account
3. Go to: https://home.openweathermap.org/api_keys
4. Copy your API key

---

## STEP 7 — Get Twilio SMS (Free trial)
1. Go to: https://www.twilio.com/try-twilio
2. Sign up for free account (gives you $15 credit)
3. From Console dashboard, copy:
   - Account SID
   - Auth Token
   - Your Twilio phone number

---

## STEP 8 — Create your .env file
1. Copy `.env.example` → rename to `.env`
2. Fill in all your keys:
```
GEMINI_API_KEY=AIza...your key...
FIREBASE_DB_URL=https://flood-agent-bd-default-rtdb.firebaseio.com
OPENWEATHER_API_KEY=abc123...your key...
TWILIO_ACCOUNT_SID=ACxxx...
TWILIO_AUTH_TOKEN=xxx...
TWILIO_PHONE=+1234567890
```

---

## STEP 9 — Add village leader contacts
Edit `setup_contacts.py` — replace phone numbers with real ones.
Then run ONCE:
```bash
python setup_contacts.py
```

---

## STEP 10 — Test the agent (single run)
```bash
python agent.py
```
You should see:
```
[1] Fetching water levels...
[2] Fetching rainfall forecasts...
[3] Gemini analyzing flood risk...
[4] Saving to Firebase...
[5] Sending SMS alerts...
[6] Logging...
Cycle complete. Next run in 1 hour.
```

---

## STEP 11 — Open the dashboard
In a second terminal tab, run:
```bash
python dashboard.py
```
Then open your browser: http://localhost:5000

You'll see a live map of Bangladesh with color-coded flood risk zones.

---

## STEP 12 — Keep agent running 24/7 (optional)
For always-on running, use Windows Task Scheduler or deploy to Google Cloud Run.
For Kaggle demo purposes, running locally is fine.

---

## Project File Structure
```
flood_agent/
├── agent.py            ← Main AI agent (brain)
├── dashboard.py        ← Web dashboard
├── setup_contacts.py   ← One-time contact setup
├── firebase_key.json   ← Your Firebase key (keep secret!)
├── .env                ← Your API keys (keep secret!)
├── requirements.txt    ← Python packages
└── logs/
    └── agent.log       ← Agent activity log
```

---

## How the Agent Loop Works
```
Every 1 hour:
  1. Fetch water levels (simulated sensors / BWDB)
  2. Fetch rainfall forecast (OpenWeather API)
  3. Send data to Gemini AI → get risk levels + Bangla SMS
  4. Save everything to Firebase
  5. Send SMS to leaders in WARNING/DANGER districts
  6. Log results
```

