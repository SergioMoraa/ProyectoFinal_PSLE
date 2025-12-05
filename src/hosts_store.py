# hosts_store.py
import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'logs.db')
HOSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'hosts')

def ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS blocked_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            client_ip TEXT,
            qname TEXT,
            qtype TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_block(client_ip, qname, qtype='A'):
    ensure_db()
    ts = int(time.time())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO blocked_events (timestamp, client_ip, qname, qtype) VALUES (?,?,?,?)',
              (ts, client_ip, qname, qtype))
    conn.commit()
    conn.close()

def load_blacklist():
    # returns a set of domains (lowercase, no protocol)
    s = set()
    os.makedirs(HOSTS_DIR, exist_ok=True)
    for fname in os.listdir(HOSTS_DIR):
        if not fname.endswith('.txt'):
            continue
        with open(os.path.join(HOSTS_DIR, fname), 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith('#'):
                    continue
                # lines like "0.0.0.0 example.com" or just "example.com"
                parts = line.split()
                domain = parts[-1].lower()
                if domain:
                    s.add(domain)
    return s
