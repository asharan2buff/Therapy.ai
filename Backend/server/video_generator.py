import os
import time
import requests
from dotenv import load_dotenv
from fastapi import HTTPException


load_dotenv()
DID_API_KEY = os.getenv("DID_API_KEY")
API_USERNAME, API_PASSWORD = DID_API_KEY.split(":", 1)
BASE_URL = "https://api.d-id.com/talks"
def generate_video(text: str) -> str:
    payload = {
        "source_url": "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg",
        "script": {
            "type": "text",
            "provider": {"type": "microsoft", "voice_id": "Sara"},
            "input": text
        },
        "config": {"fluent": False, "stitch": True}
    }

    response = requests.post(
        BASE_URL,
        json=payload,
        auth=(API_USERNAME, API_PASSWORD)
    )

    if response.status_code != 201:
        raise HTTPException(500, f"D-ID API Error: {response.text}")

    talk_id = response.json()["id"]
    
    # Poll for completion
    for _ in range(30):  # 30 attempts with 2s delay = 1 minute timeout
        status_res = requests.get(
            f"{BASE_URL}/{talk_id}",
            auth=(API_USERNAME, API_PASSWORD)
        )
        
        if status_res.status_code != 200:
            raise HTTPException(500, f"Status check failed: {status_res.text}")

        data = status_res.json()
        status = data["status"]
        
        if status == "done":
            return data.get("result_url")
        elif status in ["error", "rejected"]:
            raise HTTPException(500, f"Video failed: {data.get('error')}")
        
        time.sleep(2)

    raise HTTPException(504, "Video generation timeout")