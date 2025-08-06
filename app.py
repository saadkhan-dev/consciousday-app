import streamlit as st
import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os

# ---------- Load API Key ----------
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

# ---------- Form ----------
with st.form("journal_form"):
    dream = st.text_area("🌙 What's your dream?")
    intention = st.text_area("💭 What's your intention for today?")
    priorities = st.text_area("✅ Top 3 priorities today?")
    submitted = st.form_submit_button("Submit")

# ---------- AI Response Generation ----------
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
        st.warning("⚠ Please fill in all fields before submitting.")

# ---------- View Journal Entries ----------
with st.expander("📖 View My Past Entries"):
    if st.button("Show Entries"):
        conn = sqlite3.connect("journal.db")
        cursor = conn.cursor()
        cursor.execute("SELECT date, dream, intention, priorities, reflection, strategy FROM journal_entries ORDER BY date DESC")
        entries = cursor.fetchall()
        conn.close()

        if entries:
            for entry in entries:
                st.markdown("---")
                st.markdown(f"**🗓 Date:** {entry[0]}")
                st.markdown(f"**🌙 Dream:** {entry[1]}")
                st.markdown(f"**💭 Intention:** {entry[2]}")
                st.markdown(f"**✅ Priorities:** {entry[3]}")
                st.markdown(f"**🔍 Reflection:** {entry[4]}")
                st.markdown(f"**📌 Strategy:** {entry[5]}")
        else:
            st.info("No journal entries found.")
