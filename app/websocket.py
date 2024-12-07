from fastapi import APIRouter, WebSocket, Request, HTTPException
from typing import List, Dict
import africastalking
from app.config import settings
from pydantic import BaseModel

router = APIRouter()

# Initialize Africa's Talking
africastalking.initialize(
    username=settings.AT_USERNAME,
    api_key=settings.AT_API_KEY
)
sms = africastalking.SMS

# Pydantic model for state change requests
class StateChange(BaseModel):
    status: str

# Store state and active connections
state = {"status": "OFF"}
active_connections: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json(state)
        while True:
            data = await websocket.receive_text()
    except:
        manager.disconnect(websocket)

@router.post("/sms/callback")
async def sms_callback(request: Request):
    form_data = await request.form()
    message = form_data.get("text", "").strip().upper()
    from_number = form_data.get("from", "")
    
    if message in ["ON", "OFF"]:
        state["status"] = message
        response_message = f"Device has been turned {message}"
        await manager.broadcast(state)
    else:
        response_message = "Invalid command. Please send either 'ON' or 'OFF'"
    
    try:
        sms.send(response_message, [from_number])
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
    
    return {"status": "success", "message": response_message}

# New routes for manual control
@router.get("/state")
async def get_state() -> Dict:
    """Get current device state"""
    return state

@router.post("/control")
async def control_device(state_change: StateChange):
    """Manually control device state"""
    if state_change.status not in ["ON", "OFF"]:
        raise HTTPException(status_code=400, detail="Status must be 'ON' or 'OFF'")
    
    state["status"] = state_change.status
    await manager.broadcast(state)
    
    return {
        "status": "success",
        "message": f"Device has been turned {state_change.status}",
        "current_state": state
    }

# Optional: Add route to toggle state
@router.post("/toggle")
async def toggle_device():
    """Toggle device state between ON and OFF"""
    new_status = "ON" if state["status"] == "OFF" else "OFF"
    state["status"] = new_status
    await manager.broadcast(state)
    
    return {
        "status": "success",
        "message": f"Device has been toggled to {new_status}",
        "current_state": state
    }