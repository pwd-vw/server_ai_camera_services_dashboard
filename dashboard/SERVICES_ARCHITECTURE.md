# วิเคราะห์สถาปัตยกรรม Services สำหรับ Edge AI Camera

## สารบัญ

1. [ภาพรวมสถาปัตยกรรม](#ภาพรวมสถาปัตยกรรม)
2. [ความแตกต่างระหว่าง Services](#ความแตกต่างระหว่าง-services)
3. [บทบาทและความจำเป็นของแต่ละ Service](#บทบาทและความจำเป็นของแต่ละ-service)
4. [แนวทางการใช้งานที่เหมาะสม](#แนวทางการใช้งานที่เหมาะสม)
5. [สรุปและคำแนะนำ](#สรุปและคำแนะนำ)

---

## ภาพรวมสถาปัตยกรรม

ระบบ AI Camera ประกอบด้วย 4 Services หลัก:

```
┌─────────────────────────────────────────────────────────────┐
│                    Edge AI Camera System                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ REST API     │    │ WebSocket    │    │ MQTT         │  │
│  │ (Port 3000)  │    │ (Port 3001)  │    │ Broker       │  │
│  │              │    │              │    │ (Port 1883)  │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                    │          │
│         │                   │                    │          │
│         └───────────────────┴────────────────────┘          │
│                              │                              │
│                    ┌─────────▼─────────┐                   │
│                    │ MQTT Microservice │                   │
│                    │ (NestJS)          │                   │
│                    └───────────────────┘                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ความแตกต่างระหว่าง Services

### 1. REST API (Backend API) - Port 3000

**ประเภท:** HTTP REST API  
**Framework:** NestJS  
**Protocol:** HTTP/HTTPS  
**Port:** 3000

**หน้าที่:**
- จัดการข้อมูลแบบ Request/Response
- CRUD operations (Create, Read, Update, Delete)
- Business logic และ data processing
- Authentication และ Authorization
- Database operations

**ลักษณะการทำงาน:**
- **Stateless:** แต่ละ request เป็นอิสระจากกัน
- **Synchronous:** Client ส่ง request และรอ response
- **Pull-based:** Client ต้อง request ข้อมูลเอง

**ตัวอย่างการใช้งาน:**
```javascript
// GET request
fetch('http://lprserver.tail605477.ts.net/api/cameras')
  .then(res => res.json())
  .then(data => console.log(data));

// POST request
fetch('http://lprserver.tail605477.ts.net/api/cameras', {
  method: 'POST',
  body: JSON.stringify({ name: 'Camera 1' })
});
```

---

### 2. WebSocket Service - Port 3001

**ประเภท:** WebSocket Gateway  
**Framework:** NestJS  
**Protocol:** WebSocket (ws://) หรือ WebSocket Secure (wss://)  
**Port:** 3001

**หน้าที่:**
- การสื่อสารแบบ Real-time Bi-directional
- Push notifications
- Live streaming (ภาพ, วิดีโอ)
- Real-time updates
- Low latency communication

**ลักษณะการทำงาน:**
- **Stateful:** เก็บ connection state
- **Asynchronous:** Server สามารถ push ข้อมูลได้ทันที
- **Push-based:** Server ส่งข้อมูลให้ client โดยไม่ต้องรอ request

**ตัวอย่างการใช้งาน:**
```javascript
const ws = new WebSocket('ws://lprserver.tail605477.ts.net:3001');

// ส่งภาพแบบ real-time
ws.onopen = () => {
  setInterval(() => {
    const imageData = captureFrame();
    ws.send(JSON.stringify({
      type: 'frame',
      data: imageData,
      timestamp: Date.now()
    }));
  }, 33); // ~30 FPS
};
```

---

### 3. MQTT Broker (AI Camera MQTT Broker) - Port 1883

**ประเภท:** MQTT Message Broker  
**Software:** Mosquitto  
**Protocol:** MQTT 3.1.1 / MQTT 5.0  
**Port:** 1883

**หน้าที่:**
- เป็น Message Broker กลางสำหรับ MQTT protocol
- จัดการ connections จาก MQTT clients
- Route messages ระหว่าง publishers และ subscribers
- จัดการ QoS (Quality of Service) levels
- Persistent sessions และ retained messages

**ลักษณะการทำงาน:**
- **Message Broker:** เป็นตัวกลางในการส่งข้อความ
- **Publish/Subscribe Pattern:** Clients publish ไปที่ topic และ subscribe เพื่อรับข้อความ
- **Lightweight:** Protocol ที่เบา เหมาะสำหรับ IoT devices
- **QoS Levels:** รองรับ 3 ระดับ (0, 1, 2)

**ตัวอย่างการใช้งาน:**
```python
import paho.mqtt.client as mqtt

# Client เชื่อมต่อกับ Broker
client = mqtt.Client()
client.connect("lprserver.tail605477.ts.net", 1883, 60)

# Publish (ส่งข้อความ)
client.publish("aicamera/camera_001/image", image_data)

# Subscribe (รับข้อความ)
client.subscribe("aicamera/camera_001/commands")
client.on_message = lambda c, u, msg: process_command(msg.payload)
```

---

### 4. MQTT Microservice - No Port (Internal)

**ประเภท:** NestJS Microservice  
**Framework:** NestJS with MQTT Transport  
**Protocol:** MQTT (Internal communication)  
**Port:** ไม่มี (เชื่อมต่อกับ MQTT Broker)

**หน้าที่:**
- เป็น Business Logic Layer ที่ทำงานผ่าน MQTT
- Process MQTT messages จาก cameras
- จัดการ business rules และ data transformation
- เชื่อมต่อกับ database หรือ services อื่นๆ
- ทำหน้าที่เป็น MQTT message handler

**ลักษณะการทำงาน:**
- **Microservice Pattern:** แยก business logic ออกมาเป็น service แยก
- **MQTT Transport:** ใช้ MQTT เป็น transport protocol สำหรับ microservice communication
- **Message Handler:** รับและประมวลผล MQTT messages
- **Internal Service:** ไม่เปิด port เอง แต่เชื่อมต่อกับ MQTT Broker

**ตัวอย่างการทำงาน:**
```typescript
// MQTT Microservice จะ subscribe topics และ process messages
@MessagePattern('aicamera/camera_001/image')
async handleImageMessage(data: ImageData) {
  // Process image
  const result = await this.imageProcessor.process(data);
  
  // Publish result back
  this.mqttClient.publish('aicamera/camera_001/result', result);
}
```

---

## บทบาทและความจำเป็นของแต่ละ Service

### REST API (Port 3000)

**จำเป็น:** ✅ **จำเป็น**  
**บทบาท:** 
- จัดการข้อมูลแบบ traditional HTTP requests
- CRUD operations สำหรับ cameras, users, settings
- Authentication และ authorization
- File upload/download
- Reports และ analytics

**เมื่อไหร่ควรใช้:**
- ✅ การจัดการข้อมูล (CRUD)
- ✅ Authentication/Authorization
- ✅ File upload/download
- ✅ Reports และ analytics
- ✅ Configuration management
- ❌ Real-time streaming
- ❌ Push notifications

---

### WebSocket Service (Port 3001)

**จำเป็น:** ✅ **แนะนำ** (ถ้าต้องการ real-time features)  
**บทบาท:**
- Real-time video/audio streaming
- Live notifications
- Bi-directional communication
- Low latency updates

**เมื่อไหร่ควรใช้:**
- ✅ Real-time video streaming
- ✅ Live notifications
- ✅ Interactive features (remote control)
- ✅ Live monitoring dashboard
- ❌ Simple request/response
- ❌ IoT devices ที่มี resource จำกัด

---

### MQTT Broker (Port 1883)

**จำเป็น:** ✅ **จำเป็น** (ถ้าใช้ MQTT)  
**บทบาท:**
- Message broker กลางสำหรับ MQTT protocol
- จัดการ connections จาก cameras และ devices
- Route messages ระหว่าง components

**เมื่อไหร่ควรใช้:**
- ✅ IoT devices และ Edge cameras
- ✅ Publish/Subscribe pattern
- ✅ Devices ที่มี resource จำกัด
- ✅ Network ที่ไม่เสถียร (รองรับ QoS)
- ✅ Many-to-many communication
- ❌ Real-time video streaming (ใช้ WebSocket แทน)
- ❌ Simple request/response (ใช้ REST API แทน)

---

### MQTT Microservice

**จำเป็น:** ⚠️ **อาจไม่จำเป็น** (ขึ้นอยู่กับ architecture)  
**บทบาท:**
- Business logic layer สำหรับ MQTT messages
- Process และ transform MQTT messages
- เชื่อมต่อกับ database หรือ services อื่นๆ

**เมื่อไหร่ควรใช้:**
- ✅ ต้องการแยก business logic ออกจาก MQTT Broker
- ✅ ต้องการ process messages ก่อนส่งต่อไป
- ✅ ต้องการเชื่อมต่อกับ database หรือ external services
- ✅ ต้องการ scalability และ microservices architecture
- ❌ Simple MQTT setup ที่ไม่ต้องการ business logic
- ❌ Direct communication ระหว่าง cameras และ applications

**คำถามสำคัญ:** MQTT Microservice จำเป็นหรือไม่?

**คำตอบ:** ขึ้นอยู่กับ architecture:

1. **ถ้าใช้ MQTT Broker โดยตรง:**
   - Cameras → MQTT Broker → Applications
   - ไม่จำเป็นต้องมี MQTT Microservice
   - ใช้ได้ถ้า applications สามารถ process messages ได้เอง

2. **ถ้าใช้ MQTT Microservice:**
   - Cameras → MQTT Broker → MQTT Microservice → Applications/Database
   - จำเป็นถ้าต้องการ business logic layer
   - จำเป็นถ้าต้องการ process messages ก่อนส่งต่อไป

---

## แนวทางการใช้งานที่เหมาะสม

### สถานการณ์ที่ 1: Simple Setup (ไม่ซับซ้อน)

**Services ที่ใช้:**
- ✅ REST API (Port 3000)
- ✅ MQTT Broker (Port 1883)
- ❌ WebSocket Service (ไม่ใช้)
- ❌ MQTT Microservice (ไม่ใช้)

**Architecture:**
```
Edge Camera → MQTT Broker → Application (subscribe MQTT)
Application → REST API → Database
```

**เหมาะสำหรับ:**
- Simple IoT setup
- Cameras ส่งข้อมูลเป็นระยะ (ไม่ใช่ real-time)
- ไม่ต้องการ real-time streaming
- ไม่ต้องการ business logic ที่ซับซ้อน

**ตัวอย่างการใช้งาน:**
```python
# Camera (Edge Device)
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("lprserver.tail605477.ts.net", 1883)

# ส่งข้อมูลภาพทุก 5 วินาที
while True:
    image = capture_image()
    client.publish("aicamera/camera_001/image", image)
    time.sleep(5)

# Application (รับข้อมูล)
client.subscribe("aicamera/camera_001/image")
client.on_message = lambda c, u, msg: save_to_database(msg.payload)
```

---

### สถานการณ์ที่ 2: Real-time Setup (แนะนำ)

**Services ที่ใช้:**
- ✅ REST API (Port 3000)
- ✅ WebSocket Service (Port 3001)
- ✅ MQTT Broker (Port 1883)
- ❌ MQTT Microservice (ไม่ใช้)

**Architecture:**
```
Edge Camera → MQTT Broker → Application (metadata, commands)
Edge Camera → WebSocket → Application (real-time video)
Application → REST API → Database
```

**เหมาะสำหรับ:**
- Real-time video streaming
- Live monitoring
- Interactive control
- Low latency requirements

**ตัวอย่างการใช้งาน:**
```python
# Camera (Edge Device)
# 1. Metadata ผ่าน MQTT
mqtt_client.publish("aicamera/camera_001/metadata", {
    "status": "active",
    "fps": 30,
    "resolution": "1920x1080"
})

# 2. Video stream ผ่าน WebSocket
ws = websocket.WebSocketApp("ws://lprserver.tail605477.ts.net:3001")
ws.onopen = lambda ws: stream_video(ws)  # Stream frames
```

---

### สถานการณ์ที่ 3: Enterprise Setup (ซับซ้อน)

**Services ที่ใช้:**
- ✅ REST API (Port 3000)
- ✅ WebSocket Service (Port 3001)
- ✅ MQTT Broker (Port 1883)
- ✅ MQTT Microservice

**Architecture:**
```
Edge Camera → MQTT Broker → MQTT Microservice → Database/Applications
Edge Camera → WebSocket → Application (real-time)
Application → REST API → Database
Application ↔ MQTT Microservice (commands)
```

**เหมาะสำหรับ:**
- Complex business logic
- Data processing และ transformation
- Integration กับ multiple systems
- Scalability requirements
- Microservices architecture

**ตัวอย่างการใช้งาน:**
```python
# Camera → MQTT Broker → MQTT Microservice → Database
# MQTT Microservice จะ process และ save ข้อมูล

# Camera
mqtt_client.publish("aicamera/camera_001/detection", {
    "object": "car",
    "confidence": 0.95,
    "bbox": [100, 200, 300, 400]
})

# MQTT Microservice จะ:
# 1. รับ message
# 2. Validate และ process
# 3. Save ลง database
# 4. Trigger alerts ถ้าจำเป็น
# 5. Publish result กลับไป
```

---

## สรุปและคำแนะนำ

### ความแตกต่างหลัก

| Service | Protocol | Port | บทบาท | จำเป็น |
|---------|----------|------|-------|--------|
| **REST API** | HTTP | 3000 | Request/Response, CRUD | ✅ จำเป็น |
| **WebSocket** | WebSocket | 3001 | Real-time streaming | ⚠️ แนะนำ |
| **MQTT Broker** | MQTT | 1883 | Message broker | ✅ จำเป็น (ถ้าใช้ MQTT) |
| **MQTT Microservice** | MQTT (Internal) | - | Business logic | ⚠️ ขึ้นอยู่กับ architecture |

### คำแนะนำสำหรับ Edge AI Camera

#### 1. **REST API (Port 3000)** - ใช้สำหรับ:
- ✅ Configuration management
- ✅ Camera registration และ management
- ✅ User authentication
- ✅ Reports และ analytics
- ✅ File upload/download
- ✅ Settings และ preferences

**ตัวอย่าง:**
```javascript
// ลงทะเบียน camera
POST /api/cameras
{
  "name": "Camera 001",
  "location": "Entrance",
  "ip": "192.168.1.100"
}

// ดึงรายการ cameras
GET /api/cameras

// อัปเดต settings
PUT /api/cameras/001/settings
{
  "fps": 30,
  "resolution": "1920x1080"
}
```

#### 2. **WebSocket (Port 3001)** - ใช้สำหรับ:
- ✅ Real-time video streaming
- ✅ Live monitoring dashboard
- ✅ Remote control (PTZ, zoom, etc.)
- ✅ Real-time alerts และ notifications
- ✅ Bi-directional commands

**ตัวอย่าง:**
```javascript
// Camera → Server: Stream video frames
ws.send(JSON.stringify({
  type: 'frame',
  camera_id: 'camera_001',
  frame: base64Image,
  timestamp: Date.now()
}));

// Server → Camera: Control commands
ws.send(JSON.stringify({
  type: 'command',
  action: 'zoom',
  value: 2.0
}));
```

#### 3. **MQTT Broker (Port 1883)** - ใช้สำหรับ:
- ✅ Metadata และ sensor data
- ✅ Commands และ control messages
- ✅ Status updates
- ✅ Event notifications
- ✅ IoT devices communication

**ตัวอย่าง:**
```python
# Camera → MQTT Broker: ส่ง metadata
mqtt_client.publish("aicamera/camera_001/metadata", {
    "temperature": 45.5,
    "humidity": 60,
    "status": "active"
})

# Camera → MQTT Broker: ส่ง detection results
mqtt_client.publish("aicamera/camera_001/detections", {
    "objects": [
        {"type": "person", "confidence": 0.95},
        {"type": "car", "confidence": 0.87}
    ]
})

# Server → Camera: ส่ง commands
mqtt_client.publish("aicamera/camera_001/commands", {
    "action": "record",
    "duration": 60
})
```

#### 4. **MQTT Microservice** - ใช้สำหรับ:
- ✅ Process และ validate MQTT messages
- ✅ Data transformation
- ✅ Business logic และ rules
- ✅ Integration กับ database
- ✅ Trigger actions และ workflows

**ตัวอย่าง:**
```typescript
// MQTT Microservice จะ:
// 1. Subscribe topics จาก cameras
// 2. Process messages (validate, transform)
// 3. Save ลง database
// 4. Trigger alerts ถ้าจำเป็น
// 5. Publish processed results
```

---

### คำแนะนำการเลือกใช้

#### สำหรับ Simple Setup (ไม่ซับซ้อน):

**ใช้:**
- ✅ REST API (Port 3000)
- ✅ MQTT Broker (Port 1883)

**ไม่ใช้:**
- ❌ WebSocket Service
- ❌ MQTT Microservice

**เหตุผล:**
- Simple และ maintainable
- เหมาะสำหรับ basic IoT setup
- Cameras ส่งข้อมูลเป็นระยะ ไม่ใช่ real-time

---

#### สำหรับ Standard Setup (แนะนำ):

**ใช้:**
- ✅ REST API (Port 3000)
- ✅ WebSocket Service (Port 3001)
- ✅ MQTT Broker (Port 1883)

**ไม่ใช้:**
- ❌ MQTT Microservice (ถ้าไม่ต้องการ business logic)

**เหตุผล:**
- รองรับทั้ง real-time streaming และ IoT communication
- Flexible และ scalable
- ไม่ซับซ้อนเกินไป

---

#### สำหรับ Enterprise Setup (ซับซ้อน):

**ใช้:**
- ✅ REST API (Port 3000)
- ✅ WebSocket Service (Port 3001)
- ✅ MQTT Broker (Port 1883)
- ✅ MQTT Microservice

**เหตุผล:**
- Complex business logic
- Data processing และ transformation
- Integration กับ multiple systems
- Microservices architecture

---

### แนวทางการใช้งานที่เหมาะสม

#### Pattern 1: Hybrid Communication

```
┌─────────────┐
│ Edge Camera │
└──────┬──────┘
       │
       ├─── MQTT ────→ Metadata, Events, Commands
       │
       └─── WebSocket ────→ Real-time Video Stream
```

**ใช้เมื่อ:**
- ต้องการ real-time video streaming
- ต้องการ metadata และ commands แยกกัน
- ต้องการ optimize bandwidth

---

#### Pattern 2: MQTT Only

```
┌─────────────┐
│ Edge Camera │
└──────┬──────┘
       │
       └─── MQTT ────→ Everything (metadata, images, commands)
```

**ใช้เมื่อ:**
- Simple setup
- ไม่ต้องการ real-time streaming
- Cameras ส่งข้อมูลเป็นระยะ
- Resource จำกัด

---

#### Pattern 3: WebSocket Only

```
┌─────────────┐
│ Edge Camera │
└──────┬──────┘
       │
       └─── WebSocket ────→ Everything (real-time)
```

**ใช้เมื่อ:**
- Real-time streaming เป็นหลัก
- Bi-directional communication
- Low latency requirements
- ไม่ต้องการ MQTT features (QoS, retained messages)

---

### คำแนะนำสำหรับ Edge AI Camera

#### 1. **Metadata และ Status Updates** → ใช้ **MQTT**

```python
# Camera ส่ง metadata ทุก 10 วินาที
mqtt_client.publish("aicamera/camera_001/status", {
    "online": True,
    "fps": 30,
    "temperature": 45.5,
    "storage_used": "2.5GB"
})
```

**เหตุผล:**
- Lightweight protocol
- รองรับ QoS (guaranteed delivery)
- เหมาะสำหรับ periodic updates
- ไม่ต้อง maintain persistent connection

---

#### 2. **Real-time Video Streaming** → ใช้ **WebSocket**

```javascript
// Camera stream video frames
ws.send(JSON.stringify({
  type: 'frame',
  frame: base64Image,
  timestamp: Date.now()
}));
```

**เหตุผล:**
- Low latency
- Bi-directional
- เหมาะสำหรับ streaming
- Persistent connection

---

#### 3. **Commands และ Control** → ใช้ **MQTT** หรือ **WebSocket**

**MQTT:**
```python
# Server → Camera: ส่ง command
mqtt_client.publish("aicamera/camera_001/commands", {
    "action": "record",
    "duration": 60
})
```

**WebSocket:**
```javascript
// Server → Camera: ส่ง command
ws.send(JSON.stringify({
  type: 'command',
  action: 'zoom',
  value: 2.0
}));
```

**เลือกใช้:**
- **MQTT:** ถ้าไม่ต้องการ immediate response
- **WebSocket:** ถ้าต้องการ real-time control

---

#### 4. **Configuration และ Management** → ใช้ **REST API**

```javascript
// ตั้งค่า camera
PUT /api/cameras/001/settings
{
  "fps": 30,
  "resolution": "1920x1080",
  "ai_model": "yolo_v8"
}
```

**เหตุผล:**
- Standard HTTP protocol
- Easy to use
- Stateless
- เหมาะสำหรับ CRUD operations

---

### สรุป: จำเป็นต้องมีทั้งสอง Service (MQTT Broker + MQTT Microservice) หรือไม่?

#### คำตอบ: **ไม่จำเป็น** แต่ขึ้นอยู่กับ architecture

**ถ้าไม่ใช้ MQTT Microservice:**
- ✅ Simple และ maintainable
- ✅ Cameras → MQTT Broker → Applications โดยตรง
- ✅ Applications process messages เอง
- ⚠️ Business logic อยู่ใน applications

**ถ้าใช้ MQTT Microservice:**
- ✅ แยก business logic ออกมา
- ✅ Centralized message processing
- ✅ Scalable และ maintainable
- ⚠️ เพิ่มความซับซ้อน

**คำแนะนำ:**
- **เริ่มต้น:** ใช้แค่ MQTT Broker
- **เมื่อต้องการ:** เพิ่ม MQTT Microservice เมื่อ business logic ซับซ้อนขึ้น

---

## สรุป

### Services ที่แนะนำสำหรับ Edge AI Camera

1. **REST API (Port 3000)** - ✅ จำเป็น
   - Configuration และ management
   - CRUD operations

2. **WebSocket (Port 3001)** - ✅ แนะนำ
   - Real-time video streaming
   - Live monitoring

3. **MQTT Broker (Port 1883)** - ✅ จำเป็น (ถ้าใช้ MQTT)
   - Metadata และ sensor data
   - Commands และ control

4. **MQTT Microservice** - ⚠️ ขึ้นอยู่กับ architecture
   - Business logic layer
   - Message processing

### แนวทางการใช้งาน

- **Simple:** REST API + MQTT Broker
- **Standard:** REST API + WebSocket + MQTT Broker
- **Enterprise:** REST API + WebSocket + MQTT Broker + MQTT Microservice

---

---

## ตัวอย่างการใช้งานจริง

### Scenario 1: Edge AI Camera ส่งภาพและ Metadata

```python
# Edge Camera Code
import paho.mqtt.client as mqtt
import websocket
import json
import base64
import cv2

# 1. เชื่อมต่อ MQTT สำหรับ metadata
mqtt_client = mqtt.Client()
mqtt_client.connect("lprserver.tail605477.ts.net", 1883)

# 2. เชื่อมต่อ WebSocket สำหรับ video streaming
ws = websocket.WebSocketApp("ws://lprserver.tail605477.ts.net:3001")

def on_ws_open(ws):
    print("WebSocket connected - starting video stream")

def stream_video(ws):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if ret:
            # Encode frame
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode()
            
            # ส่งผ่าน WebSocket
            ws.send(json.dumps({
                "type": "frame",
                "camera_id": "camera_001",
                "frame": frame_base64,
                "timestamp": int(time.time() * 1000)
            }))
        time.sleep(0.033)  # ~30 FPS

ws.on_open = on_ws_open
ws_thread = threading.Thread(target=lambda: ws.run_forever())
ws_thread.start()

# 3. ส่ง metadata ผ่าน MQTT
while True:
    metadata = {
        "camera_id": "camera_001",
        "status": "active",
        "fps": 30,
        "resolution": "1920x1080",
        "temperature": get_temperature(),
        "timestamp": int(time.time())
    }
    mqtt_client.publish("aicamera/camera_001/metadata", json.dumps(metadata))
    time.sleep(10)  # ส่งทุก 10 วินาที
```

### Scenario 2: Server รับข้อมูลและควบคุม Camera

```python
# Server Code
import paho.mqtt.client as mqtt
import websocket
import json

# 1. Subscribe MQTT สำหรับ metadata
mqtt_client = mqtt.Client()
mqtt_client.connect("lprserver.tail605477.ts.net", 1883)

def on_mqtt_message(client, userdata, msg):
    metadata = json.loads(msg.payload)
    print(f"Received metadata: {metadata}")
    # Process และ save ลง database
    save_to_database(metadata)

mqtt_client.subscribe("aicamera/+/metadata")
mqtt_client.on_message = on_mqtt_message
mqtt_client.loop_start()

# 2. เชื่อมต่อ WebSocket สำหรับ video stream
ws = websocket.WebSocketApp("ws://lprserver.tail605477.ts.net:3001")

def on_ws_message(ws, message):
    data = json.loads(message)
    if data['type'] == 'frame':
        # Process frame
        frame = base64.b64decode(data['frame'])
        process_frame(frame, data['camera_id'])

ws.on_message = on_ws_message
ws.run_forever()

# 3. ส่ง commands ผ่าน MQTT
def send_command(camera_id, command):
    mqtt_client.publish(f"aicamera/{camera_id}/commands", json.dumps(command))

# ตัวอย่าง: บันทึกวิดีโอ 60 วินาที
send_command("camera_001", {
    "action": "record",
    "duration": 60
})
```

### Scenario 3: ใช้ MQTT Microservice สำหรับ Business Logic

```typescript
// MQTT Microservice (NestJS)
@Controller()
export class CameraController {
  constructor(
    private readonly cameraService: CameraService,
    private readonly mqttClient: MqttService
  ) {}

  @MessagePattern('aicamera/+/metadata')
  async handleMetadata(@Payload() data: CameraMetadata) {
    // 1. Validate data
    if (!this.validateMetadata(data)) {
      return { error: 'Invalid metadata' };
    }

    // 2. Process และ transform
    const processed = await this.cameraService.processMetadata(data);

    // 3. Save ลง database
    await this.cameraService.saveToDatabase(processed);

    // 4. Check alerts
    if (processed.temperature > 50) {
      await this.triggerAlert(processed);
    }

    // 5. Publish processed result
    this.mqttClient.publish(
      `aicamera/${data.camera_id}/processed`,
      processed
    );

    return { success: true };
  }

  @MessagePattern('aicamera/+/detections')
  async handleDetections(@Payload() data: DetectionData) {
    // Process AI detection results
    const results = await this.aiService.processDetections(data);
    
    // Save และ trigger actions
    await this.cameraService.handleDetections(results);
    
    return results;
  }
}
```

---

## Decision Tree: เลือกใช้ Service อย่างไร?

```
เริ่มต้น
  │
  ├─ ต้องการ Real-time Video Streaming?
  │   ├─ ใช่ → ใช้ WebSocket (Port 3001)
  │   └─ ไม่ → ข้าม
  │
  ├─ ต้องการ IoT Communication?
  │   ├─ ใช่ → ใช้ MQTT Broker (Port 1883)
  │   └─ ไม่ → ข้าม
  │
  ├─ ต้องการ Business Logic Processing?
  │   ├─ ใช่ → ใช้ MQTT Microservice
  │   └─ ไม่ → ข้าม
  │
  └─ ต้องการ Traditional HTTP API?
      ├─ ใช่ → ใช้ REST API (Port 3000)
      └─ ไม่ → ข้าม
```

---

## FAQ

### Q: จำเป็นต้องมีทั้ง MQTT Broker และ MQTT Microservice หรือไม่?

**A:** ไม่จำเป็น แต่ขึ้นอยู่กับ architecture:

- **ถ้าไม่ใช้ MQTT Microservice:**
  - Cameras → MQTT Broker → Applications โดยตรง
  - Applications process messages เอง
  - Simple และ maintainable

- **ถ้าใช้ MQTT Microservice:**
  - Cameras → MQTT Broker → MQTT Microservice → Applications/Database
  - Business logic อยู่ใน MQTT Microservice
  - Centralized processing

**คำแนะนำ:** เริ่มต้นด้วย MQTT Broker เพียงอย่างเดียว แล้วเพิ่ม MQTT Microservice เมื่อ business logic ซับซ้อนขึ้น

---

### Q: WebSocket และ MQTT ต่างกันอย่างไร?

**A:**

| Feature | WebSocket | MQTT |
|---------|-----------|------|
| **Protocol** | WebSocket (ws://) | MQTT |
| **Latency** | Very Low | Low |
| **QoS** | ไม่มี | 3 ระดับ (0, 1, 2) |
| **Retained Messages** | ไม่มี | มี |
| **Persistent Sessions** | Connection-based | Session-based |
| **เหมาะสำหรับ** | Real-time streaming | IoT, Periodic updates |
| **Bi-directional** | ✅ ใช่ | ✅ ใช่ |
| **Lightweight** | ❌ ไม่ | ✅ ใช่ |

---

### Q: ควรใช้ REST API, WebSocket, หรือ MQTT สำหรับอะไร?

**A:**

| Use Case | Service | เหตุผล |
|----------|---------|--------|
| **Configuration** | REST API | Standard, Easy to use |
| **Real-time Video** | WebSocket | Low latency, Streaming |
| **Metadata/Status** | MQTT | Lightweight, Periodic |
| **Commands** | MQTT หรือ WebSocket | ขึ้นอยู่กับ requirements |
| **File Upload** | REST API | Standard HTTP |
| **Live Monitoring** | WebSocket | Real-time updates |
| **IoT Devices** | MQTT | Lightweight, QoS |

---

### Q: MQTT Microservice ทำอะไร?

**A:** MQTT Microservice เป็น business logic layer ที่:
- Subscribe MQTT topics จาก cameras
- Process และ validate messages
- Transform data
- Save ลง database
- Trigger actions และ workflows
- Publish processed results

**ตัวอย่าง:**
```
Camera → MQTT Broker → MQTT Microservice → Database
                              ↓
                        Process & Validate
                              ↓
                        Save & Trigger Actions
```

---

### Q: ถ้าไม่ใช้ MQTT Microservice จะทำอย่างไร?

**A:** Applications จะ subscribe MQTT topics โดยตรง:

```
Camera → MQTT Broker → Application (subscribe)
                              ↓
                        Process & Save
```

**ข้อดี:**
- Simple และ direct
- ไม่มี extra layer
- เหมาะสำหรับ simple setup

**ข้อเสีย:**
- Business logic กระจัดกระจาย
- ยากต่อการ maintain
- ไม่เหมาะสำหรับ complex logic

---

**เวอร์ชัน:** 1.0  
**อัปเดตล่าสุด:** 2026-02-16

