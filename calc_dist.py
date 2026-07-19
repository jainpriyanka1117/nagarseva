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

print('=== Distance Calculations ===\n')

# Seeded potholes in Ward 1
print('Seeded potholes in Ward 1:')
print('  C001: (19.1364, 72.8296)')
print('  C002: (19.1367, 72.83)')
print('\nTest coordinates in original TEST 2: (19.20, 72.90)')
print('Test coordinates in retry: (19.25, 72.95)\n')

coord1 = (19.1364, 72.8296)
coord2_orig = (19.20, 72.90)
coord2_retry = (19.25, 72.95)

dist1 = haversine_distance(coord1[0], coord1[1], coord2_orig[0], coord2_orig[1])
dist2 = haversine_distance(coord1[0], coord1[1], coord2_retry[0], coord2_retry[1])

print(f'Distance C001 to Original TEST 2 (19.20, 72.90): {dist1:.2f}m ({dist1/1000:.2f}km)')
print(f'Distance C001 to Retry (19.25, 72.95): {dist2:.2f}m ({dist2/1000:.2f}km)')
print(f'\nPothole duplicate threshold: 15 meters')
print(f'Original TEST 2 is duplicate of C001? {dist1 <= 15}')
print(f'Retry is duplicate of C001? {dist2 <= 15}')
