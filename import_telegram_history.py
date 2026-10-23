"""Telegram Desktop result.json -> Supabase PostgreSQL.

Run on your own computer after obtaining group consent. Never commit result.json.
Requires DATABASE_URL; run the bot once first to create the tables.
"""
import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv()

def plain_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ''.join(x if isinstance(x, str) else str(x.get('text', '')) for x in value if isinstance(x, (str, dict)))
    return ''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('export', type=Path)
    parser.add_argument('--chat-id', type=int, required=True)
    parser.add_argument('--days', type=int, default=365)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    data = json.loads(args.export.read_text(encoding='utf-8-sig'))
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    rows = []
    for msg in data.get('messages', []):
        if msg.get('type') != 'message' or not msg.get('from'):
            continue
        body = plain_text(msg.get('text')).strip()[:3000]
        if not body or body.startswith('/'):
            continue
        try:
            date = datetime.fromisoformat(msg['date'].replace('Z', '+00:00'))
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
        except (ValueError, KeyError, TypeError):
            continue
        if date < cutoff:
            continue
        from_id = str(msg.get('from_id') or '')
        if from_id.startswith('channel'):
            continue
        uid = int(from_id[4:]) if from_id.startswith('user') and from_id[4:].isdigit() else None
        rows.append((str(msg.get('id', '')), args.chat_id, uid, str(msg['from'])[:100], body, date.isoformat()))
    rows.sort(key=lambda r: (r[5], int(r[0]) if r[0].isdigit() else 0))
    print(f'Export: {data.get("name", "unknown")}; last {args.days} days: {len(rows)} text messages')
    if args.dry_run:
        return
    url = os.environ.get('DATABASE_URL', '').strip()
    if not url:
        raise SystemExit('DATABASE_URL yo‘q. Import bekor qilindi.')
    with psycopg.connect(url) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS imported_messages (
            chat_id BIGINT NOT NULL, source_message_id TEXT NOT NULL,
            PRIMARY KEY(chat_id, source_message_id))''')
        count = 0
        for source_id, chat_id, uid, name, body, date in rows:
            if not source_id:
                continue
            inserted = conn.execute('INSERT INTO imported_messages(chat_id,source_message_id) VALUES (%s,%s) ON CONFLICT DO NOTHING RETURNING source_message_id', (chat_id,source_id)).fetchone()
            if inserted:
                conn.execute('INSERT INTO messages(chat_id,user_id,name,text,created_at) VALUES (%s,%s,%s,%s,%s)', (chat_id,uid,name,body,date))
                count += 1
        print(f'Imported: {count}. Duplicates skipped: {len(rows)-count}.')

if __name__ == '__main__':
    main()
