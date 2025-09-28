# 🌐 Using Decluttered.ai Agents Online - Setup Guide

## 📋 Overview

Your friend can use your deployed Decluttered.ai agents from anywhere! Here's how:

## 🚀 **Option 1: Simple HTTP API (Recommended)**

### Setup Instructions for Your Friend:

```bash
# 1. Install dependencies
pip install fastapi uvicorn uagents

# 2. Get the API wrapper file (friend_api_wrapper.py)
# 3. Update agent addresses in the file
# 4. Run the API wrapper
python friend_api_wrapper.py
```

### Usage in Friend's Python App:

```python
import requests
import time

# Upload image for processing
def process_image(image_path):
    url = "http://localhost:8080/api/process-image"

    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        return response.json()['session_id']
    else:
        raise Exception(f"Upload failed: {response.text}")

# Check processing status
def check_status(session_id):
    url = f"http://localhost:8080/api/status/{session_id}"
    response = requests.get(url)
    return response.json()

# Get final results
def get_results(session_id):
    url = f"http://localhost:8080/api/result/{session_id}"
    response = requests.get(url)
    return response.json()

# Complete example
def process_and_wait(image_path):
    # Start processing
    session_id = process_image(image_path)
    print(f"Processing started: {session_id}")

    # Wait for completion
    while True:
        status = check_status(session_id)
        print(f"Status: {status['status']} ({status['progress']*100:.0f}%)")

        if status['status'] == 'processing_complete':
            break

        time.sleep(5)  # Check every 5 seconds

    # Get final results
    results = get_results(session_id)
    print(f"Detected: {results['detected_objects']}")
    print(f"Resellable: {results['resellable_items']}")
    print(f"Crops created: {len(results['cropped_files'])}")

    return results

# Usage
results = process_and_wait("my_image.jpg")
```

### Web Frontend Integration:

```javascript
// JavaScript example for web apps
async function processImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:8080/api/process-image', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    return result.session_id;
}

async function checkStatus(sessionId) {
    const response = await fetch(`http://localhost:8080/api/status/${sessionId}`);
    return await response.json();
}

async function getResults(sessionId) {
    const response = await fetch(`http://localhost:8080/api/result/${sessionId}`);
    return await response.json();
}
```

---

## 🤖 **Option 2: Direct Agent Communication**

For more advanced users who want direct agent communication:

### Setup:

```bash
pip install uagents
```

### Code (using remote_client_example.py):

```python
from uagents import Agent, Context
# ... copy the message models and agent setup from remote_client_example.py

# Your friend's agent
friend_agent = Agent(
    name="friend_client",
    seed="friend_unique_seed",
    port=9000,
    mailbox=True
)

# Send images directly to your agents
@friend_agent.on_event("startup")
async def startup(ctx: Context):
    # Send image for processing
    captured_image = CapturedImage(
        filename="test.jpg",
        timestamp=int(time.time()),
        file_path="/path/to/image.jpg",
        capture_index=1,
        session_id="friend_session_123"
    )

    # Send to your detection agent
    await ctx.send("your_detection_agent_address", captured_image)

# Handle responses
@friend_agent.on_message(model=ProcessingResult)
async def handle_result(ctx: Context, sender: str, msg: ProcessingResult):
    print(f"Processing complete! Cropped files: {msg.cropped_files}")

friend_agent.run()
```

---

## 🔑 **Your Agent Addresses**

**IMPORTANT**: Your friend needs these exact addresses from your deployed agents:

```python
# Replace with your actual deployed agent addresses
AGENT_ADDRESSES = {
    "detection": "agent1qte25te5k79ygajeapzelgyle8ape8pvzdxdw9zndp4kph53qeq5unc8n6j",
    "ai_evaluator": "agent1q0vgqkwxlz7lfve6tqyse6z7m3zccv4uv7kt484jlc77dutxngzy62ea92p",
    "image_processor": "agent1qwgxuc8z9nsafsl30creg2hhykclaw4pnwm7ge9e5l3qakrx4r6nu67p2au",
    "report_coordinator": "agent1qvf8rwqhnuj85w9fl7kap6uszlk00gpjed0pq6vh289thwqys0zeq9w9g4y"
}
```

### How to Get Your Real Agent Addresses:

1. **Check Agent Logs**: Look for lines like:
   ```
   Starting agent with address: agent1qte25te5k79ygajeapzelgyle8ape8pvzdxdw9zndp4kph53qeq5unc8n6j
   ```

2. **Check Agentverse Dashboard**: Visit https://agentverse.ai and find your deployed agents

3. **Use Agent Inspector**: Each agent shows its inspector URL in logs

---

## 📱 **Integration Examples**

### Flask Web App:
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    # Forward to your agent API
    response = requests.post(
        'http://localhost:8080/api/process-image',
        files={'file': file}
    )

    return response.json()
```

### Django Views:
```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def process_image_view(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']

        response = requests.post(
            'http://localhost:8080/api/process-image',
            files={'file': image_file}
        )

        return JsonResponse(response.json())
```

### React Frontend:
```jsx
function ImageUploader() {
    const [file, setFile] = useState(null);
    const [results, setResults] = useState(null);

    const handleUpload = async () => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/process-image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        // Poll for results...
    };

    return (
        <div>
            <input type="file" onChange={(e) => setFile(e.target.files[0])} />
            <button onClick={handleUpload}>Analyze Image</button>
        </div>
    );
}
```

---

## 🔧 **Deployment Options**

### For Production:

1. **Deploy API Wrapper to Cloud**:
   - Heroku, AWS, Google Cloud, etc.
   - Update URLs in friend's code

2. **Use Docker**:
   ```dockerfile
   FROM python:3.11
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY friend_api_wrapper.py .
   CMD ["python", "friend_api_wrapper.py"]
   ```

3. **Environment Variables**:
   ```bash
   export DETECTION_AGENT_ADDRESS="agent1q..."
   export API_PORT="8080"
   ```

---

## ✅ **Quick Test**

Your friend can test the connection:

```bash
# 1. Start the API wrapper
python friend_api_wrapper.py

# 2. Test health endpoint
curl http://localhost:8080/api/health

# 3. Upload a test image
curl -X POST -F 'file=@test.jpg' http://localhost:8080/api/process-image
```

## 🎯 **Summary**

Your friend gets:
- ✅ **Simple HTTP API** for easy integration
- ✅ **Real-time status updates** during processing
- ✅ **Complete results** with detected objects and crops
- ✅ **Works with any programming language/framework**
- ✅ **No need to run your agents locally**

**Your agents stay deployed on Agentverse and handle all the heavy lifting!** 🚀