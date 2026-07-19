import math

def haversine_distance(lat1, lng1, lat2, lng2):
    """Calculate distance in meters"""
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

# Ward 1 pothole coordinates from seed data
ward1_potholes = [
    (19.1364, 72.8296),  # C001
    (19.1367, 72.8300),  # C002
]

# Test coordinates
test_coords = (19.20, 72.90)

print(f"Testing duplicate detection with test coordinates: {test_coords}\n")

for idx, (lat, lng) in enumerate(ward1_potholes, 1):
    distance = haversine_distance(lat, lng, test_coords[0], test_coords[1])
    print(f"Ward 1 Pothole {idx}: ({lat}, {lng})")
    print(f"  Distance to test coords: {distance:.2f} meters ({distance/1000:.3f} km)")
    print(f"  Within 15m threshold? {distance <= 15}\n")

# Also check all Ward 1 complaints
ward1_complaints = [
    (19.1364, 72.8296, "pothole C001"),
    (19.1367, 72.8300, "pothole C002"),
    (19.1189, 72.8468, "streetlight C003"),
    (19.1195, 72.8475, "exposed_wire C004"),
    (19.1400, 72.8350, "streetlight C014"),
    (19.1150, 72.8440, "waterlogging C016"),
    (19.1300, 72.8250, "road_damage C018"),
]

print(f"\n{'='*60}")
print("All Ward 1 Complaints:")
print(f"{'='*60}\n")

for lat, lng, desc in ward1_complaints:
    distance = haversine_distance(lat, lng, test_coords[0], test_coords[1])
    print(f"{desc}: ({lat}, {lng})")
    print(f"  Distance to test coords: {distance:.2f} meters ({distance/1000:.3f} km)")
