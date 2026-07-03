"""
Bangladesh Flood Early Warning AI Agent
Uses: Gemini AI + OpenWeather API + Firebase + Twilio SMS
"""

import os
import json
import time
import requests
import sys
from datetime import datetime
from google import genai
from google.genai import types
import firebase_admin
from firebase_admin import credentials, db
from twilio.rest import Client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# ── Setup Gemini AI ──────────────────────────────────────────────────────────
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── Setup Firebase ───────────────────────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": os.getenv("FIREBASE_DB_URL")
    })

# ── Setup Twilio SMS ─────────────────────────────────────────────────────────
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# ── Simulated sensor stations (replace with real BWDB API later) ─────────────
STATIONS = [
    {"id": "sylhet_surma",    "name": "Surma River - Sylhet",    "district": "Sylhet",    "danger_level": 8.5},
    {"id": "sunamganj_surma", "name": "Surma River - Sunamganj", "district": "Sunamganj", "danger_level": 7.8},
    {"id": "netrokona_kng",   "name": "Kangsha River - Netrokona","district": "Netrokona","danger_level": 6.2},
    {"id": "jamalpur_brhm",   "name": "Brahmaputra - Jamalpur",  "district": "Jamalpur",  "danger_level": 9.1},
]

# Village leaders to alert (phone numbers from Firebase contacts)
def get_contacts():
    return db.reference("contacts").get() or {}


# ── STEP 1: Fetch Water Level Data ──────────────────────────────────────────
def fetch_water_levels():
    """
    In production: call BWDB (Bangladesh Water Development Board) API
    For demo: simulate realistic sensor readings
    """
    import random
    readings = []
    for station in STATIONS:
        # Simulate sensor - replace with: requests.get(BWDB_API_URL)
        level = round(station["danger_level"] + random.uniform(-1.5, 2.0), 2)
        readings.append({
            "station_id":    station["id"],
            "station_name":  station["name"],
            "district":      station["district"],
            "water_level_m": level,
            "danger_level":  station["danger_level"],
            "timestamp":     datetime.now().isoformat()
        })
    return readings


# ── STEP 2: Fetch Rainfall Forecast ─────────────────────────────────────────
def fetch_rainfall(district_name):
    """Calls OpenWeather API for rainfall forecast"""
    api_key = os.getenv("OPENWEATHER_API_KEY")

    # Map districts to coordinates
    coords = {
        "Sylhet":    (24.8949, 91.8687),
        "Sunamganj": (25.0658, 91.3950),
        "Netrokona": (24.8703, 90.7279),
        "Jamalpur":  (24.9376, 89.9407),
    }

    lat, lon = coords.get(district_name, (23.8103, 90.4125))

    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    )

    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        # Sum rainfall for next 24 hours (8 x 3-hour intervals)
        total_rain = sum(
            item.get("rain", {}).get("3h", 0)
            for item in data.get("list", [])[:8]
        )
        return round(total_rain, 1)
    except Exception as e:
        print(f"Weather API error for {district_name}: {e}")
        return 0.0


# ── STEP 3: AI Reasoning with Gemini ────────────────────────────────────────
def analyze_with_gemini(water_readings, rainfall_data):
    """
    Send all sensor + weather data to Gemini.
    Gemini reasons about flood risk and generates Bangla warnings.
    """

    data_summary = []
    for r in water_readings:
        rain = rainfall_data.get(r["district"], 0)
        pct  = round((r["water_level_m"] / r["danger_level"]) * 100, 1)
        data_summary.append(
            f"- {r['district']}: water={r['water_level_m']}m "
            f"(danger={r['danger_level']}m, {pct}%), "
            f"rain forecast={rain}mm"
        )

    prompt = f"""
You are a flood risk AI agent for Bangladesh. Analyze this real-time data:

{chr(10).join(data_summary)}

For EACH district, you must:
1. Classify risk: SAFE / WATCH / WARNING / DANGER
   - SAFE: water < 70% of danger level AND rain < 30mm
   - WATCH: water 70-85% OR rain 30-60mm
   - WARNING: water 85-95% OR rain 60-100mm
   - DANGER: water > 95% of danger level OR rain > 100mm

2. Estimate hours until flooding (if WARNING or DANGER)

3. Write a SHORT Bangla SMS alert (max 160 chars) for WARNING/DANGER districts only

Respond ONLY with valid JSON, no markdown:
{{
  "assessments": [
    {{
      "district": "...",
      "risk_level": "SAFE|WATCH|WARNING|DANGER",
      "water_pct": 85.2,
      "rainfall_mm": 45.0,
      "hours_to_flood": 18,
      "bangla_sms": "বাংলা বার্তা এখানে...",
      "action_needed": true
    }}
  ],
  "overall_summary": "One sentence English summary"
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    raw = response.text.strip()
    # Strip markdown code fences if present
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


# ── STEP 4: Save to Firebase ─────────────────────────────────────────────────
def save_to_firebase(water_readings, analysis):
    """Store readings + AI analysis in Firebase Realtime Database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save raw sensor data
    db.reference(f"sensor_readings/{timestamp}").set({
        "readings":  water_readings,
        "timestamp": datetime.now().isoformat()
    })

    # Save AI analysis results
    db.reference(f"alerts/{timestamp}").set({
        "analysis":  analysis,
        "timestamp": datetime.now().isoformat()
    })

    # Update latest status (dashboard reads this)
    db.reference("latest_status").set({
        "assessments": analysis["assessments"],
        "summary":     analysis["overall_summary"],
        "updated_at":  datetime.now().isoformat()
    })

    print(f"  Saved to Firebase: {timestamp}")


# ── STEP 5: Send SMS Alerts ───────────────────────────────────────────────────
def send_sms_alerts(analysis):
    """Send Bangla SMS to village leaders for WARNING/DANGER districts"""
    contacts = get_contacts()
    alerts_sent = 0

    for assessment in analysis["assessments"]:
        if not assessment.get("action_needed"):
            continue

        district  = assessment["district"]
        risk      = assessment["risk_level"]
        bangla_msg = assessment.get("bangla_sms", "")

        if not bangla_msg:
            continue

        # Find leaders registered for this district
        district_contacts = [
            c for c in contacts.values()
            if c.get("district") == district
        ]

        for contact in district_contacts:
            phone = contact.get("phone")
            name  = contact.get("name", "Leader")
            if not phone:
                continue

            # Log sent alert in Firebase first for the dashboard demo
            db.reference("sms_log").push({
                "to":        phone,
                "name":      name,
                "district":  district,
                "risk":      risk,
                "message":   bangla_msg,
                "sent_at":   datetime.now().isoformat()
            })

            try:
                twilio_client.messages.create(
                    body=bangla_msg,
                    from_=os.getenv("TWILIO_PHONE"),
                    to=phone
                )
                print(f"  SMS sent to {name} ({district}): {risk}")
                alerts_sent += 1
            except Exception as e:
                print(f"  SMS failed to {name}: {e}")

    return alerts_sent


# ── STEP 6: Log results ───────────────────────────────────────────────────────
def log_cycle(analysis, alerts_sent):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary   = analysis.get("overall_summary", "")

    danger_districts = [
        a["district"] for a in analysis["assessments"]
        if a["risk_level"] in ("WARNING", "DANGER")
    ]

    log_line = (
        f"[{timestamp}] {summary} | "
        f"High-risk: {danger_districts or 'None'} | "
        f"SMS sent: {alerts_sent}\n"
    )

    with open("logs/agent.log", "a", encoding="utf-8") as f:
        f.write(log_line)
    print(f"\n  LOG: {log_line.strip()}")


# ── MAIN AGENT LOOP ───────────────────────────────────────────────────────────
def run_agent_cycle():
    print(f"\n{'='*55}")
    print(f"  FLOOD AGENT CYCLE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    # Step 1: Collect water level data
    print("\n[1] Fetching water levels...")
    water_readings = fetch_water_levels()
    for r in water_readings:
        print(f"    {r['district']}: {r['water_level_m']}m (danger: {r['danger_level']}m)")

    # Step 2: Fetch rainfall for each district
    print("\n[2] Fetching rainfall forecasts...")
    rainfall_data = {}
    for r in water_readings:
        rain = fetch_rainfall(r["district"])
        rainfall_data[r["district"]] = rain
        print(f"    {r['district']}: {rain}mm expected")

    # Step 3: Gemini AI analysis
    print("\n[3] Gemini analyzing flood risk...")
    analysis = analyze_with_gemini(water_readings, rainfall_data)
    for a in analysis["assessments"]:
        flag = "🚨" if a["risk_level"] in ("WARNING","DANGER") else "✓"
        print(f"    {flag} {a['district']}: {a['risk_level']}")

    # Step 4: Save to Firebase
    print("\n[4] Saving to Firebase...")
    save_to_firebase(water_readings, analysis)

    # Step 5: Send SMS alerts
    print("\n[5] Sending SMS alerts...")
    alerts_sent = send_sms_alerts(analysis)
    print(f"    {alerts_sent} alerts sent")

    # Step 6: Log
    print("\n[6] Logging...")
    log_cycle(analysis, alerts_sent)

    print(f"\n  Cycle complete. Next run in 1 hour.\n")
    return analysis


if __name__ == "__main__":
    print("Bangladesh Flood Early Warning Agent starting...")
    while True:
        try:
            run_agent_cycle()
        except Exception as e:
            print(f"Agent error: {e}")
        time.sleep(3600)  # Run every 1 hour