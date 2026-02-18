# Quick Start Guide - AI Camera Services Dashboard

## การเริ่มต้นใช้งานอย่างรวดเร็ว

### 1. เข้าถึง Dashboard

เปิดเบราว์เซอร์และไปที่:
```
http://lprserver.tail605477.ts.net/dashboard/
```

### 2. ตรวจสอบสถานะ Services

Dashboard จะแสดงสถานะของ 3 services:
- 🟢 **WebSocket Service** (Port 3001)
- 🟢 **MQTT Microservice** 
- 🟢 **AI Camera MQTT Broker** (Port 1883)

### 3. ทดสอบการเชื่อมต่อ

#### WebSocket (Port 3001)
```bash
# ใช้ wscat
wscat -c ws://lprserver.tail605477.ts.net:3001

# หรือใช้ Browser Console
const ws = new WebSocket('ws://lprserver.tail605477.ts.net:3001');
ws.onopen = () => console.log('Connected!');
```

#### MQTT (Port 1883)
```bash
# Subscribe
mosquitto_sub -h lprserver.tail605477.ts.net -p 1883 -t "aicamera/#" -v

# Publish
mosquitto_pub -h lprserver.tail605477.ts.net -p 1883 -t "aicamera/test" -m "Hello"
```

### 4. การควบคุม Services

- **Start:** คลิกปุ่ม ▶ เริ่ม
- **Stop:** คลิกปุ่ม ⏹ หยุด
- **Restart:** คลิกปุ่ม 🔄 รีสตาร์ท

### 5. ดู Logs

คลิกปุ่ม **📋 Logs** เพื่อดู logs ของแต่ละ service

---

## Troubleshooting อย่างรวดเร็ว

### Dashboard ไม่แสดง
```bash
systemctl status dashboard.service
sudo systemctl restart dashboard.service
```

### Static files ไม่โหลด
```bash
sudo nginx -t
sudo systemctl reload nginx
# แล้วกด Ctrl+F5 ในเบราว์เซอร์
```

### Service ไม่สามารถ Start
```bash
sudo journalctl -u SERVICE_NAME.service -n 50
sudo journalctl -u websocket.service -n 50
sudo journalctl -u aicamera-mqtt.service -n 50
```

### ไม่สามารถเชื่อมต่อ WebSocket/MQTT
```bash
# ตรวจสอบ firewall
sudo ufw status
sudo ufw allow 3001/tcp  # WebSocket
sudo ufw allow 1883/tcp  # MQTT

# ตรวจสอบ service
systemctl status websocket.service
systemctl status aicamera-mqtt.service
```

---

## ตัวอย่างโค้ดสำหรับลูกข่าย

### WebSocket Client (JavaScript)
```javascript
const ws = new WebSocket('ws://lprserver.tail605477.ts.net:3001');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Received:', e.data);
ws.send('Hello Server');
```

### MQTT Client (Python)
```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("lprserver.tail605477.ts.net", 1883, 60)
client.publish("aicamera/test", "Hello")
client.subscribe("aicamera/#")
client.loop_forever()
```

---

สำหรับรายละเอียดเพิ่มเติม ดูที่ [USER_GUIDE.md](USER_GUIDE.md)

