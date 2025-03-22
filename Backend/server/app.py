from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import ollama  # Make sure to install: pip install ollama
from video_generator import generate_video  
from fastapi import HTTPException
import requests
import json
import datetime


# Firebase Config
with open("config.json", "r") as f:
    config = json.load(f)

DB_URL = config["dbUrl"]
NODE = config["node"]

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def save_to_firebase(user_id, user_message, bot_message):
    url = f"{DB_URL}/{NODE}/{user_id}.json"
    chat_data = {
        "user_message": user_message,
        "bot_message": bot_message,
        "timestamp": datetime.datetime.now().isoformat()  # Add timestamp
    }
    response = requests.post(url, json=chat_data)
    return response.json()

    
@app.post("/receive-data")
async def receive_data(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")  # Pass user ID from frontend
        user_message = data.get("text", "")
        print("Received data:", data)

        # Get Ollama response
        response = ollama.generate(
            model='mistral',
            prompt=data.get('text', '')
        )
        
        ollama_response = response['response']
        print("Ollama response:", ollama_response)

        # Generate video from Ollama response
        video_url = generate_video(ollama_response)  # Use your existing function

        # Save conversation to Firebase
        save_to_firebase(user_id, user_message, ollama_response)
        
        return {
            "status": "success",
            "text_response": ollama_response,
            "video_url": video_url  # Add this to response
        }
    
    
        
    except Exception as e:
        print("Error processing request:", str(e))
        return {"status": "error", "detail": str(e)}
    
# Add this new endpoint to fetch chat history
@app.get("/get-chats/{user_id}")
async def get_chats(user_id: str):
    try:
        url = f"{DB_URL}/{NODE}/{user_id}.json"
        response = requests.get(url)
        data = response.json()
        
        if not data:
            return {"chats": []}
            
        # Extract messages and filter by today
        today = datetime.datetime.now().date()
        chats = []
        for key, value in data.items():
            if 'timestamp' in value:
                msg_date = datetime.datetime.fromisoformat(value['timestamp']).date()
                if msg_date == today:
                    chats.append({
                        'user_message': value.get('user_message', ''),
                        'bot_message': value.get('bot_message', ''),
                        'time': value.get('timestamp', '')
                    })
        return {"chats": chats}
        
    except Exception as e:
        print("Error fetching chats:", str(e))
        return {"chats": []}

    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

