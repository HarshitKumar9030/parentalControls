from scapy.all import sniff, conf, IP, TCP, DNS, DNSRR, DNSQR, sr1
from datetime import datetime
import sqlite3
import time
import socket

conn = sqlite3.connect('traffic.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS traffic (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        src_ip TEXT,
        dest_ip TEXT,
        domain TEXT,
        timestamp TEXT,
        flagged INTEGER DEFAULT 0
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS allowed_websites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS blocked_websites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT
    )
''')
conn.commit()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Exception in get_local_ip: {e}")
        return None

local_ip = get_local_ip()
if not local_ip:
    print("Could not determine local IP address. Exiting...")
    exit(1)

monitored_ips = {local_ip, '192.168.137.130', '192.168.137.131', '152.59.89.93', '192.168.0.1'}

def get_blocked_domains():
    c.execute('SELECT domain FROM blocked_websites')
    return {row[0] for row in c.fetchall()}

def get_allowed_domains():
    c.execute('SELECT domain FROM allowed_websites')
    return {row[0] for row in c.fetchall()}

def get_domain(ip):
    try:
        # Reverse DNS lookup
        domain = socket.gethostbyaddr(ip)[0]
        print(f"Resolved domain for {ip}: {domain}")
        return domain
    except (socket.herror, socket.gaierror):
        print(f"Could not resolve domain for {ip}")
        return ''

def packet_callback(packet):
    try:
        if packet.haslayer(IP):
            src_ip = packet[IP].src
            dest_ip = packet[IP].dst

            if (src_ip in monitored_ips or dest_ip in monitored_ips) and (packet.haslayer(TCP) and (packet[TCP].dport == 80 or packet[TCP].dport == 443)):
                domain = get_domain(dest_ip)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                flagged = 0
                blocked_domains = get_blocked_domains()
                allowed_domains = get_allowed_domains()
                if any(bd in domain for bd in blocked_domains):
                    flagged = 1
                elif domain not in allowed_domains:
                    flagged = 2

                c.execute('INSERT INTO traffic (src_ip, dest_ip, domain, timestamp, flagged) VALUES (?, ?, ?, ?, ?)', (src_ip, dest_ip, domain, timestamp, flagged))
                conn.commit()

                print(f'Logged: {src_ip} -> {dest_ip} ({domain}) at {timestamp} {"[FLAGGED - Blocked]" if flagged == 1 else ("[FLAGGED - Not Allowed]" if flagged == 2 else "")}')
                time.sleep(1)
    except Exception as e:
        print(f"Exception in packet_callback: {e}")

conf.filter = "ip and (tcp port 80 or tcp port 443)"

while True:
    try:
        sniff(prn=packet_callback, store=0)
    except KeyboardInterrupt:
        break

print("Exiting...")

conn.close()
