# IPA2026 Week07 Part 7 RabbitMQ Producer

ไฟล์ใน VM: `~/IPA2026/Week7/scheduler/producer.py`

```bash
cd ~/IPA2026/Week7
source .venv/bin/activate
pip install -r scheduler/requirements.txt
sudo docker run -d -p 15672:15672 -p 5672:5672 --name rabbitmq rabbitmq:3-management
python scheduler/producer.py
python scheduler/producer.py 192.168.1.45
python scheduler/producer.py 192.168.1.46
```

หากมี container `rabbitmq` อยู่แล้ว ให้เริ่มตัวเดิมแทนสร้างซ้ำ

เปิด RabbitMQ Management ใน Firefox ของ VM ที่ http://localhost:15672 ใช้ guest / guest ตาม Part 7

ตรวจ Exchange `jobs` เป็นชนิด `direct`, Queue `router_jobs`, Binding key `check_interfaces` และจำนวน Messages Ready

ในหน้ารายละเอียด queue เปิด Get messages เลือก Ack mode เป็น Nack message requeue true แล้วกด Get Message(s) เพื่อดู payload และเก็บข้อความไว้ใน queue

พอร์ต 5672 ใช้ AMQP สำหรับ Python ส่วนพอร์ต 15672 ใช้ Management UI สำหรับ browser

Part 7 ส่งข้อความเข้า queue เพื่อรอ consumer ยังไม่ได้สั่ง SSH เข้า Router

อ้างอิงบทเรียน:
https://app.notion.com/p/IPA2026-Lab-Week07-Docker-and-Docker-Compose-Part-1-39086ecd18de8015b617f0a14ff440ee
