import sqlite3

conn = sqlite3.connect('complaints.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, category, lat, lng, description, ward_id, status
    FROM complaint
    WHERE category = 'pothole'
    AND ward_id = 1
    ORDER BY id DESC
""")

results = cursor.fetchall()
print(f'Found {len(results)} pothole complaints in Ward 1:\n')
for row in results:
    print(f'ID: {row[0]}')
    print(f'  Category: {row[1]}')
    print(f'  Lat/Lng: {row[2]}, {row[3]}')
    print(f'  Description: {row[4]}')
    print(f'  Status: {row[6]}')
    print()

conn.close()
