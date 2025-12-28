import requests
import json

# ==========================================
# 🔑 ใส่กุญแจของคุณตรงนี้ (อย่าลืมเครื่องหมายคำพูด '...' นะครับ)
# ==========================================
LINE_ACCESS_TOKEN = 'R8cR4RQiDZA9sRljWNa8f6TaspfFYUxBoGaLNUAIBfaxD5iiN0jWiI2e34NAkXP36GBtALNyEk7foed2g1bdkArDqhA9NbhPeVqYqGdElngJt7+YHjdsiNv81geRXVfrKqD4UQABNNemXFfFwCW1uAdB04t89/1O/w1cDnyilFU='
YOUR_USER_ID = 'Ubb324ad1f45ef40d567ee70823007142'

# ==========================================
# 📨 เตรียมข้อความที่จะส่ง
# ==========================================
url = 'https://api.line.me/v2/bot/message/push'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
}
data = {
    'to': YOUR_USER_ID,
    'messages': [
        {
            'type': 'text',
            'text': 'สวัสดีครับ JC! นี่คือข้อความทดสอบจาก PythonAnywhere 🚀✨'
        },
        {
            'type': 'sticker',
            'packageId': '446',
            'stickerId': '1988'
        }
    ]
}

# ==========================================
# 🚀 ยิงออกไปเลย!
# ==========================================
print("กำลังส่งข้อความ... ⏳")
response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    print("✅ สำเร็จ! เช็คดูใน LINE ได้เลยครับ")
else:
    print(f"❌ ล้มเหลว! (Code: {response.status_code})")
    print(response.text)