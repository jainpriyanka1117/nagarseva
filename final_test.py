import sqlite3, requests, json
conn = sqlite3.connect('complaints.db')
cursor = conn.cursor()
cursor.execute('SELECT id, lat, lng FROM complaint ORDER BY id')
rows = cursor.fetchall()
print(f'All {len(rows)} complaints:')
for r in rows:
    print(f'ID {r[0]}: ({r[1]}, {r[2]})')
conn.close()

print('\n=== POST /api/complaints (lat 30.0, lng 30.0) ===')
r = requests.post('http://localhost:5000/api/complaints',
    json={'category':'pothole','description':'final clean test','lat':30.0,'lng':30.0,'ward_id':1,'photo':'https://example.com/final.jpg'},
    timeout=5)
print(f'HTTP Status: {r.status_code}')
print(f'Result: {r.json().get("result")}')
