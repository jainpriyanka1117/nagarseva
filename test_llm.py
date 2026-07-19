import requests
import json
import time

r = requests.post('http://localhost:5000/api/complaints',
    json={
        'description':'live wire hanging near school gate, sparking in the rain',
        'category':'pothole',
        'lat':31.5,
        'lng':31.5,
        'ward_id':1,
        'photo':'https://example.com/test.jpg'
    },
    timeout=10)
        'ward_id':1,
        'photo':'https://example.com/test.jpg'
    },
    timeout=10)

print(f'HTTP Status: {r.status_code}')
data = r.json()
complaint = data.get('complaint', {})
print(f'Saved category: {complaint.get("category")}')
print(f'Saved severity: {complaint.get("severity")}')
print(f'Saved authority_id: {complaint.get("authority_id")}')

# Look up authority name
import sqlite3
conn = sqlite3.connect('complaints.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM authority WHERE id = ?', (complaint.get("authority_id"),))
auth = cursor.fetchone()
if auth:
    print(f'Authority name: {auth[0]}')
conn.close()
