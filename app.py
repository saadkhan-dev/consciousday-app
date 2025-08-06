import streamlit as st
import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")


# ---------- Save Journal Entry to SQLite ----------
def save_entry(dream, intention, priorities, reflection, strategy):
    conn = sqlite3.connect("journal.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            dream TEXT,
            intention TEXT,
            priorities TEXT,
            reflection TEXT,
            strategy TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO journal_entries (date, dream, intention, priorities, reflection, strategy)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        dream,
        intention,
        priorities,
        reflection,
        strategy
    ))

    conn.commit()
    conn.close()


# ---------- Streamlit UI ----------
st.set_page_config(page_title="ConsciousDay Journal", page_icon="🧠")
st.title("🧠 ConsciousDay - AI Journal")
st.write("Welcome! Let's set your mindset for the day.")

with st.form("journal_form"):
    dream = st.text_area("🌙 What's your dream?")
    intention = st.text_area("💭 What's your intention for today?")
    priorities = st.text_area("✅ Top 3 priorities today?")
    submitted = st.form_submit_button("Submit")

if submitted:
    if dream and intention and priorities:
        st.success("Journal submitted! Generating AI response...")

        prompt = f"""
        Today’s Journal Entry:
        - Dream: {dream}
        - Intention: {intention}
        - Priorities: {priorities}

        Give me:
        1. A brief reflection on this mindset.
        2. A simple strategy to stay focused today.
        """

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            st.subheader("🤖 AI Response:")
            st.write(reply)

            # Save in database
            try:
                reflection = reply.split("2.")[0].strip()
                strategy = reply.split("2.")[1].strip()
                save_entry(dream, intention, priorities, reflection, strategy)
                st.success("✅ Your journal has been saved successfully!")
            except:
                st.warning("⚠ Could not split AI response correctly. Please check format.")

        else:
            st.error("❌ Failed to get AI response.")
            st.code(response.text)

    else:
        st.warning("Please fill in all fields before submitting.")