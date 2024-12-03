import cv2
from ultralytics import YOLO
import os

# Load the YOLO model
model = YOLO("ai-fire-detection/best.pt")

# Open the video file or stream
url_cam = os.environ.get('CAM_URL', 'rtsp://tapoadmin:meuzovo123@192.168.15.109:554/stream2')
cap = cv2.VideoCapture(url_cam)

if not cap.isOpened():
    print("Erro ao abrir o vídeo ou stream.")
    exit()

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO inference on the frame
        results = model.predict(frame, max_det=1)

        # Draw bounding boxes for detected objects
        for detection in results[0].boxes.data:  # Iterate over detected objects
            class_id = int(detection[5])  # Class ID is in the 6th position (index 5)
            if class_id == 0:
                print("Classe 0 detectada!")

                # Draw bounding box (example: x1, y1, x2, y2)
                x1, y1, x2, y2 = map(int, detection[:4])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Classe 0", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Show the frame with bounding boxes
        cv2.imshow("YOLO Detection", frame)

        # Exit the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    else:
        # Break the loop if the end of the video is reached
        print("Fim do vídeo ou falha ao ler o frame.")
        break

# Release the video capture object and close windows
cap.release()
cv2.destroyAllWindows()
