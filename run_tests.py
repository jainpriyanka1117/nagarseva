import requests
import json
import time

time.sleep(3)

print('=== TEST 1: Duplicate pothole ===')
try:
    r = requests.post('http://localhost:5000/api/complaints', 
        json={'category':'pothole','description':'test near Andheri station','lat':19.1365,'lng':72.8298,'ward_id':1,'photo':'https://example.com/test1.jpg'},
        timeout=5)
    print(f'Status: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')
    result1 = 'PASS' if r.status_code == 200 and r.json().get('result') == 'possible_duplicate' else 'FAIL'
    print(f'RESULT: {result1}')
except Exception as e:
    print(f'ERROR: {e}')
    result1 = 'FAIL'

print('\n=== TEST 2: Far away pothole (new) ===')
try:
    r = requests.post('http://localhost:5000/api/complaints',
        json={'category':'pothole','description':'far off test','lat':19.20,'lng':72.90,'ward_id':1,'photo':'https://example.com/test2.jpg'},
        timeout=5)
    print(f'Status: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')
    result2 = 'PASS' if r.status_code == 201 and r.json().get('result') == 'created' else 'FAIL'
    print(f'RESULT: {result2}')
except Exception as e:
    print(f'ERROR: {e}')
    result2 = 'FAIL'

print('\n=== TEST 3: List potholes ===')
try:
    r = requests.get('http://localhost:5000/api/complaints?category=pothole', timeout=5)
    print(f'Status: {r.status_code}')
    data = r.json()
    print(f'Total: {data["total"]}, Count: {data["count"]}')
    print(f'Complaints returned: {len(data["complaints"])}')
    result3 = 'PASS' if r.status_code == 200 and len(data['complaints']) > 0 else 'FAIL'
    print(f'RESULT: {result3}')
except Exception as e:
    print(f'ERROR: {e}')
    result3 = 'FAIL'

print('\n=== TEST 4: Health check ===')
try:
    r = requests.get('http://localhost:5000/health', timeout=5)
    print(f'Status: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')
    result4 = 'PASS' if r.status_code == 200 and r.json().get('status') == 'ok' else 'FAIL'
    print(f'RESULT: {result4}')
except Exception as e:
    print(f'ERROR: {e}')
    result4 = 'FAIL'

print('\n' + '='*60)
print(f'TEST 1 (Duplicate): {result1}')
print(f'TEST 2 (Create new): {result2}')
print(f'TEST 3 (List): {result3}')
print(f'TEST 4 (Health): {result4}')
print('='*60)
