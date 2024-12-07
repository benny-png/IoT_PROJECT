# WebSocket Integration Guide for IoT Control System

## WebSocket Communication Protocol

### 1. Initial Connection
When your frontend first connects to the WebSocket, the backend immediately sends the current state:

```javascript
// Frontend: Establishing connection
const ws = new WebSocket(`ws://${API_URL}/ws`);

ws.onopen = function() {
    console.log('Connected to WebSocket');
    // Backend will automatically send current state
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // data format: { "status": "ON" } or { "status": "OFF" }
    updateUI(data.status);
};
```

### 2. Message Format
All WebSocket messages follow this JSON format:
```json
{
    "status": "ON" | "OFF"
}
```

### 3. Complete Frontend Implementation Example
```javascript
let ws;
const API_URL = 'your-backend-url';  // e.g., 'localhost:8000' or 'your-app.render.com'

function connectWebSocket() {
    // Determine WebSocket protocol
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${API_URL}/ws`);
    
    // Connection opened
    ws.onopen = function() {
        console.log('Connected to WebSocket');
        document.getElementById('connectionStatus').textContent = 'Connected';
    };
    
    // Listen for messages
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateUI(data.status);
    };
    
    // Connection closed
    ws.onclose = function() {
        console.log('Disconnected from WebSocket');
        document.getElementById('connectionStatus').textContent = 'Disconnected';
        // Optional: Implement reconnection logic
        setTimeout(connectWebSocket, 3000);
    };
    
    // Connection error
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        document.getElementById('connectionStatus').textContent = 'Error connecting';
    };
}

// Update UI based on received status
function updateUI(status) {
    document.getElementById('statusText').textContent = status;
    document.getElementById('indicator').className = `indicator ${status}`;
}

// Call this when page loads
connectWebSocket();
```

### 4. When Do You Receive Updates?
1. **Initial Connection**: Backend sends current state immediately
2. **SMS Received**: When someone sends "ON" or "OFF" via SMS
3. **API Control**: When device state changes through REST API endpoints
4. **Toggle**: When device is toggled through the toggle endpoint

### 5. Error Handling Best Practices
```javascript
function setupWebSocket() {
    try {
        connectWebSocket();
    } catch (error) {
        console.error('WebSocket setup failed:', error);
        // Implement your error UI update here
    }
}

// Reconnection logic
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function handleDisconnection() {
    if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        console.log(`Reconnecting... Attempt ${reconnectAttempts}`);
        setTimeout(connectWebSocket, 3000);
    } else {
        console.error('Max reconnection attempts reached');
        // Update UI to show permanent disconnection
    }
}
```

### 6. Testing WebSocket Connection
```javascript
// Add this to check if you're receiving updates
ws.onmessage = function(event) {
    console.log('Received:', event.data);  // See the raw message
    const data = JSON.parse(event.data);
    console.log('Parsed status:', data.status);  // See the parsed status
    updateUI(data.status);
};
```

### 7. Common Issues and Solutions

1. **Connection Failing**
   - Check if backend URL is correct
   - Verify WebSocket protocol matches (ws:// for HTTP, wss:// for HTTPS)
   - Ensure backend is running and accessible

2. **Not Receiving Updates**
   - Check browser console for errors
   - Verify onmessage handler is properly set up
   - Ensure JSON parsing is working

3. **State Not Syncing**
   - Check if updateUI function is being called
   - Verify DOM element IDs match your HTML
   - Console.log the received data for debugging

### 8. Quick Integration Checklist
- [ ] Set up WebSocket connection
- [ ] Implement message handler
- [ ] Add reconnection logic
- [ ] Set up error handling
- [ ] Test initial connection
- [ ] Verify state updates
- [ ] Implement UI updates

## Backend API Reference

### Endpoints

#### GET /state
Returns current device state
```json
{
    "status": "ON" | "OFF"
}
```

#### POST /control
Control device state
- Request body:
```json
{
    "status": "ON" | "OFF"
}
```
- Response:
```json
{
    "status": "success",
    "message": "Device has been turned ON/OFF",
    "current_state": {
        "status": "ON" | "OFF"
    }
}
```

#### POST /toggle
Toggle device state
- Response:
```json
{
    "status": "success",
    "message": "Device has been toggled to ON/OFF",
    "current_state": {
        "status": "ON" | "OFF"
    }
}
```

#### WebSocket /ws
- Connects to real-time updates
- Receives JSON messages:
```json
{
    "status": "ON" | "OFF"
}
```

### Error Handling
All endpoints return error responses in the format:
```json
{
    "status": "error",
    "message": "Error description"
}
```

## Development Setup

1. Local Testing:
```javascript
const API_URL = 'localhost:8000';
```

2. Production:
```javascript
const API_URL = 'your-app.onrender.com';
```

3. Update protocols for production:
```javascript
// WebSocket
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${wsProtocol}//${API_URL}/ws`;

// HTTP requests
const httpProtocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
const apiUrl = `${httpProtocol}//${API_URL}`;
```

## Common Issues

1. CORS Errors
- Make sure your backend has CORS properly configured
- Check the allowed origins in your backend configuration

2. WebSocket Connection Fails
- Verify the correct protocol (ws:// vs wss://)
- Check if your backend is running and accessible

3. State Updates Not Showing
- Ensure WebSocket connection is established
- Check browser console for errors

## Best Practices

1. Error Handling
```javascript
try {
    const response = await fetch(`http://${API_URL}/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
} catch (error) {
    console.error('Error:', error);
    // Handle error appropriately
}
```

2. WebSocket Reconnection
```javascript
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connect() {
    // ... WebSocket connection code ...
    
    ws.onclose = () => {
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            setTimeout(connect, 3000);
        }
    };
}
```

## Testing
1. Use browser Developer Tools (F12)
2. Check Network tab for API requests
3. Monitor Console for WebSocket messages and errors



## Africa's Talking SMS Webhook Integration

### SMS Callback Endpoint
Your FastAPI application exposes a webhook endpoint that Africa's Talking calls when an SMS is received:

example https://c2f3-197-250-226-222.ngrok-free.app/sms/callback

```python
@router.post("/sms/callback")
async def sms_callback(request: Request):
    form_data = await request.form()
    message = form_data.get("text", "").strip().upper()
    from_number = form_data.get("from", "")
```

### Webhook Setup
1. In your Africa's Talking dashboard:
   - Go to SMS > SMS Callback URL
   - Set callback URL to: `https://your-domain.com/sms/callback`
   - For local testing, use ngrok: `https://your-ngrok-url/sms/callback`

### Callback Data Format
Africa's Talking sends these parameters to your webhook:
```json
{
    "text": "ON",           // The SMS message content
    "from": "+254711XXXXX", // Sender's phone number
    "to": "12345",          // Your shortcode/phone number
    "id": "msg-id",         // Message ID
    "linkId": "link-id",    // Optional link ID
    "date": "2024-01-01"    // Message timestamp
}
```

### Complete Flow
1. User sends SMS "ON" or "OFF" to your AT number
2. Africa's Talking receives SMS and POSTs to your webhook
3. Your webhook:
   ```python
   if message in ["ON", "OFF"]:
       # Update state
       state["status"] = message
       
       # Send SMS confirmation
       response_message = f"Device has been turned {message}"
       sms.send(response_message, [from_number])
       
       # Broadcast to WebSocket clients
       await manager.broadcast(state)
   ```
4. Connected WebSocket clients receive update
5. User receives confirmation SMS

### Testing Webhook Locally
1. Install ngrok:
   ```bash
   npm install -g ngrok
   # or
   snap install ngrok
   ```

2. Start ngrok tunnel:
   ```bash
   ngrok http 8000
   ```

3. Update Africa's Talking callback URL with ngrok URL

### Webhook Security
1. Africa's Talking sends these headers:
   ```
   Content-Type: application/x-www-form-urlencoded
   Accept: application/json
   ```

2. Consider adding validation:
   ```python
   # Example validation
   @router.post("/sms/callback")
   async def sms_callback(request: Request):
       # Validate content type
       if request.headers.get("content-type") != "application/x-www-form-urlencoded":
           raise HTTPException(status_code=400, detail="Invalid content type")
           
       # Process SMS...
   ```

### Common Webhook Issues
1. **Callback URL Not Reachable**
   - Check your server is running
   - Verify URL is publicly accessible
   - Test using ngrok for local development

2. **Invalid Response Format**
   - Ensure you return valid JSON
   - Include required response fields

3. **Timeout Issues**
   - Process webhook quickly (under 30 seconds)
   - Use background tasks for long operations

4. **SMS Not Processing**
   - Check webhook logs for incoming requests
   - Verify message format parsing
   - Test state updates via WebSocket