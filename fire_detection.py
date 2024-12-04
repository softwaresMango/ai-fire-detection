import cv2
from ultralytics import YOLO
import os
import threading
import requests
import queue
import jwt
import datetime
import secrets
import string

# Load the YOLO model
model = YOLO("/app/best.pt")

# Video stream URL
SECRET_KEY = os.environ.get('SECRET-KEY', 'jwt-secret-key')
clientID = os.environ.get('CLIENT-ID', 'UNI-S3dI6aBnlQrrgGZd')
equipamentID = os.environ.get('EQUIPAMENT-ID', 'SYCMTOEXPER4')
url_cam = os.environ.get('CAM_URL', 'rtsp://tapoadmin:meuzovo123@192.168.15.109:554/stream2')
cap = cv2.VideoCapture(url_cam)


if not cap.isOpened():
    print("Erro ao abrir o vídeo ou stream.")
    exit()

detection_queue = queue.Queue()

last_request_time = threading.Event()
last_request_time.set() 

def generate_tid(length=24):
    characters = string.ascii_uppercase + string.digits
    tid = ''.join(secrets.choice(characters) for _ in range(length))
    return tid

def generate_jwt(payload, exp_minutes=300):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=exp_minutes)
    payload.update({"exp": expiration})
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token



# Function to handle HTTP requests
def send_request(ip):
    payload_token = {
        "clientID": clientID,
        "equipamentID": equipamentID
    }
    
    payload_body = {
        "client_id": clientID,
        "equipament_id": equipamentID
    }
    
    messageId = f"{generate_tid()}"
    token = f"{generate_jwt(payload_token)}"
    
    header = {
        "Content-Type":"application/json",
        "messageId": messageId,
        "token": token
    }

    try:
        requests.post(f"http://{ip}/flow/geral/v1/orch-fire-detection-alarm", headers=header, json=payload_body)
    except Exception as e:
        print(str(e))
        pass

def detection_handler(interval=60):
    global last_request_time

    while True:
        ip = detection_queue.get()  
        if ip is None: 
            break

        if last_request_time.is_set():
            send_request(ip)
            last_request_time.clear()
            threading.Timer(interval, last_request_time.set).start()
        else:
            with detection_queue.mutex:
                detection_queue.queue.clear()  

ip_address = "afsolucoesemti.ddns.net:9000" 
thread = threading.Thread(target=detection_handler, daemon=True)
thread.start()

try:
    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            print("Fim do vídeo ou falha ao ler o frame.")
            break

        results = model.predict(frame, max_det=1)

        for detection in results[0].boxes.data:
            class_id = int(detection[5]) 
            if class_id == 0:
                print("Classe 0 detectada!")
                detection_queue.put((ip_address))

except KeyboardInterrupt:
    print("\nInterrupção pelo usuário.")

finally:
    detection_queue.put((None, None))
    thread.join()
    cap.release()
    print("Processo encerrado.")
