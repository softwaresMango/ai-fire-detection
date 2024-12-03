import cv2
from ultralytics import YOLO
import requests
import threading
import time
from time import sleep

# Load the YOLOv8 model
model = YOLO("fire-detection/best.pt")

# Open the video file (or webcam if index 0)
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("Erro ao abrir a câmera")
    exit()

def send_request(frame, data):
    # Encode the frame as JPEG
    _, img_encoded = cv2.imencode('.jpg', frame)
    # Send POST request to Flask server with the image
    try:
        response = requests.post(
            'http://192.168.15.14/alarm/fire_detection',
            files={'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')},
            data=data
        )
        # Print server response
        print(response.status_code)
    except requests.exceptions.RequestException as e:
        print("Erro ao conectar ao servidor:", e)

# Variable to control the time between requests
last_request_time = 0
request_interval = 10  # Interval in seconds

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Convert BGR to RGB for YOLOv8 inference
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run YOLOv8 inference on the frame
        results = model(frame_rgb, conf=0.7)

        # Debug: print the results

        # Check if any objects were detected
        if len(results) > 0 and hasattr(results[0], 'boxes') and results[0].boxes:
            print("Objeto detectado!")
            current_time = time.time()
            if current_time - last_request_time > request_interval:
                last_request_time = current_time
                # Prepare data to send
                data = {
                    "apiKey": "teste",
                    "clientId": "teste",
                    "cam": "camera 1",
                    "detections": str(results[0].boxes)
                }
                # Start a new thread to send the request
                threading.Thread(target=send_request, args=(frame, data)).start()

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        # Convert the annotated frame back to BGR for proper display in OpenCV
        annotated_frame_bgr = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)

        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame_bgr)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # If no frame is captured, break the loop
        print("Erro ao capturar frame")
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
