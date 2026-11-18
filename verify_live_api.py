import urllib.request
import json

base = 'http://127.0.0.1:8000'

# 1. Health check
with urllib.request.urlopen(f'{base}/api/v1/health') as r:
    data = json.loads(r.read().decode())
    print('1. Health API:', r.getcode(), data)

# 2. Registration
user_data = json.dumps({
    'email': 'student_live@careerpilot.edu',
    'username': 'lifestudent',
    'full_name': 'Live Student',
    'password': 'SecurePassword@123',
    'role': 'student'
}).encode('utf-8')

req = urllib.request.Request(f'{base}/api/v1/auth/register', data=user_data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as r:
        print('2. Registration successful:', r.getcode())
except Exception as e:
    print('2. Registration note:', e)

# 3. Login
login_data = json.dumps({
    'email': 'student_live@careerpilot.edu',
    'password': 'SecurePassword@123'
}).encode('utf-8')
req = urllib.request.Request(f'{base}/api/v1/auth/login', data=login_data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as r:
    res = json.loads(r.read().decode())
    token = res['access_token']
    print('3. Login successful, token acquired!')

# 4. Add Skills
skills_data = json.dumps([{
    'skill_name': 'Python',
    'proficiency_level': 5,
    'skill_type': 'technical',
    'years_experience': 3.0
}, {
    'skill_name': 'Machine Learning',
    'proficiency_level': 4,
    'skill_type': 'technical',
    'years_experience': 2.0
}]).encode('utf-8')

req = urllib.request.Request(f'{base}/api/v1/profile/skills', data=skills_data, headers={
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
})
with urllib.request.urlopen(req) as r:
    print('4. Skills added successfully:', r.getcode())

# 5. Add Interests
interests_data = json.dumps([{
    'category': 'Technology',
    'interest_name': 'Artificial Intelligence',
    'strength': 10
}]).encode('utf-8')
req = urllib.request.Request(f'{base}/api/v1/profile/interests', data=interests_data, headers={
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
})
with urllib.request.urlopen(req) as r:
    print('5. Interests added successfully:', r.getcode())

# 6. Profile Completion status
req = urllib.request.Request(f'{base}/api/v1/profile/completion', headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as r:
    comp = json.loads(r.read().decode())
    print(f'6. Profile completion status: {comp["percentage"]}% (Complete: {comp["is_complete"]})')

# 7. AI Recommendation Endpoint
req = urllib.request.Request(f'{base}/api/v1/recommendations', headers={
    'Authorization': f'Bearer {token}'
})
with urllib.request.urlopen(req) as r:
    recs = json.loads(r.read().decode())
    print(f'7. AI Career Recommendations Generated: {len(recs)} suggestions returned!')
    for i, rec in enumerate(recs[:3], 1):
        print(f'   #{i}: {rec["career_title"]} | Match Score: {rec["score"]}% | Confidence: {rec["confidence"]}')
        print(f'       Explanation: {rec.get("explanation")}')
