from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")
cap = cv2.VideoCapture("traffic.mp4")

while cap.isOpened():
    ok, frame = cap.read()
    if not ok:
        break

    results = model(frame, verbose=False)
    annotated = results[0].plot()

    cv2.imshow("Python Vision", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()