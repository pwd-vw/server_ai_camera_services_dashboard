# แผนพัฒนา Edge Client Connection Services

แผนการเขียน Service สำหรับการเชื่อมต่อจากลูกข่าย (Edge/Client) ในการสื่อสาร รับ-ส่งข้อมูล แยกแต่ละ Service และพัฒนาทีละ Service พร้อม Dashboard แสดงสถานะการเชื่อมต่อและ Log

---

## 1. ภาพรวมความต้องการ

| รายการ | รายละเอียด |
|--------|-------------|
| **จุดประสงค์** | ให้เครื่องลูกข่าย (Edge/Client) เชื่อมต่อกับ Server เพื่อรับ-ส่งข้อมูล |
| **แนวทาง** | แยก Service ตามโปรโตคอล/หน้าที่ พัฒนาทีละ Service |
| **Client Dashboard** | แสดงสถานะการเชื่อมต่อ + Log (วันเวลา, title ของข้อมูลที่ส่ง) |

---

## 2. สถาปัตยกรรมภาพรวม

```
                    ┌─────────────────────────────────────────┐
                    │           Server (Central)               │
                    │  REST API │ WebSocket │ MQTT Broker     │
                    └─────────────────┬───────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│ Edge Client 1 │           │ Edge Client 2 │           │ Edge Client N │
│ ┌───────────┐ │           │ ┌───────────┐ │           │ ┌───────────┐ │
│ │Dashboard  │ │           │ │Dashboard  │ │           │ │Dashboard  │ │
│ │- สถานะ    │ │           │ │- สถานะ    │ │           │ │- สถานะ    │ │
│ │- Log      │ │           │ │- Log      │ │           │ │- Log      │ │
│ └───────────┘ │           │ └───────────┘ │           │ └───────────┘ │
│ Connection    │           │ Connection    │           │ Connection    │
│ Services      │           │ Services      │           │ Services      │
└───────────────┘           └───────────────┘           └───────────────┘
```

---

## 3. การแยก Service ฝั่งลูกข่าย (Edge Client)

แยกตามโปรโตคอลและหน้าที่ ไม่ผูกกัน เพื่อพัฒนาทีละตัว:

| ลำดับ | Service | หน้าที่ | โปรโตคอล | พัฒนาก่อน/หลัง |
|-------|---------|--------|----------|----------------|
| **1** | **Connection Status Service** | ตรวจสอบและรายงานสถานะการเชื่อมต่อของทุกช่องทาง | - | ตัวแรก (ใช้ร่วมกับทุกตัว) |
| **2** | **REST Client Service** | ส่ง/รับข้อมูลแบบ Request-Response (CRUD, config, reports) | HTTP/HTTPS | ตัวที่ 2 |
| **3** | **WebSocket Client Service** | ส่ง/รับแบบ Real-time (stream, แจ้งเตือน, คำสั่ง) | WebSocket | ตัวที่ 3 |
| **4** | **MQTT Client Service** | Publish/Subscribe ข้อความ (metadata, events, commands) | MQTT | ตัวที่ 4 |
| **5** | **Client Log Service** | รวบรวมและจัดเก็บ Log (วันเวลา + title) สำหรับแสดงบน Dashboard | Internal | คู่กับ Dashboard |

---

## 4. รายละเอียดแต่ละ Service

### 4.1 Connection Status Service (พัฒนาตัวแรก)

**หน้าที่**

- ตรวจสอบว่า REST / WebSocket / MQTT เชื่อมต่อได้หรือไม่
- รายงานสถานะต่อ Dashboard (connected / disconnected / error)
- รองรับการ reconnect / backoff ตามนโยบาย

**ข้อมูลออก (สำหรับ Dashboard)**

- `rest: connected | disconnected | error`
- `websocket: connected | disconnected | reconnecting | error`
- `mqtt: connected | disconnected | error`
- `last_updated`: เวลา

**พัฒนาทีละขั้น**

1. กำหนด interface สถานะ (เช่น enum/struct) และฟังก์ชัน `get_connection_status()`.
2. เริ่มจาก REST เท่านั้น (ping/health endpoint) แล้วรายงานสถานะ.
3. เพิ่ม WebSocket (เชื่อมต่อแล้วถือว่า connected).
4. เพิ่ม MQTT (เชื่อมต่อกับ broker แล้วถือว่า connected).
5. เพิ่ม retry/reconnect logic และอัปเดตสถานะให้ Dashboard อ่านได้ (ในหน่วยความจำหรือไฟล์).

---

### 4.2 REST Client Service (พัฒนาตัวที่ 2)

**หน้าที่**

- ส่ง HTTP request ไปยัง Server (GET/POST/PUT/DELETE)
- รับ response และส่งต่อให้ส่วนอื่นของระบบ
- รองรับ config (base URL, timeout, headers)

**ข้อมูลที่ส่ง (ตัวอย่าง)**

- รายการที่ส่ง: config, events, reports, สถิติ
- แต่ละครั้งที่ส่งสำเร็จ/ไม่สำเร็จ ควรบันทึก Log (วันเวลา + title) ผ่าน Client Log Service

**พัฒนาทีละขั้น**

1. โมดูลเรียก HTTP เท่านั้น (เช่น `requests` หรือ `fetch`) ต่อ base URL จาก config.
2. ฟังก์ชันส่งข้อมูลหลัก เช่น `send_event(title, payload)`, `upload_report(title, data)`.
3. ผูกกับ Connection Status Service: อัปเดตสถานะ REST ตามผลการเรียก.
4. ผูกกับ Client Log Service: บันทึกแต่ละครั้งที่ส่ง (วันเวลา + title).

---

### 4.3 WebSocket Client Service (พัฒนาตัวที่ 3)

**หน้าที่**

- เชื่อมต่อ WebSocket กับ Server (ws/wss)
- ส่งข้อความ (เช่น frame, event, command)
- รับข้อความและส่งต่อให้แอปหรือ Log

**ข้อมูลที่ส่ง (ตัวอย่าง)**

- ประเภท: frame, event, command, ping/pong
- แต่ละการส่งที่สำคัญ ควรมี title (เช่น "frame", "event:alarm") และบันทึกใน Log

**พัฒนาทีละขั้น**

1. เชื่อมต่อ WebSocket และรักษา connection (reconnect เมื่อหลุด).
2. ฟังก์ชันส่ง เช่น `send(type, payload)` หรือ `send_with_title(title, data)`.
3. ผูกกับ Connection Status Service: อัปเดตสถานะ WebSocket.
4. ผูกกับ Client Log Service: บันทึกการส่งสำคัญ (วันเวลา + title).

---

### 4.4 MQTT Client Service (พัฒนาตัวที่ 4)

**หน้าที่**

- เชื่อมต่อ MQTT Broker (port 1883)
- Publish ข้อความไปยัง topic ที่กำหนด
- Subscribe topic ที่ต้องการรับ (commands, config)

**ข้อมูลที่ส่ง (ตัวอย่าง)**

- Topic เช่น `aicamera/{client_id}/events`, `aicamera/{client_id}/metadata`
- Payload เป็น JSON หรือ binary ตามข้อกำหนด
- แต่ละ Publish ที่สำคัญ ควรมี title (หรือ derived จาก topic) และบันทึกใน Log

**พัฒนาทีละขั้น**

1. เชื่อมต่อ MQTT และรักษา connection (reconnect).
2. ฟังก์ชัน `publish(topic, payload)` และ `subscribe(topic, callback)`.
3. ผูกกับ Connection Status Service: อัปเดตสถานะ MQTT.
4. ผูกกับ Client Log Service: บันทึกการส่ง/รับสำคัญ (วันเวลา + title).

---

### 4.5 Client Log Service (พัฒนาคู่กับ Dashboard)

**หน้าที่**

- รับเหตุการณ์จาก REST / WebSocket / MQTT Client Services
- จัดเก็บ Log แต่ละรายการ: **วันเวลา** + **title** (และถ้าต้องการ: type, success/error)
- ให้ API หรือ in-memory store สำหรับ Dashboard ดึงรายการล่าสุด

**รูปแบบ Log (ขั้นต่ำ)**

- `timestamp`: วันเวลา (ISO หรือ Unix ms)
- `title`: ชื่อ/หัวข้อของข้อมูลที่ส่ง (หรือประเภทเหตุการณ์)
- (ถ้าต้องการ) `type`: rest | websocket | mqtt
- (ถ้าต้องการ) `direction`: send | receive
- (ถ้าต้องการ) `success`: true | false

**พัฒนาทีละขั้น**

1. โครงสร้างข้อมูลในหน่วยความจำ (เช่น list ของ dict หรือ class LogEntry) จำกัดจำนวนรายการ (เช่น 500 รายการล่าสุด).
2. ฟังก์ชัน `append_log(timestamp, title, **kwargs)`.
3. ฟังก์ชัน `get_logs(limit, since)` สำหรับ Dashboard.
4. (ถ้าต้องการ) เขียนลงไฟล์หรือ SQLite เพื่อ persist หลังรีสตาร์ท.

---

## 5. Client Dashboard (ฝั่งลูกข่าย)

Dashboard ทำงานบนเครื่องลูกข่าย (Edge) เพื่อแสดงสถานะและ Log โดยไม่พึ่ง Server เป็นหลัก (อาจดึง config จาก Server ก็ได้)

### 5.1 สิ่งที่ต้องแสดง

| ส่วน | รายละเอียด |
|------|-------------|
| **สถานะการเชื่อมต่อ** | REST / WebSocket / MQTT แต่ละตัว: connected / disconnected / reconnecting / error (สี/ไอคอน) |
| **Log** | ตารางหรือรายการ: **วันเวลา** และ **title** ของข้อมูลที่ส่ง (และถ้ามี: type, direction, success) |

### 5.2 แนวทางพัฒนา Dashboard

- **ตัวเลือก A:** หน้าเว็บ (HTML/JS) ฝั่ง Client ที่เรียก API ของตัว Client เอง (เช่น Flask/FastAPI เล็กๆ บน Edge หรือ static + backend script).
- **ตัวเลือก B:** แอป desktop/minimal UI (เช่น Electron, Tkinter, Qt) อ่านสถานะและ Log จาก Connection Status Service + Client Log Service.

**API ที่ Dashboard ต้องใช้ (ฝั่ง Client)**

- `GET /api/connection-status` → สถานะ REST / WebSocket / MQTT
- `GET /api/logs?limit=100` → รายการ Log (วันเวลา, title, ...)

ทั้งสอง endpoint นี้ implement ในโปรเจกต์ฝั่ง Edge (ไม่ใช่ Server เดิมของ AI Camera).

---

## 6. ลำดับการพัฒนาทีละ Service (สรุป)

| Phase | Service | ผลลัพธ์ที่ได้ |
|-------|---------|----------------|
| **1** | Client Log Service + โครงสร้าง Connection Status | โครง Log และรูปแบบสถานะ พร้อมฟังก์ชันให้บริการ |
| **2** | Connection Status Service | ดึงสถานะ REST/WS/MQTT ได้ (เริ่มจาก REST อย่างเดียวก็ได้) |
| **3** | Dashboard ขั้นต่ำ | หน้าแสดงสถานะ + แสดง Log (วันเวลา, title) |
| **4** | REST Client Service | ส่งข้อมูลผ่าน HTTP ได้ + อัปเดตสถานะ + บันทึก Log |
| **5** | WebSocket Client Service | ส่ง/รับผ่าน WebSocket ได้ + อัปเดตสถานะ + บันทึก Log |
| **6** | MQTT Client Service | Publish/Subscribe MQTT ได้ + อัปเดตสถานะ + บันทึก Log |
| **7** | ปรับปรุง Dashboard | กรอง Log ตาม type, เวลา, ค้นหา title |

---

## 7. โครงสร้างโฟลเดอร์แนะนำ (ฝั่ง Edge Client)

```
edge-client/
├── README.md
├── requirements.txt          # Python: requests, paho-mqtt, websocket-client, flask
├── config/
│   └── client_config.json    # server URL, MQTT broker, client_id
├── services/
│   ├── connection_status.py # Connection Status Service
│   ├── rest_client.py       # REST Client Service
│   ├── websocket_client.py  # WebSocket Client Service
│   ├── mqtt_client.py       # MQTT Client Service
│   └── client_log.py       # Client Log Service
├── dashboard/                # Dashboard ฝั่ง Client
│   ├── app.py               # Flask/FastAPI เล็กๆ สำหรับ API สถานะ + Log
│   └── static/
│       ├── index.html
│       ├── app.js
│       └── style.css
└── main.py                  # เริ่มทุก service + Dashboard (ถ้าใช้)
```

---

## 8. รายละเอียดการเชื่อมต่อและ Config (สำหรับพัฒนาบน Repo/Machine ลูกข่าย)

ส่วนนี้กำหนด **URL, Authentication, Config** ของแต่ละ Service เพื่อให้นำไปใช้พัฒนาบน Repository หรือเครื่องลูกข่าย (Edge) ได้โดยตรง

### 8.1 โครงสร้าง Config ร่วม (Config File + Environment)

ใช้ได้ทั้ง **ไฟล์ config** และ **ตัวแปรสภาพแวดล้อม (Environment)** โดยค่าจาก env จะ override ค่าในไฟล์ (เหมาะกับ deployment หลายเครื่อง)

**ตำแหน่ง config ที่แนะนำ**

- ไฟล์: `config/client_config.json` หรือ `config/client_config.yaml`
- Environment: `.env` ในโฟลเดอร์โปรเจกต์ (ไม่ commit ลง git) หรือ systemd `Environment=` / systemd `EnvironmentFile=`

---

### 8.2 REST Client Service — การเชื่อมต่อและ Config

| รายการ | รายละเอียด | ตัวอย่างค่า | หมายเหตุ |
|--------|-------------|-------------|----------|
| **Base URL** | โปรโตคอล + host + port (ไม่รวม path) | `http://lprserver.tail605477.ts.net:3000` หรือ `https://api.example.com` | บังคับ |
| **Health/ Ping endpoint** | path สำหรับตรวจสอบสถานะ | `/api/health` หรือ `/health` | ใช้สำหรับ Connection Status |
| **Timeout (วินาที)** | timeout ต่อ request | `10` | เลือกได้ |
| **Authentication** | ไม่มี / Bearer / Basic / API-Key | ดูตารางด้านล่าง | เลือกได้ |
| **Headers เพิ่มเติม** | คู่ key-value สำหรับทุก request | `X-Client-ID`, `X-Device-Type` | เลือกได้ |

**รูปแบบ Authentication (REST)**

| ประเภท | Config key | ตัวอย่างค่า | วิธีส่ง |
|--------|------------|-------------|--------|
| ไม่ใช้ | - | - | - |
| Bearer Token | `rest.auth.bearer_token` หรือ env `REST_BEARER_TOKEN` | `eyJhbGc...` | Header: `Authorization: Bearer <token>` |
| Basic | `rest.auth.username`, `rest.auth.password` หรือ env `REST_USERNAME`, `REST_PASSWORD` | `client01`, `secret` | Header: `Authorization: Basic <base64(user:pass)>` |
| API Key | `rest.auth.api_key` และ `rest.auth.api_key_header` หรือ env `REST_API_KEY`, `REST_API_KEY_HEADER` | `abc123`, `X-API-Key` | Header: `<api_key_header>: <api_key>` |

**โครงสร้าง Config (JSON) — REST**

```json
{
  "rest": {
    "base_url": "http://lprserver.tail605477.ts.net:3000",
    "health_path": "/api/health",
    "timeout_seconds": 10,
    "auth": {
      "type": "none",
      "bearer_token": null,
      "username": null,
      "password": null,
      "api_key": null,
      "api_key_header": "X-API-Key"
    },
    "headers": {
      "X-Client-ID": "${client_id}",
      "User-Agent": "EdgeClient/1.0"
    }
  }
}
```

**ตัวแปร Environment — REST**

| ชื่อตัวแปร | ความหมาย | ตัวอย่าง |
|------------|----------|----------|
| `REST_BASE_URL` | Base URL ของ REST API | `http://lprserver.tail605477.ts.net:3000` |
| `REST_HEALTH_PATH` | Path สำหรับ health check | `/api/health` |
| `REST_TIMEOUT` | Timeout (วินาที) | `10` |
| `REST_BEARER_TOKEN` | Bearer token (ถ้าใช้) | `eyJhbGc...` |
| `REST_USERNAME` | Basic auth username | `client01` |
| `REST_PASSWORD` | Basic auth password | `secret` |
| `REST_API_KEY` | API Key (ถ้าใช้) | `abc123` |
| `REST_API_KEY_HEADER` | ชื่อ header ของ API Key | `X-API-Key` |

---

### 8.3 WebSocket Client Service — การเชื่อมต่อและ Config

| รายการ | รายละเอียด | ตัวอย่างค่า | หมายเหตุ |
|--------|-------------|-------------|----------|
| **URL** | WebSocket endpoint เต็ม | `ws://lprserver.tail605477.ts.net:3001` หรือ `wss://...` | บังคับ |
| **Protocol** | ws หรือ wss | `wss` ถ้ามี TLS | แนะนำใช้ wss ใน production |
| **Reconnect** | เปิด/ปิด auto reconnect | `true` | เลือกได้ |
| **Reconnect interval (วินาที)** | ช่วงเวลาก่อน reconnect | `5` | เลือกได้ |
| **Ping interval (วินาที)** | ส่ง ping เพื่อรักษา connection | `30` | เลือกได้ |
| **Authentication** | ไม่มี / Query string / Header (ถ้า Server รองรับ) | ดูตารางด้านล่าง | ขึ้นกับ Server |

**รูปแบบ Authentication (WebSocket)**

| ประเภท | Config key | ตัวอย่าง | วิธีส่ง |
|--------|------------|----------|--------|
| ไม่ใช้ | - | - | - |
| Query string | `websocket.auth.query_token` หรือ env `WS_AUTH_QUERY` | `token=abc123` | เพิ่มใน URL: `ws://host:3001?token=abc123` |
| Header | บาง Server รองรับ custom header ตอน handshake (ขึ้นกับ library) | - | กำหนดใน client library |

**โครงสร้าง Config (JSON) — WebSocket**

```json
{
  "websocket": {
    "url": "ws://lprserver.tail605477.ts.net:3001",
    "use_tls": false,
    "reconnect": true,
    "reconnect_interval_seconds": 5,
    "ping_interval_seconds": 30,
    "auth": {
      "type": "none",
      "query_token": null
    }
  }
}
```

**ตัวแปร Environment — WebSocket**

| ชื่อตัวแปร | ความหมาย | ตัวอย่าง |
|------------|----------|----------|
| `WS_URL` | WebSocket URL เต็ม | `ws://lprserver.tail605477.ts.net:3001` |
| `WS_USE_TLS` | ใช้ wss หรือไม่ (true/false) | `false` |
| `WS_RECONNECT` | เปิด auto reconnect | `true` |
| `WS_RECONNECT_INTERVAL` | วินาทีก่อน reconnect | `5` |
| `WS_PING_INTERVAL` | วินาทีระหว่าง ping | `30` |
| `WS_AUTH_QUERY` | ค่า query string สำหรับ auth (เช่น token=xxx) | `token=abc123` |

---

### 8.4 MQTT Client Service — การเชื่อมต่อและ Config

| รายการ | รายละเอียด | ตัวอย่างค่า | หมายเหตุ |
|--------|-------------|-------------|----------|
| **Host** | hostname หรือ IP ของ MQTT Broker | `lprserver.tail605477.ts.net` | บังคับ |
| **Port** | พอร์ต MQTT | `1883` (ไม่ใช้ TLS), `8883` (TLS) | บังคับ |
| **Client ID** | รหัส client ไม่ซ้ำต่อ broker | `edge_camera_001` หรือ `${client_id}` | บังคับ |
| **Username / Password** | ถ้า Broker เปิดใช้ | ตามที่ Server กำหนด | เลือกได้ |
| **TLS** | ใช้ TLS หรือไม่ | `false` / `true` | เลือกได้ |
| **Keep Alive (วินาที)** | MQTT keep alive | `60` | เลือกได้ |
| **Topic prefix** | prefix ของ topic ที่ใช้ | `aicamera` | ใช้สร้าง topic เช่น `aicamera/{client_id}/events` |
| **QoS** | 0, 1 หรือ 2 | `1` | เลือกได้ |

**Topic ที่ใช้ (ตาม SERVICES_ARCHITECTURE / USER_GUIDE)**

| วัตถุประสงค์ | Topic pattern | ทิศทาง |
|--------------|----------------|--------|
| ส่ง metadata | `aicamera/{client_id}/metadata` | Publish |
| ส่ง events | `aicamera/{client_id}/events` | Publish |
| ส่ง detections | `aicamera/{client_id}/detections` | Publish |
| รับ commands | `aicamera/{client_id}/commands` | Subscribe |

**โครงสร้าง Config (JSON) — MQTT**

```json
{
  "mqtt": {
    "host": "lprserver.tail605477.ts.net",
    "port": 1883,
    "client_id": "edge_camera_001",
    "username": null,
    "password": null,
    "use_tls": false,
    "keep_alive_seconds": 60,
    "topic_prefix": "aicamera",
    "default_qos": 1,
    "subscribe_topics": [
      "aicamera/edge_camera_001/commands"
    ],
    "publish_topics": {
      "metadata": "aicamera/edge_camera_001/metadata",
      "events": "aicamera/edge_camera_001/events",
      "detections": "aicamera/edge_camera_001/detections"
    }
  }
}
```

**ตัวแปร Environment — MQTT**

| ชื่อตัวแปร | ความหมาย | ตัวอย่าง |
|------------|----------|----------|
| `MQTT_HOST` | Broker host | `lprserver.tail605477.ts.net` |
| `MQTT_PORT` | Broker port | `1883` |
| `MQTT_CLIENT_ID` | Client ID | `edge_camera_001` |
| `MQTT_USERNAME` | Username (ถ้ามี) | `device_user` |
| `MQTT_PASSWORD` | Password (ถ้ามี) | `secret` |
| `MQTT_USE_TLS` | ใช้ TLS | `false` |
| `MQTT_KEEP_ALIVE` | Keep alive (วินาที) | `60` |
| `MQTT_TOPIC_PREFIX` | Topic prefix | `aicamera` |

---

### 8.5 Connection Status Service — Config

| รายการ | รายละเอียด | ตัวอย่างค่า |
|--------|-------------|-------------|
| **Check interval (วินาที)** | ช่วงเวลาตรวจสอบสถานะแต่ละช่องทาง | `10` |
| **REST / WebSocket / MQTT** | ใช้ค่าจาก config ของแต่ละ Service ข้างต้น | - |

ไม่ต้องมี URL หรือ auth แยก — อ่านจาก REST, WebSocket, MQTT config แล้วใช้ health check / connection state ตามนั้น

---

### 8.6 Client Log Service — Config

| รายการ | รายละเอียด | ตัวอย่างค่า |
|--------|-------------|-------------|
| **Max entries in memory** | จำนวนรายการ Log สูงสุดในหน่วยความจำ | `500` |
| **Persist to file** | บันทึกลงไฟล์หรือไม่ | `true` |
| **Log file path** | path ไฟล์ log (ฝั่งลูกข่าย) | `./data/edge_client.log` หรือ `/var/log/edge-client/events.log` |
| **Log format** | รูปแบบแต่ละบรรทัด | `%(timestamp)s | %(title)s | %(type)s` |

---

### 8.7 ไฟล์ Config ตัวอย่างสำหรับ Repo/Machine ลูกข่าย

**ไฟล์: `config/client_config.json` (ตัวอย่างเต็ม)**

```json
{
  "client_id": "edge_camera_001",
  "rest": {
    "base_url": "http://lprserver.tail605477.ts.net:3000",
    "health_path": "/api/health",
    "timeout_seconds": 10,
    "auth": { "type": "none" },
    "headers": { "X-Client-ID": "edge_camera_001" }
  },
  "websocket": {
    "url": "ws://lprserver.tail605477.ts.net:3001",
    "use_tls": false,
    "reconnect": true,
    "reconnect_interval_seconds": 5,
    "ping_interval_seconds": 30,
    "auth": { "type": "none" }
  },
  "mqtt": {
    "host": "lprserver.tail605477.ts.net",
    "port": 1883,
    "client_id": "edge_camera_001",
    "username": null,
    "password": null,
    "use_tls": false,
    "keep_alive_seconds": 60,
    "topic_prefix": "aicamera",
    "default_qos": 1,
    "subscribe_topics": ["aicamera/edge_camera_001/commands"],
    "publish_topics": {
      "metadata": "aicamera/edge_camera_001/metadata",
      "events": "aicamera/edge_camera_001/events",
      "detections": "aicamera/edge_camera_001/detections"
    }
  },
  "connection_status": {
    "check_interval_seconds": 10
  },
  "client_log": {
    "max_entries": 500,
    "persist_to_file": true,
    "log_file_path": "./data/edge_client.log"
  }
}
```

**ไฟล์: `.env.example` (สำหรับ copy ไปใช้บนเครื่องลูกข่าย)**

```bash
# Client identity
CLIENT_ID=edge_camera_001

# REST API
REST_BASE_URL=http://lprserver.tail605477.ts.net:3000
REST_HEALTH_PATH=/api/health
REST_TIMEOUT=10
# REST_BEARER_TOKEN=
# REST_USERNAME=
# REST_PASSWORD=
# REST_API_KEY=
# REST_API_KEY_HEADER=X-API-Key

# WebSocket
WS_URL=ws://lprserver.tail605477.ts.net:3001
WS_USE_TLS=false
WS_RECONNECT=true
WS_RECONNECT_INTERVAL=5
WS_PING_INTERVAL=30
# WS_AUTH_QUERY=token=xxx

# MQTT
MQTT_HOST=lprserver.tail605477.ts.net
MQTT_PORT=1883
MQTT_CLIENT_ID=edge_camera_001
# MQTT_USERNAME=
# MQTT_PASSWORD=
MQTT_USE_TLS=false
MQTT_KEEP_ALIVE=60
MQTT_TOPIC_PREFIX=aicamera

# Connection status
CONNECTION_CHECK_INTERVAL=10

# Client log
LOG_MAX_ENTRIES=500
LOG_PERSIST_TO_FILE=true
LOG_FILE_PATH=./data/edge_client.log
```

**หมายเหตุการ deploy บนเครื่องลูกข่าย**

- Copy `.env.example` เป็น `.env` แล้วแก้ค่า (host, client_id, password ฯลฯ) ตามเครื่อง
- ใส่ `.env` ใน `.gitignore` ไม่ commit ค่าจริง
- ถ้ารันด้วย systemd ใช้ `EnvironmentFile=/path/to/edge-client/.env` ได้

---

### 8.8 สรุปพอร์ตและ Endpoint ฝั่ง Server (อ้างอิง)

| Service | Protocol | Port | Endpoint / การเชื่อมต่อ |
|---------|----------|------|--------------------------|
| REST API | HTTP/HTTPS | 3000 | `{base_url}/api/...` เช่น `/api/health`, `/api/cameras` |
| WebSocket | ws/wss | 3001 | `ws://{host}:3001` หรือ `wss://{host}:3001` |
| MQTT Broker | MQTT | 1883 (TLS: 8883) | `{host}:1883` |

ค่า `{host}` ใช้จาก config (เช่น `lprserver.tail605477.ts.net` หรือ IP/Domain ของ Server จริง)

---

## 9. ขั้นตอนถัดไป (Next Steps)

1. สร้าง repo/โฟลเดอร์ `edge-client` และไฟล์ config ตัวอย่าง
2. **Phase 1:** Implement Client Log Service + โครง Connection Status
3. **Phase 2:** Implement Connection Status (เริ่มจาก REST health check)
4. **Phase 3:** ทำ Dashboard ขั้นต่ำ (สถานะ + Log)
5. **Phase 4–6:** ทำ REST → WebSocket → MQTT Client ทีละตัว แล้วผูกกับ Status + Log
6. ทดสอบกับ Server จริง (REST API, WebSocket, MQTT Broker) ตาม `SERVICES_ARCHITECTURE.md`

เมื่อต้องการเริ่ม Phase ใด บอกหมายเลข Phase หรือชื่อ Service ได้ จะช่วยลงรายละเอียดหรือเขียนโค้ดตัวอย่างให้ได้ทีละส่วน

---

**การนำไปใช้บน Repository / Machine ลูกข่าย:**  
ใช้ค่าจาก **Section 8** (รายละเอียดการเชื่อมต่อและ Config) ในการสร้าง `config/client_config.json` และ `.env` บน Repo หรือเครื่องลูกข่าย โดยแทนที่ host, client_id และค่าอื่นๆ ตาม environment จริง
