const toggleCameraBtn = document.getElementById('toggle-camera');
const localVideo = document.getElementById('local-video');
const canvas = document.getElementById('frame-canvas');
const ctx = canvas.getContext('2d', { willReadFrequently: true });
const processedFeed = document.getElementById('processed-feed');
const loadingOverlay = document.getElementById('loading-overlay');

const wsStatusDot = document.getElementById('ws-status-dot');
const wsStatusText = document.getElementById('ws-status-text');

let ws = null;
let stream = null;
let cameraActive = false;
let isProcessing = false;
let wsConnected = false;

// Connecting to the backend websocket
function connectWebSocket() {
    // Dynamically get the current host so it works LOCALLY and in CLOUD deployment 
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);
    
    ws.onopen = () => {
        console.log('Connected to WebSocket server');
        wsConnected = true;
        wsStatusDot.classList.add('connected');
        wsStatusText.textContent = 'Connected';
        wsStatusText.classList.add('connected');
    };
    
    ws.onmessage = (event) => {
        // Render the received base64 string directly into our image
        if (event.data) {
            processedFeed.src = event.data;
        }
        // Once we receive a frame, we can send another one (ping-pong style)
        // rather than sending on a blind interval to prevent queue buildup.
        isProcessing = false;
    };
    
    ws.onclose = () => {
        console.log('Disconnected from WebSocket server');
        wsConnected = false;
        wsStatusDot.classList.remove('connected');
        wsStatusText.textContent = 'Disconnected';
        wsStatusText.classList.remove('connected');
        
        // Try to reconnect in 2 seconds
        setTimeout(connectWebSocket, 2000);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
    };
}

// Start camera stream
async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user' 
            } 
        });
        
        localVideo.srcObject = stream;
        await localVideo.play();
        
        // Match canvas size to video size
        canvas.width = localVideo.videoWidth;
        canvas.height = localVideo.videoHeight;
        
        cameraActive = true;
        toggleCameraBtn.textContent = 'Stop Camera';
        toggleCameraBtn.classList.remove('primary');
        toggleCameraBtn.classList.add('danger');
        
        // Start the infinite rendering-capture loop
        requestAnimationFrame(processLoop);
        
    } catch (err) {
        console.error('Error accessing camera:', err);
        alert('Could not access camera. Please allow camera permissions.');
    }
}

// Stop camera stream
function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    localVideo.srcObject = null;
    cameraActive = false;
    toggleCameraBtn.textContent = 'Start Camera';
    toggleCameraBtn.classList.remove('danger');
    toggleCameraBtn.classList.add('primary');
}

toggleCameraBtn.addEventListener('click', () => {
    if (cameraActive) {
        stopCamera();
    } else {
        startCamera();
    }
});

function processLoop() {
    if (!cameraActive) return;
    
    // We only send a new frame if the websocket is connected
    // AND we are not currently waiting for the backend to process the last frame
    if (wsConnected && !isProcessing && ws.readyState === WebSocket.OPEN) {
        
        // Draw the current video frame to our hidden canvas
        ctx.drawImage(localVideo, 0, 0, canvas.width, canvas.height);
        
        // Compress the image slightly to reduce payload size (quality=0.6)
        const frameData = canvas.toDataURL('image/jpeg', 0.6);
        
        isProcessing = true;
        ws.send(frameData);
    }
    
    // Always request the next animation frame to keep loop going
    requestAnimationFrame(processLoop);
}

// Initialize connection on load
connectWebSocket();
