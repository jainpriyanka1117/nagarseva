import sqlite3
import math

def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371000
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    return distance

conn = sqlite3.connect('complaints.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, category, lat, lng, description, ward_id, status, reported_at
    FROM complaint
    WHERE category = 'pothole'
    AND ward_id = 1
    ORDER BY id DESC
""")

results = cursor.fetchall()
print('=== All pothole complaints in Ward 1 ===\n')
for row in results:
    print(f'ID: {row[0]} | Lat: {row[2]}, Lng: {row[3]} | Status: {row[6]}')
    print(f'  Description: {row[4]}')
    print(f'  Reported: {row[7]}')
    print()

print('\n=== Testing duplicate detection logic ===\n')
lat_new, lng_new = 19.25, 72.95
radius_meters = 15

for row in results:
    if row[6] in ['pending', 'in_progress']:
        distance = haversine_distance(lat_new, lng_new, row[2], row[3])
        is_dup = distance <= radius_meters
        print(f'ID {row[0]} ({row[2]}, {row[3]}): {distance:.2f}m - Duplicate? {is_dup}')

conn.close()
