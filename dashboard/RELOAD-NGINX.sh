#!/bin/bash
# สคริปต์สำหรับ reload nginx และทดสอบ

echo "=========================================="
echo "Reload Nginx และทดสอบ Static Files"
echo "=========================================="
echo ""

echo "⚠️  ต้องใช้ sudo เพื่อ reload nginx"
echo ""
echo "รันคำสั่งนี้:"
echo "  sudo nginx -t"
echo "  sudo systemctl reload nginx"
echo ""
echo "จากนั้นทดสอบ:"
echo "  curl -I http://lprserver.tail605477.ts.net/dashboard/static/style.css"
echo "  curl -I http://lprserver.tail605477.ts.net/dashboard/static/app.js"
echo ""

