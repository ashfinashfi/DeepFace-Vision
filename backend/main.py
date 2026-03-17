import base64
import cv2
import numpy as np
import asyncio
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from analyzer import analyze_frame

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_base64_frame(data: str) -> str:
    try:
        # Split header if present, e.g. "data:image/jpeg;base64,....."
        if ',' in data:
            data = data.split(',')[1]
            
        img_bytes = base64.b64decode(data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return ""
            
        # Analyze frame
        processed_frame = analyze_frame(frame)
        
        # Encode back to base64
        _, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        b64_str = base64.b64encode(buffer).decode('utf-8')
        
        return "data:image/jpeg;base64," + b64_str
    except Exception as e:
        print(f"Frame processing error: {e}")
        return ""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to WS")
    try:
        while True:
            # We use text mode to send base64 back and forth easily with JS
            data = await websocket.receive_text()
            
            # Run the heavy deepface inference in a threadpool so we don't block the async event loop
            processed_data = await asyncio.to_thread(process_base64_frame, data)
            
            if processed_data:
                await websocket.send_text(processed_data)
                
    except WebSocketDisconnect:
        print("Client disconnected from WS")
    except Exception as e:
        print(f"WebSocket error: {e}")

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

@app.get("/")
async def get_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
