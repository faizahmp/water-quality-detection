# line_notifier.py
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
USER_ID = os.getenv("USER_ID")

def push_message(message_text):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}',
    }
    payload = {
        'to': USER_ID,
        'messages': [
            {'type': 'text', 'text': message_text}
        ]
    }
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    print("📤 LINE:", res.status_code, res.text)