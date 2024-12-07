# IoT Control System Integration Guide

This guide explains how to integrate with the IoT Control System, either by using the provided frontend interface or by building your own implementation.

## Frontend Integration

### Quick Start
1. Save the HTML file provided below
2. Update the `API_URL` constant to point to your backend
3. Open in any web browser

### HTML Template
```html
<!-- Save this as control-panel.html -->
<!DOCTYPE html>
<html>
<head>
    <title>IoT Control Panel</title>
    <!-- Your styles here -->
</head>
<body>
    <div class="container">
        <!-- Your HTML structure -->
    </div>

    <script>
        // 1. Configure your API URL
        const API_URL = 'localhost:8000'; // Change this to your backend URL

        // 2. WebSocket Connection
        let ws;
        function connectWebSocket() {
            ws = new WebSocket(`ws://${API_URL}/ws`);
            // Handle WebSocket events...
        }

        // 3. Device Control
        async function controlDevice(newStatus) {
            try {
                const response = await fetch(`http://${API_URL}/control`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await response.json();
                // Handle response...
            } catch (error) {
                console.error('Error:', error);
            }
        }
    </script>
</body>
</html>
```

### Configuration
- Development: Use `localhost:8000`
- Production: Use your deployed backend URL (e.g., `your-app.onrender.com`)

### Available Endpoints

1. WebSocket Connection
```javascript
// Connect to real-time updates
ws = new WebSocket(`ws://${API_URL}/ws`);
```

2. Control Device
```javascript
// Turn device ON/OFF
await fetch(`http://${API_URL}/control`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: "ON" }) // or "OFF"
});
```

3. Toggle Device
```javascript
// Toggle current state
await fetch(`http://${API_URL}/toggle`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
});
```

4. Get Current State
```javascript
// Check device status
const response = await fetch(`http://${API_URL}/state`);
const data = await response.json();
```

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