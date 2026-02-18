#!/bin/bash
# สคริปต์สำหรับอัปเดต dashboard service ให้ใช้ virtual environment

echo "=========================================="
echo "อัปเดต Dashboard Service"
echo "=========================================="
echo ""

# 1. อัปเดต service file
echo "[1/3] กำลังอัปเดต service file..."
sudo sed -i 's|ExecStart=/usr/bin/python3 app.py|ExecStart=/home/devuser/edge_ai_dashboard/dashboard/.venv/bin/python3 app.py|' /etc/systemd/system/dashboard.service

if [ $? -ne 0 ]; then
    echo "❌ ไม่สามารถอัปเดต service file ได้"
    exit 1
fi

echo "✅ อัปเดต service file สำเร็จ"
echo ""

# 2. Reload systemd
echo "[2/3] กำลัง reload systemd..."
sudo systemctl daemon-reload

if [ $? -ne 0 ]; then
    echo "❌ ไม่สามารถ reload systemd ได้"
    exit 1
fi

echo "✅ reload systemd สำเร็จ"
echo ""

# 3. Restart dashboard service
echo "[3/3] กำลัง restart dashboard service..."
sudo systemctl restart dashboard.service

if [ $? -ne 0 ]; then
    echo "❌ ไม่สามารถ restart dashboard service ได้"
    exit 1
fi

echo "✅ restart dashboard service สำเร็จ"
echo ""

# ตรวจสอบสถานะ
echo "=========================================="
echo "สถานะ Dashboard Service:"
echo "=========================================="
sudo systemctl status dashboard.service --no-pager | head -15

echo ""
echo "Port 5000:"
ss -tulpn | grep 5000 || echo "  → Port 5000 ยังไม่เปิด"

echo ""
echo "=========================================="
echo "✅ เสร็จสมบูรณ์!"
echo "=========================================="
echo ""
echo "ทดสอบ:"
echo "  curl -I http://localhost:5000/"
echo "  curl -I http://YOUR_SERVER_IP/dashboard/"
echo ""

