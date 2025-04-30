import requests
import json

def test_tokenizer_api():
    url = "http://localhost:8000/tokenize"
    
    payload = {
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "huggingface_api_key": null,
        "max_chunk_length": 128,
        "max_tokens_per_chunk": 5,
        "token_overlap": 2,
        "texts": [
            "this is a very simple sentence",
            "hello, how's your day going today?",
            "The quick brown fox jumped quietly over the lazy dog sitting under the tree"
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