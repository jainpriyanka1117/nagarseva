import requests
import json
import time

time.sleep(2)

print('=== TEST 2 (RETRY): Far away pothole with fresh coordinates ===')
try:
    r = requests.post('http://localhost:5000/api/complaints',
        json={'category':'pothole','description':'far off test v2','lat':19.25,'lng':72.95,'ward_id':1,'photo':'https://example.com/test2b.jpg'},
        timeout=5)
    print(f'Status: {r.status_code}')
    print(f'Response: {json.dumps(r.json(), indent=2)}')
    
    if r.status_code == 201 and r.json().get('result') == 'created':
        print('\nRESULT: PASS')
    else:
        print(f'\nRESULT: FAIL')
        print(f'  Expected: HTTP 201 with "result": "created"')
        print(f'  Got: HTTP {r.status_code} with "result": "{r.json().get("result")}"')
except Exception as e:
    print(f'ERROR: {e}')
    print('RESULT: FAIL')
