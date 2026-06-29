import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001/api/v1/ai"

endpoints = [
    {
        "method": "GET",
        "url": f"{BASE_URL}/executive-summary",
        "payload": None
    },
    {
        "method": "GET",
        "url": f"{BASE_URL}/analytics-insights",
        "payload": None
    },
    {
        "method": "POST",
        "url": f"{BASE_URL}/analyze-feedback",
        "payload": {
            "title": "Charger won't start",
            "category": "Hardware",
            "description": "The screen is completely blank on charger 3."
        }
    },
    {
        "method": "POST",
        "url": f"{BASE_URL}/analyze-complaint",
        "payload": {
            "title": "App crashed during payment",
            "priority": "High",
            "status": "Open",
            "description": "I tried to pay but the app closed and charged me anyway."
        }
    },
    {
        "method": "POST",
        "url": f"{BASE_URL}/generate-report",
        "payload": {
            "report_type": "Weekly Performance",
            "focus_areas": ["Revenue", "Hardware Issues"]
        }
    },
    {
        "method": "POST",
        "url": f"{BASE_URL}/chat",
        "payload": {
            "messages": [
                {"role": "user", "content": "What is the status of our chargers?"}
            ]
        }
    }
]

def run_tests():
    all_success = True
    results = []

    for ep in endpoints:
        print(f"\nTesting {ep['method']} {ep['url']}")
        try:
            if ep["method"] == "GET":
                response = requests.get(ep["url"])
            else:
                response = requests.post(ep["url"], json=ep["payload"])
            
            status = response.status_code
            print(f"Status: {status}")
            
            try:
                data = response.json()
                sample = json.dumps(data, indent=2)
                # Truncate sample if too long
                if len(sample) > 500:
                    sample = sample[:500] + "...\n}"
                print(f"Response snippet:\n{sample}")
            except Exception as e:
                print(f"Failed to parse JSON: {response.text}")
                data = None
                
            if status != 200:
                all_success = False
                
            results.append({
                "url": ep["url"],
                "status": status,
                "data": data
            })
            
        except Exception as e:
            print(f"Request failed: {e}")
            all_success = False

    return all_success

if __name__ == "__main__":
    time.sleep(2)  # Wait for server to be fully ready
    success = run_tests()
    if success:
        print("\nALL ENDPOINTS SUCCEEDED!")
    else:
        print("\nSOME ENDPOINTS FAILED!")
