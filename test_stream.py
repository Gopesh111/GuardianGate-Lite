import requests
import sys

url = "http://127.0.0.1:8000/v1/chat/stream"
payload = {
    "user_id": "test_1",
    "prompt": "Explain Quantum Computing in 2 sentences."
}

print("Prompt sent. Waiting for stream...\n")
print("AI Response: ", end="", flush=True)

# stream=True is the magic here!
with requests.post(url, json=payload, stream=True) as r:
    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            print(chunk, end="", flush=True)
            
print("\n\n✅ Stream Finished!")