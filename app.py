from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app) 

@app.route('/api/traffic', methods=['GET'])
def get_traffic_data():
    conn = sqlite3.connect('traffic.db')
    c = conn.cursor()
    c.execute('SELECT src_ip, dest_ip, domain, timestamp, flagged FROM traffic ORDER BY timestamp DESC LIMIT 100')
    data = c.fetchall()
    conn.close()
    return jsonify([{'src_ip': row[0], 'dest_ip': row[1], 'domain': row[2], 'timestamp': row[3], 'flagged': row[4]} for row in data])

@app.route('/api/allowed_websites', methods=['GET', 'POST', 'DELETE'])
def manage_allowed_websites():
    conn = sqlite3.connect('traffic.db')
    c = conn.cursor()
    if request.method == 'POST':
        domain = request.json.get('domain')
        c.execute('INSERT INTO allowed_websites (domain) VALUES (?)', (domain,))
    elif request.method == 'DELETE':
        domain = request.json.get('domain')
        c.execute('DELETE FROM allowed_websites WHERE domain = ?', (domain,))
    conn.commit()
    c.execute('SELECT domain FROM allowed_websites')
    data = c.fetchall()
    conn.close()
    return jsonify([row[0] for row in data])

@app.route('/api/blocked_websites', methods=['GET', 'POST', 'DELETE'])
def manage_blocked_websites():
    conn = sqlite3.connect('traffic.db')
    c = conn.cursor()
    if request.method == 'POST':
        domain = request.json.get('domain')
        c.execute('INSERT INTO blocked_websites (domain) VALUES (?)', (domain,))
    elif request.method == 'DELETE':
        domain = request.json.get('domain')
        c.execute('DELETE FROM blocked_websites WHERE domain = ?', (domain,))
    conn.commit()
    c.execute('SELECT domain FROM blocked_websites')
    data = c.fetchall()
    conn.close()
    return jsonify([row[0] for row in data])

if __name__ == '__main__':
    app.run(debug=True)
