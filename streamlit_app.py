import streamlit as st
from openai import OpenAI
from datetime import datetime
import json
import os
# Initialize the OpenAI client securely
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Custom Instructions for Chatbot ---
SYSTEM_PROMPT = """

You are an AI customer service agent. Your goal is to offer Internet support.

First, introduce yourself pro-actively: “Hello. I’m a bot assistant Jerry.  Please provide your Prolific ID below:

Wait for the user to provide a prolific id.


Next ask the user: How can I assist you with your Internet issue today?”. Wait for a response form the user.


Next, if the user inquires about the WiFi trouble shooting/ slow WiFi, then ask the following clarification question:

Is the issue happening on one device or multiple devices?
•	Only one device (e.g., just my laptop or phone)
•	Multiple devices (e.g., laptop, phone, and TV)


Wait for a user to respond. Then reply with WiFi troubleshooting instructions below:

“Troubleshooting Wireless WiFi Connectivity (Home Network / Laptop or Desktop)
Use this when a user is trying to connect a laptop, desktop, or smart device to their home WiFi network and it's not working.

Restart the router and modem
o	Unplug both for 30 seconds, then plug them back in.
o	Wait 2–3 minutes for full reboot.
Forget the network and reconnect
o	Go to your device's WiFi settings, click the network name, and choose “Forget”
o	Then reconnect and re-enter the password.
Check router lights
o	Make sure Power, Internet, and WiFi lights are steady.
o	A blinking or red light may indicate an ISP issue.
”


After you provide the instructions, thank the user and express hope that the answer was helpful
 Complete the interaction with the phrase below:
Thank you for reaching out. I hope this information was helpful.

 ***Please proceed back to the survey to complete all questions about your experience:***
 : https://asu.co1.qualtrics.com/jfe/preview/previewId/62fdf4cc-a69f-4255-a321-4d795485d826/SV_3rutUOKtHWkQaA6?Q_CHL=preview&Q_SurveyVersionID=current

If at any point, user asks questions non-related to the modem troubleshooting, then reply: "I am sorry. I was only trained to handle Internet connectivity issues. Please contact Reihane Boghrati if you have any additional inquires unrelated to the WiFi troubleshooting."

"""

# --- Page Config ---
st.set_page_config(page_title="Wireless Support Bot", page_icon="💬")
st.title("📶 Wireless Support Bot")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# --- Chat Bubble Styling ---
USER_STYLE = "background-color:#DCF8C6;padding:8px;border-radius:10px;margin:5px 0;"
BOT_STYLE = "background-color:#F1F0F0;padding:8px;border-radius:10px;margin:5px 0;"

# --- Display Chat History (excluding system prompt) ---
for msg in st.session_state.messages[1:]:
    role = msg["role"]
    content = msg["content"]

    if role == "user":
        st.markdown(f"<div style='{USER_STYLE}'><strong>You:</strong> {content}</div>", unsafe_allow_html=True)
    elif role == "assistant":
        st.markdown(f"<div style='{BOT_STYLE}'><strong>Assistant:</strong> {content}</div>", unsafe_allow_html=True)

# --- User Input Form (auto-clearing) ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get assistant response
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages
    )
    reply = response.choices[0].message.content

    # Add assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Trigger rerun to show updated chat
    st.rerun()

# --- Save transcript locally (for researcher use only) ---
conversation_json = json.dumps(st.session_state.messages[1:], indent=2)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"chat_transcript_{timestamp}.json"
output_dir = "transcripts"
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
    f.write(conversation_json)
