"""
Test file to verify all Module 3 API endpoints work correctly.
This tests the complaint creation, confirmation, listing, status updates, and ward stats.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("\n=== Testing /health ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ Health check passed")

def test_create_complaint_duplicate():
    """Test creating a complaint that matches an existing one (duplicate detection)"""
    print("\n=== Testing POST /api/complaints (Duplicate Detection) ===")
    
    # Try to create a complaint near the seeded pothole in Ward 1
    payload = {
        "category": "pothole",
        "description": "Another pothole very close to the seeded one",
        "lat": 19.1364,  # Same as C001
        "lng": 72.8296,  # Same as C001
        "ward_id": 1,
        "photo": "photo_duplicate.jpg"
    }
    
    response = requests.post(f"{BASE_URL}/api/complaints", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['result'] == 'possible_duplicate'
    assert 'complaint' in data
    print("✓ Duplicate detection passed - correctly identified existing complaint")

def test_create_complaint_far_away():
    """Test creating a complaint far away from existing ones (should create new)"""
    print("\n=== Testing POST /api/complaints (Far Away - Should Create) ===")
    
    payload = {
        "category": "pothole",
        "description": "Pothole at far away location",
        "lat": 19.20,  # Far from seeded coordinates
        "lng": 72.90,  # Far from seeded coordinates
        "ward_id": 1,
        "photo": "photo_faraway.jpg",
        "severity": "routine"
    }
    
    response = requests.post(f"{BASE_URL}/api/complaints", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 201
    data = response.json()
    assert data['result'] == 'created'
    assert 'complaint' in data
    complaint_id = data['complaint']['id']
    print(f"✓ New complaint created with ID: {complaint_id}")
    return complaint_id

def test_create_complaint_missing_photo():
    """Test that missing photo field returns error"""
    print("\n=== Testing POST /api/complaints (Missing Photo) ===")
    
    payload = {
        "category": "pothole",
        "description": "Pothole without photo",
        "lat": 19.15,
        "lng": 72.83,
        "ward_id": 1
        # photo is missing
    }
    
    response = requests.post(f"{BASE_URL}/api/complaints", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data
    print("✓ Correctly rejected request without photo field")

def test_create_complaint_empty_photo():
    """Test that empty photo value returns error"""
    print("\n=== Testing POST /api/complaints (Empty Photo) ===")
    
    payload = {
        "category": "pothole",
        "description": "Pothole with empty photo",
        "lat": 19.15,
        "lng": 72.83,
        "ward_id": 1,
        "photo": ""  # empty string
    }
    
    response = requests.post(f"{BASE_URL}/api/complaints", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data
    print("✓ Correctly rejected request with empty photo")

def test_confirm_complaint(complaint_id):
    """Test confirming/upvoting a complaint"""
    print(f"\n=== Testing POST /api/complaints/{complaint_id}/confirm ===")
    
    response = requests.post(f"{BASE_URL}/api/complaints/{complaint_id}/confirm")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    data = response.json()
    assert 'complaint' in data
    print(f"✓ Complaint confirmed - confirm_count: {data['complaint']['confirm_count']}")

def test_list_complaints():
    """Test listing all complaints with optional filters"""
    print("\n=== Testing GET /api/complaints ===")
    
    # Test without filters
    response = requests.get(f"{BASE_URL}/api/complaints")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total complaints: {data['total']}")
    print(f"Returned: {data['count']}")
    
    assert response.status_code == 200
    assert 'complaints' in data
    print("✓ List complaints (no filter) passed")
    
    # Test with filters
    print("\n--- Testing with filters ---")
    response = requests.get(f"{BASE_URL}/api/complaints?category=pothole&status=pending")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Filtered complaints: {data['count']}")
    
    assert response.status_code == 200
    print("✓ List complaints (with filters) passed")

def test_update_complaint_status(complaint_id):
    """Test updating complaint status"""
    print(f"\n=== Testing PATCH /api/complaints/{complaint_id}/status ===")
    
    payload = {
        "status": "in_progress",
        "note": "Work started on this pothole"
    }
    
    response = requests.patch(f"{BASE_URL}/api/complaints/{complaint_id}/status", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['complaint']['status'] == 'in_progress'
    print("✓ Status updated to in_progress")
    
    # Update to resolved
    payload = {
        "status": "resolved",
        "note": "Pothole has been fixed"
    }
    
    response = requests.patch(f"{BASE_URL}/api/complaints/{complaint_id}/status", json=payload)
    print(f"Status: {response.status_code}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['complaint']['status'] == 'resolved'
    print("✓ Status updated to resolved")

def test_ward_stats():
    """Test getting ward statistics"""
    print("\n=== Testing GET /api/wards/<id>/stats ===")
    
    response = requests.get(f"{BASE_URL}/api/wards/1/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    data = response.json()
    assert 'open_count' in data
    assert 'resolved_count' in data
    assert 'resolution_rate' in data
    assert 'avg_response_days' in data
    print("✓ Ward stats retrieved successfully")

if __name__ == '__main__':
    print("=" * 60)
    print("Module 3 - API Endpoint Tests")
    print("=" * 60)
    
    try:
        test_health()
        
        # Test photo validation
        test_create_complaint_missing_photo()
        test_create_complaint_empty_photo()
        
        # Test duplicate detection
        test_create_complaint_duplicate()
        
        # Test creating a new complaint
        new_complaint_id = test_create_complaint_far_away()
        
        # Test confirm
        test_confirm_complaint(new_complaint_id)
        
        # Test listing
        test_list_complaints()
        
        # Test status update
        test_update_complaint_status(new_complaint_id)
        
        # Test ward stats
        test_ward_stats()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
