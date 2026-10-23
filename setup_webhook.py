"""Run locally after Render deploy: python setup_webhook.py"""
import os
import sys
import requests
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
secret = os.getenv('WEBHOOK_SECRET', '').strip()
base = os.getenv('RENDER_URL', '').strip().rstrip('/')
if not all([token, secret, base]) or not base.startswith('https://'):
    sys.exit('Set TELEGRAM_BOT_TOKEN, WEBHOOK_SECRET and RENDER_URL in local .env first.')
response = requests.post(f'https://api.telegram.org/bot{token}/setWebhook', json={
    'url': base + '/webhook', 'secret_token': secret,
    'allowed_updates': ['message', 'edited_message'], 'drop_pending_updates': True
}, timeout=25)
print('HTTP:', response.status_code)
try:
    result = response.json()
    print('Webhook set:', result.get('ok'), result.get('description', ''))
except ValueError:
    print('Telegram returned non-JSON response')
