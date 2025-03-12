import requests
import json

def test_tokenizer_api():
    url = "http://localhost:8000/tokenize"
    
    payload = {
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "text": [
            "here is sentence 1",
            "this is another example",
            "FastAPI microservices are powerful"
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_tokenizer_api()