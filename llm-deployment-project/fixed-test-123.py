import requests
import json

def test_fixed():
    print("🧪 Testing Fixed Deployment...")
    
    payload = {
        "email": "student@example.com",
        "secret": "sw11234dfrt675wwq",  # ← USE YOUR SECRET
        "task": "fixed-test-123",
        "round": 1,
        "nonce": "fixed-test-123",
        "brief": "Create a simple sales summary page with seed=test123",
        "checks": ["Repo has MIT license", "README.md exists"],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": [{
            "name": "data.csv",
            "url": "data:text/csv;base64,cHJvZHVjdCxzYWxlcwpBLCwxMDAKQiwxNTAKQyw3NQ=="
        }]
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/deploy",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"✅ Status: {response.status_code}")
        print(f"📨 Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n🎉 SUCCESS! Check your app logs for deployment progress.")
            print("📋 Check your GitHub account for the new repository.")
        else:
            print(f"\n❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_fixed()