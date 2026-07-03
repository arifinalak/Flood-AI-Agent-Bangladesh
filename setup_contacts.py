"""
Run this ONCE to add village leader contacts to Firebase.
Add real phone numbers here before running.
"""

import os
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv

load_dotenv()

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": os.getenv("FIREBASE_DB_URL")
    })

# Add your real contacts here
contacts = [
    {
        "name":     "Altaf Mahabub",
        "phone":    "+88017xxxxxxxx",   # Replace with real number
        "district": "Sylhet",
        "role":     "Union Parishad Chairman"
    },
    {
        "name":     "Rohim Ali",
        "phone":    "+88013xxxxxxxx",   # Replace with real number
        "district": "Sunamganj",
        "role":     "Village Leader"
    },
    {
        "name":     "Rokon Mia",
        "phone":    "+88019xxxxxxxx",   # Replace with real number
        "district": "Netrokona",
        "role":     "DDMC Officer"
    },
    {
        "name":     "Ali hossain dewan",
        "phone":    "+88018xxxxxxxx",   # Replace with real number
        "district": "Jamalpur",
        "role":     "Union Parishad Member"
    },
]

ref = db.reference("contacts")
for contact in contacts:
    ref.push(contact)
    print(f"Added: {contact['name']} ({contact['district']})")

print("\nAll contacts added to Firebase!")
