# คู่มือการใช้งาน AI Camera Services Dashboard

## สารบัญ

1. [ภาพรวม](#ภาพรวม)
2. [การเข้าถึง Dashboard](#การเข้าถึง-dashboard)
3. [ส่วนประกอบของ Dashboard](#ส่วนประกอบของ-dashboard)
4. [การควบคุม Services](#การควบคุม-services)
5. [การตั้งค่าลูกข่ายสำหรับเชื่อมต่อ Services](#การตั้งค่าลูกข่ายสำหรับเชื่อมต่อ-services)
6. [การทดสอบการเชื่อมต่อ](#การทดสอบการเชื่อมต่อ)
7. [การแก้ไขปัญหา](#การแก้ไขปัญหา)
8. [FAQ](#faq)

---

## ภาพรวม

AI Camera Services Dashboard เป็นเครื่องมือสำหรับควบคุมและตรวจสอบสถานะของ Services ที่เกี่ยวข้องกับ AI Camera System ประกอบด้วย:

- **WebSocket Service** - บริการสำหรับการสื่อสารแบบ Real-time ผ่าน WebSocket
- **MQTT Microservice** - บริการสำหรับจัดการ MQTT messages
- **AI Camera MQTT Broker** - MQTT Broker สำหรับรับส่งข้อมูลจากเครื่องลูกข่าย

### คุณสมบัติหลัก

- ✅ แสดงสถานะ Services แบบ Real-time
- ✅ ควบคุมการทำงาน (Start, Stop, Restart)
- ✅ ดูและแก้ไข Configuration Files
- ✅ ดูและแก้ไข Storage Path
- ✅ ดู Logs แบบ Real-time
- ✅ Auto-refresh ทุก 5 วินาที

---

## การเข้าถึง Dashboard

### วิธีที่ 1: ผ่าน Nginx (แนะนำ)

```
http://lprserver.tail605477.ts.net/dashboard/
```


### วิธีที่ 2: โดยตรง

```
http://lprserver.tail605477.ts.net:5000/
```

**หมายเหตุ:** วิธีนี้ต้องเปิด port 5000 ใน firewall

---

## ส่วนประกอบของ Dashboard

### 1. Header Section

- **ชื่อ Dashboard:** "AI Camera Services Dashboard"
- **สถานะการเชื่อมต่อ:** แสดงสถานะการเชื่อมต่อกับ API
  - 🟢 "เชื่อมต่อแล้ว" - เชื่อมต่อสำเร็จ
  - 🟡 "กำลังเชื่อมต่อ..." - กำลังเชื่อมต่อ
  - 🔴 "ไม่สามารถเชื่อมต่อได้" - เชื่อมต่อล้มเหลว
- **ปุ่มรีเฟรช:** สำหรับรีเฟรชข้อมูลด้วยตนเอง

### 2. Service Cards

แต่ละ Service จะแสดงในรูปแบบ Card ที่มีข้อมูล:

- **ชื่อ Service:** ชื่อที่แสดงและชื่อจริงของ service
- **สถานะ:** 
  - 🟢 ทำงาน - Service กำลังทำงานอยู่
  - 🔴 หยุดทำงาน - Service หยุดทำงาน
- **รายละเอียด:**
  - ชื่อ Service (service name)
  - สถานะ (state และ substate)
  - พอร์ต (ถ้ามี)
  - Working Directory (ถ้ามี)
  - Process ID (ถ้ากำลังทำงาน)

### 3. ปุ่มควบคุม

แต่ละ Service มีปุ่มควบคุมดังนี้:

- **▶ เริ่ม** - เริ่ม service
- **⏹ หยุด** - หยุด service
- **🔄 รีสตาร์ท** - รีสตาร์ท service
- **⚙️ Config** - ดูและแก้ไข configuration
- **📁 Storage** - ดูและแก้ไข storage path
- **📋 Logs** - ดู logs

---

## การควบคุม Services

### เริ่ม Service

1. คลิกปุ่ม **▶ เริ่ม** บน Service Card
2. ยืนยันการเริ่ม service
3. รอสักครู่ Dashboard จะอัปเดตสถานะอัตโนมัติ

### หยุด Service

1. คลิกปุ่ม **⏹ หยุด** บน Service Card
2. ยืนยันการหยุด service
3. รอสักครู่ Dashboard จะอัปเดตสถานะอัตโนมัติ

### รีสตาร์ท Service

1. คลิกปุ่ม **🔄 รีสตาร์ท** บน Service Card
2. ยืนยันการรีสตาร์ท service
3. รอสักครู่ Dashboard จะอัปเดตสถานะอัตโนมัติ

### ดูและแก้ไข Configuration

1. คลิกปุ่ม **⚙️ Config** บน Service Card
2. Modal จะแสดง configuration file
3. แก้ไขเนื้อหาใน text area
4. เลือก "รีสตาร์ท service หลังอัปเดต" (ถ้าต้องการ)
5. คลิก **💾 บันทึก**

**คำเตือน:** การแก้ไข configuration อาจทำให้ service ไม่สามารถเริ่มทำงานได้ ควรทำการ backup ก่อน

### ดูและแก้ไข Storage Path

1. คลิกปุ่ม **📁 Storage** บน Service Card
2. Modal จะแสดง storage path ปัจจุบัน
3. แก้ไข path ใหม่
4. เลือก "รีสตาร์ท service หลังอัปเดต" (ถ้าต้องการ)
5. คลิก **💾 บันทึก**

**หมายเหตุ:** Path จะถูกสร้างอัตโนมัติถ้ายังไม่มี

### ดู Logs

1. คลิกปุ่ม **📋 Logs** บน Service Card
2. Modal จะแสดง logs
3. เลือกจำนวนบรรทัดที่ต้องการ (50, 100, 200, 500)
4. คลิก **🔄 โหลด Logs** เพื่อรีเฟรช

---

## การตั้งค่าลูกข่ายสำหรับเชื่อมต่อ Services

### WebSocket Service

#### พอร์ตและ Protocol

- **Port:** 3001
- **Protocol:** WebSocket (ws://) หรือ WebSocket Secure (wss://)

#### การตั้งค่าลูกข่าย

**JavaScript (Browser):**
```javascript
const ws = new WebSocket('ws://lprserver.tail605477.ts.net:3001');

ws.onopen = () => {
    console.log('Connected to WebSocket');
};

ws.onmessage = (event) => {
    console.log('Message:', event.data);
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('WebSocket closed');
};
```

**Python:**
```python
import websocket
import json

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket connected")
    # ส่งข้อความ
    ws.send(json.dumps({"type": "ping"}))

ws = websocket.WebSocketApp(
    "ws://lprserver.tail605477.ts.net:3001",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()
```

**Node.js:**
```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://lprserver.tail605477.ts.net:3001');

ws.on('open', () => {
    console.log('Connected to WebSocket');
    ws.send(JSON.stringify({ type: 'ping' }));
});

ws.on('message', (data) => {
    console.log('Received:', data.toString());
});

ws.on('error', (error) => {
    console.error('WebSocket error:', error);
});

ws.on('close', () => {
    console.log('WebSocket closed');
});
```

### MQTT Microservice

#### พอร์ตและ Protocol

- **Port:** 1883 (MQTT standard)
- **Protocol:** MQTT 3.1.1 หรือ MQTT 5.0

#### การตั้งค่าลูกข่าย

**Python (paho-mqtt):**
```python
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe("aicamera/#")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}, Message: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("lprserver.tail605477.ts.net", 1883, 60)
client.loop_forever()
```

**Node.js (mqtt):**
```javascript
const mqtt = require('mqtt');

const client = mqtt.connect('mqtt://lprserver.tail605477.ts.net:1883');

client.on('connect', () => {
    console.log('Connected to MQTT broker');
    client.subscribe('aicamera/#');
});

client.on('message', (topic, message) => {
    console.log(`Topic: ${topic}, Message: ${message.toString()}`);
});

// ส่งข้อความ
client.publish('aicamera/test', 'Hello from client');
```

**C/C++ (Eclipse Paho):**
```c
#include <MQTTClient.h>

#define ADDRESS     "tcp://lprserver.tail605477.ts.net:1883"
#define CLIENTID    "client_id"
#define TOPIC       "aicamera/test"
#define QOS         1
#define TIMEOUT     10000L

int main(int argc, char* argv[])
{
    MQTTClient client;
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    MQTTClient_message pubmsg = MQTTClient_message_initializer;
    MQTTClient_deliveryToken token;
    int rc;

    MQTTClient_create(&client, ADDRESS, CLIENTID,
        MQTTCLIENT_PERSISTENCE_NONE, NULL);
    conn_opts.keepAliveInterval = 20;
    conn_opts.cleansession = 1;

    if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS)
    {
        printf("Failed to connect, return code %d\n", rc);
        exit(-1);
    }

    pubmsg.payload = "Hello from C client";
    pubmsg.payloadlen = strlen(pubmsg.payload);
    pubmsg.qos = QOS;
    pubmsg.retained = 0;
    MQTTClient_publishMessage(client, TOPIC, &pubmsg, &token);
    printf("Waiting for up to %d seconds for publication\n", (int)(TIMEOUT/1000));
    rc = MQTTClient_waitForCompletion(client, token, TIMEOUT);
    printf("Message delivered\n");

    MQTTClient_disconnect(client, 10000);
    MQTTClient_destroy(&client);
    return rc;
}
```

### AI Camera MQTT Broker (Mosquitto)

#### พอร์ตและ Protocol

- **Port:** 1883 (MQTT standard)
- **Protocol:** MQTT 3.1.1 หรือ MQTT 5.0
- **Config File:** `/etc/mosquitto/conf.d/aicamera.conf`

#### การตั้งค่าลูกข่าย

การตั้งค่าเหมือนกับ MQTT Microservice แต่ใช้ port เดียวกัน (1883)

**หมายเหตุ:** MQTT Broker และ MQTT Microservice ใช้ port เดียวกัน แต่ทำงานคนละหน้าที่

### ตัวอย่างการใช้งานจริง

#### WebSocket - ส่งข้อมูลภาพ

```javascript
// Client ส่งภาพไปยัง Server
const ws = new WebSocket('ws://lprserver.tail605477.ts.net:3001');

ws.onopen = () => {
    const canvas = document.getElementById('canvas');
    const imageData = canvas.toDataURL('image/jpeg');
    ws.send(JSON.stringify({
        type: 'image',
        data: imageData,
        timestamp: Date.now()
    }));
};
```

#### MQTT - Publish/Subscribe Pattern

```python
# Publisher (ส่งข้อมูล)
import paho.mqtt.client as mqtt
import json

client = mqtt.Client()
client.connect("lprserver.tail605477.ts.net", 1883, 60)

# ส่งข้อมูลภาพ
data = {
    "camera_id": "camera_001",
    "image": "base64_encoded_image",
    "timestamp": "2026-02-16T12:00:00Z"
}
client.publish("aicamera/images", json.dumps(data))

# Subscriber (รับข้อมูล)
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(f"Received image from {data['camera_id']}")

client.subscribe("aicamera/images")
client.on_message = on_message
client.loop_forever()
```

### การตั้งค่า Firewall

#### สำหรับ WebSocket (Port 3001)

```bash
# UFW
sudo ufw allow 3001/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 3001 -j ACCEPT
```

#### สำหรับ MQTT (Port 1883)

```bash
# UFW
sudo ufw allow 1883/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 1883 -j ACCEPT
```

### การตั้งค่า Authentication (ถ้าต้องการ)

#### MQTT Authentication

1. สร้าง password file:
```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd username
```

2. แก้ไข config:
```ini
# /etc/mosquitto/conf.d/aicamera.conf
allow_anonymous false
password_file /etc/mosquitto/passwd
```

3. ใช้ใน client:
```python
client.username_pw_set("username", "password")
```

---

## การทดสอบการเชื่อมต่อ

### ทดสอบ WebSocket Service

#### 1. ใช้ Browser Console

```javascript
const ws = new WebSocket('ws://lprserver.tail605477.ts.net:3001');
ws.onopen = () => console.log('✅ Connected');
ws.onerror = (e) => console.error('❌ Error:', e);
ws.onclose = () => console.log('🔌 Closed');
```

#### 2. ใช้ wscat (Command Line)

```bash
# ติดตั้ง wscat
npm install -g wscat

# ทดสอบเชื่อมต่อ
wscat -c ws://lprserver.tail605477.ts.net:3001
```

#### 3. ใช้ curl (HTTP Upgrade)

```bash
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://lprserver.tail605477.ts.net:3001/
```

### ทดสอบ MQTT Services

#### 1. ใช้ mosquitto_pub และ mosquitto_sub

```bash
# ติดตั้ง mosquitto-clients
sudo apt-get install mosquitto-clients

# Subscribe (รับข้อความ)
mosquitto_sub -h lprserver.tail605477.ts.net -p 1883 -t "aicamera/#" -v

# Publish (ส่งข้อความ)
mosquitto_pub -h lprserver.tail605477.ts.net -p 1883 -t "aicamera/test" -m "Hello MQTT"
```

#### 2. ใช้ Python Script

```python
import paho.mqtt.client as mqtt
import time

def test_connection():
    client = mqtt.Client()
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to MQTT broker")
            client.publish("aicamera/test", "Test message")
        else:
            print(f"❌ Failed to connect, return code {rc}")
    
    def on_publish(client, userdata, mid):
        print("✅ Message published")
        client.disconnect()
    
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    try:
        client.connect("lprserver.tail605477.ts.net", 1883, 60)
        client.loop_start()
        time.sleep(2)
        client.loop_stop()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_connection()
```

#### 3. ใช้ telnet (ทดสอบพอร์ต)

```bash
telnet lprserver.tail605477.ts.net 1883
```

ถ้าเชื่อมต่อได้จะเห็น:
```
Trying lprserver.tail605477.ts.net...
Connected to lprserver.tail605477.ts.net.
Escape character is '^]'.
```

### ทดสอบผ่าน Dashboard

1. เปิด Dashboard
2. ตรวจสอบสถานะ Services
3. ดู Logs ของแต่ละ Service
4. ทดสอบ Start/Stop/Restart

---

## การแก้ไขปัญหา

### ปัญหา: Dashboard ไม่แสดงผล

**อาการ:**
- หน้าเว็บเป็นสีขาว
- ไม่มีข้อมูลแสดง
- Console แสดง error

**วิธีแก้ไข:**

1. **ตรวจสอบสถานะ Dashboard Service:**
   ```bash
   systemctl status dashboard.service
   ```

2. **ตรวจสอบ Port 5000:**
   ```bash
   ss -tulpn | grep 5000
   ```

3. **ตรวจสอบ Nginx:**
   ```bash
   sudo systemctl status nginx
   sudo nginx -t
   ```

4. **ตรวจสอบ Logs:**
   ```bash
   sudo journalctl -u dashboard.service -n 50
   sudo tail -f /var/log/nginx/error.log
   ```

5. **Restart Services:**
   ```bash
   sudo systemctl restart dashboard.service
   sudo systemctl reload nginx
   ```

### ปัญหา: Static Files ไม่แสดง (CSS/JS ไม่โหลด)

**อาการ:**
- หน้าเว็บไม่มี styling
- ปุ่มไม่ทำงาน
- Console แสดง 404 สำหรับ CSS/JS

**วิธีแก้ไข:**

1. **ตรวจสอบ Nginx Config:**
   ```bash
   sudo nginx -t
   ```

2. **ตรวจสอบ Static Files:**
   ```bash
   curl -I http://lprserver.tail605477.ts.net/dashboard/static/style.css
   curl -I http://lprserver.tail605477.ts.net/dashboard/static/app.js
   ```

3. **Reload Nginx:**
   ```bash
   sudo systemctl reload nginx
   ```

4. **Clear Browser Cache:**
   - กด Ctrl+F5 (Windows/Linux) หรือ Cmd+Shift+R (Mac)

### ปัญหา: Service ไม่สามารถ Start ได้

**อาการ:**
- คลิกปุ่ม Start แล้ว service ยังไม่ทำงาน
- แสดง error message

**วิธีแก้ไข:**

1. **ตรวจสอบ Logs:**
   ```bash
   sudo journalctl -u SERVICE_NAME.service -n 50
   ```

2. **ตรวจสอบ Configuration:**
   ```bash
   sudo systemctl cat SERVICE_NAME.service
   ```

3. **ตรวจสอบ Permissions:**
   ```bash
   ls -la /etc/systemd/system/SERVICE_NAME.service
   ```

4. **ทดสอบ Start โดยตรง:**
   ```bash
   sudo systemctl start SERVICE_NAME.service
   sudo systemctl status SERVICE_NAME.service
   ```

### ปัญหา: ไม่สามารถเชื่อมต่อ WebSocket ได้

**อาการ:**
- WebSocket connection failed
- Connection timeout

**วิธีแก้ไข:**

1. **ตรวจสอบ Firewall:**
   ```bash
   sudo ufw status
   sudo ufw allow 3001/tcp
   ```

2. **ตรวจสอบ Service Status:**
   ```bash
   systemctl status websocket.service
   ```

3. **ตรวจสอบ Port:**
   ```bash
   ss -tulpn | grep 3001
   ```

4. **ตรวจสอบ Logs:**
   ```bash
   sudo journalctl -u websocket.service -f
   ```

5. **ทดสอบเชื่อมต่อ:**
   ```bash
   telnet lprserver.tail605477.ts.net 3001
   ```

### ปัญหา: ไม่สามารถเชื่อมต่อ MQTT ได้

**อาการ:**
- MQTT connection failed
- Connection refused

**วิธีแก้ไข:**

1. **ตรวจสอบ Firewall:**
   ```bash
   sudo ufw status
   sudo ufw allow 1883/tcp
   ```

2. **ตรวจสอบ Service Status:**
   ```bash
   systemctl status mqtt.service
   systemctl status aicamera-mqtt.service
   ```

3. **ตรวจสอบ Port:**
   ```bash
   ss -tulpn | grep 1883
   ```

4. **ตรวจสอบ Mosquitto Config:**
   ```bash
   sudo cat /etc/mosquitto/conf.d/aicamera.conf
   ```

5. **ทดสอบเชื่อมต่อ:**
   ```bash
   mosquitto_pub -h lprserver.tail605477.ts.net -p 1883 -t "test" -m "test"
   ```

### ปัญหา: API ไม่ตอบสนอง

**อาการ:**
- Dashboard แสดง "ไม่สามารถเชื่อมต่อได้"
- API calls ล้มเหลว

**วิธีแก้ไข:**

1. **ตรวจสอบ Dashboard Service:**
   ```bash
   systemctl status dashboard.service
   ```

2. **ตรวจสอบ API Endpoint:**
   ```bash
   curl http://localhost:5000/api/health
   curl http://lprserver.tail605477.ts.net/dashboard/api/health
   ```

3. **ตรวจสอบ Nginx Config:**
   ```bash
   sudo nginx -t
   ```

4. **ตรวจสอบ Logs:**
   ```bash
   sudo journalctl -u dashboard.service -f
   ```

### ปัญหา: Configuration ไม่สามารถบันทึกได้

**อาการ:**
- คลิกบันทึกแล้วไม่สำเร็จ
- แสดง error message

**วิธีแก้ไข:**

1. **ตรวจสอบ Permissions:**
   ```bash
   ls -la /etc/systemd/system/SERVICE_NAME.service
   ```

2. **ตรวจสอบ Sudoers:**
   ```bash
   sudo visudo -f /etc/sudoers.d/dashboard
   ```

3. **ตรวจสอบ Logs:**
   ```bash
   sudo journalctl -u dashboard.service -n 50
   ```

---

## FAQ

### Q: Dashboard auto-refresh ทุกกี่วินาที?

**A:** Dashboard จะ auto-refresh ทุก 5 วินาทีอัตโนมัติ

### Q: ต้องใช้สิทธิ์ sudo เพื่อควบคุม services หรือไม่?

**A:** ใช่ ต้องตั้งค่า sudoers เพื่อให้ dashboard สามารถควบคุม systemd services ได้

### Q: สามารถเข้าถึง Dashboard จากเครือข่ายภายนอกได้หรือไม่?

**A:** ได้ ผ่าน nginx ที่ port 80 แต่ควรตั้งค่า firewall และ authentication เพิ่มเติม

### Q: Storage path ควรตั้งค่าอย่างไร?

**A:** ควรเป็น absolute path และ user ที่รัน service ต้องมีสิทธิ์อ่าน/เขียน

### Q: Logs แสดงกี่บรรทัด?

**A:** สามารถเลือกได้ 50, 100, 200, หรือ 500 บรรทัด

### Q: Configuration backup อยู่ที่ไหน?

**A:** Backup จะถูกสร้างที่ `CONFIG_PATH.backup` ก่อนการแก้ไข

### Q: Service restart ใช้เวลานานแค่ไหน?

**A:** ขึ้นอยู่กับ service แต่โดยทั่วไปใช้เวลา 5-10 วินาที

### Q: สามารถใช้ Dashboard ควบคุม services อื่นได้หรือไม่?

**A:** ได้ แต่ต้องแก้ไขโค้ดใน `app.py` เพื่อเพิ่ม services ใหม่

### Q: WebSocket และ MQTT ต่างกันอย่างไร?

**A:** 
- **WebSocket:** เหมาะสำหรับการสื่อสารแบบ Real-time, Bi-directional, Low latency
- **MQTT:** เหมาะสำหรับ IoT devices, Publish/Subscribe pattern, Lightweight protocol

### Q: ควรใช้ WebSocket หรือ MQTT สำหรับ AI Camera?

**A:** 
- ใช้ **WebSocket** สำหรับการส่งภาพแบบ Real-time streaming
- ใช้ **MQTT** สำหรับการส่งข้อมูล sensor, commands, และ metadata

### Q: Port 1883 ถูกใช้โดย service ไหน?

**A:** Port 1883 ถูกใช้โดย **AI Camera MQTT Broker (Mosquitto)** ซึ่งเป็น MQTT broker หลัก

### Q: Storage path ควรเก็บไฟล์อะไร?

**A:** ควรเก็บ:
- ภาพที่ capture จาก cameras
- Log files
- Configuration backups
- Temporary files

### Q: Configuration backup ถูกเก็บไว้กี่วัน?

**A:** Backup files จะไม่ถูกลบอัตโนมัติ ควรทำการ cleanup เองเป็นระยะ

---

## สรุป

Dashboard นี้เป็นเครื่องมือที่ช่วยให้การจัดการ AI Camera Services ง่ายขึ้น โดยมีฟีเจอร์ครบถ้วนสำหรับการควบคุมและตรวจสอบสถานะ services

สำหรับคำถามเพิ่มเติมหรือรายงานปัญหา กรุณาติดต่อทีมพัฒนา

---

**เวอร์ชัน:** 1.0  
**อัปเดตล่าสุด:** 2026-02-16

