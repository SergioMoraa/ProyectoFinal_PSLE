# webui.py
from flask import Flask, jsonify, request
import sqlite3, os, time
from hosts_store import load_blacklist
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'logs.db')
app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

@app.route('/stats')
def stats():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM blocked_events')
    total = c.fetchone()[0] if c.fetchone() is not None else 0
    # simple last 10
    c.execute('SELECT timestamp, client_ip, qname FROM blocked_events ORDER BY timestamp DESC LIMIT 20')
    rows = c.fetchall()
    conn.close()
    return jsonify({
        "total_blocks": total,
        "last": [{"time": r[0], "client": r[1], "domain": r[2]} for r in rows]
    })

@app.route('/blacklist')
def bl():
    s = list(load_blacklist())
    return jsonify({"count": len(s), "sample": s[:20]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
