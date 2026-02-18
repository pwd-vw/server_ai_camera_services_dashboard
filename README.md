# AI Camera Services Dashboard

Dashboard สำหรับควบคุมและตรวจสอบสถานะของ AI Camera Services

## Features

- ✅ แสดงสถานะของ Services ทั้ง 3 ตัว (WebSocket, MQTT Microservice, MQTT Broker)
- ✅ ควบคุมการทำงาน (Start, Stop, Restart)
- ✅ ดูและแก้ไข Configuration Files
- ✅ ดูและแก้ไข Storage Path
- ✅ ดู Logs แบบ Real-time
- ✅ Auto-refresh ทุก 5 วินาที

## Services ที่รองรับ

1. **websocket.service** - AI Camera Websocket Service
2. **mqtt.service** - AI Camera MQTT Microservice
3. **aicamera-mqtt.service** - AI Camera MQTT Broker

## การติดตั้ง

### 1. ติดตั้ง Dependencies

```bash
cd /home/devuser/edge_ai_dashboard/dashboard
pip3 install -r requirements.txt
```

### 2. ตั้งค่า Sudoers (สำหรับควบคุม systemd)

เพิ่มสิทธิ์ให้ user สามารถรัน systemctl commands โดยไม่ต้องใส่ password:

```bash
sudo visudo
```

เพิ่มบรรทัดนี้:

```
devuser ALL=(ALL) NOPASSWD: /usr/bin/systemctl start *, /usr/bin/systemctl stop *, /usr/bin/systemctl restart *, /usr/bin/systemctl show *, /usr/bin/systemctl daemon-reload, /bin/cp /tmp/service_config_update *, /bin/cp /tmp/service_env_update *
```

### 3. รัน Dashboard

#### วิธีที่ 1: รันโดยตรง

```bash
cd /home/devuser/edge_ai_dashboard/dashboard
python3 app.py
```

Dashboard จะทำงานที่: http://localhost:5000

#### วิธีที่ 2: รันเป็น Systemd Service (แนะนำ)

สร้างไฟล์ service:

```bash
sudo nano /etc/systemd/system/dashboard.service
```

เพิ่มเนื้อหานี้:

```ini
[Unit]
Description=AI Camera Services Dashboard
After=network.target

[Service]
Type=simple
User=devuser
WorkingDirectory=/home/devuser/edge_ai_dashboard/dashboard
Environment=FLASK_APP=app.py
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable และ Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
sudo systemctl status dashboard.service
```

## การใช้งาน

1. เปิดเบราว์เซอร์ไปที่: http://localhost:5000
2. Dashboard จะแสดงสถานะของ Services ทั้งหมด
3. ใช้ปุ่มต่างๆ เพื่อควบคุม Services:
   - **▶ เริ่ม** - เริ่ม service
   - **⏹ หยุด** - หยุด service
   - **🔄 รีสตาร์ท** - รีสตาร์ท service
   - **⚙️ Config** - ดูและแก้ไข configuration
   - **📁 Storage** - ดูและแก้ไข storage path
   - **📋 Logs** - ดู logs

## API Endpoints

### GET /api/services
ดึงรายการ services ทั้งหมดพร้อมสถานะ

### GET /api/services/{service_id}
ดึงข้อมูล service เฉพาะ

### POST /api/services/{service_id}/start
เริ่ม service

### POST /api/services/{service_id}/stop
หยุด service

### POST /api/services/{service_id}/restart
รีสตาร์ท service

### GET /api/services/{service_id}/logs?lines=100
ดึง logs ของ service

### GET /api/services/{service_id}/config
ดึง config ของ service

### POST /api/services/{service_id}/config
อัปเดต config ของ service

### GET /api/services/{service_id}/storage-path
ดึง storage path ของ service

### POST /api/services/{service_id}/storage-path
อัปเดต storage path ของ service

## Security Notes

⚠️ **คำเตือน**: Dashboard นี้มีสิทธิ์ควบคุม systemd services ซึ่งเป็นสิทธิ์ระดับสูง ควร:

1. จำกัดการเข้าถึงด้วย Firewall หรือ Reverse Proxy
2. เพิ่ม Authentication (ถ้าต้องการใช้งานจริง)
3. ใช้ HTTPS สำหรับการเชื่อมต่อ
4. จำกัดการเข้าถึงจาก IP ที่อนุญาตเท่านั้น

## Troubleshooting

### ไม่สามารถควบคุม service ได้

ตรวจสอบว่า:
1. User มีสิทธิ์ sudo สำหรับ systemctl commands
2. Sudoers configuration ถูกต้อง
3. Service files อยู่ในตำแหน่งที่ถูกต้อง

### Dashboard ไม่แสดงข้อมูล

ตรวจสอบว่า:
1. Flask app ทำงานอยู่
2. API endpoint ทำงานได้ (ทดสอบที่ http://localhost:5000/api/health)
3. ไม่มี firewall block port 5000

### ไม่สามารถแก้ไข config ได้

ตรวจสอบว่า:
1. User มีสิทธิ์เขียนไฟล์ config
2. Config path ถูกต้อง
3. มี backup file ถูกสร้างขึ้น

## License

MIT

