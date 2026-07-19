import math

def haversine_distance(lat1, lng1, lat2, lng2):
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.
    """
    R = 6371000  # Earth's radius in meters
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c
    return distance

# Test the two coordinates
lat1, lng1 = 19.2, 72.9      # First complaint
lat2, lng2 = 19.25, 72.95    # New complaint

distance = haversine_distance(lat1, lng1, lat2, lng2)
print(f'Distance between ({lat1}, {lng1}) and ({lat2}, {lng2})')
print(f'Distance: {distance:.2f} meters')
print(f'Distance: {distance/1000:.2f} km')
print(f'\nThreshold for pothole: 15 meters')
print(f'Is duplicate? {distance <= 15}')
