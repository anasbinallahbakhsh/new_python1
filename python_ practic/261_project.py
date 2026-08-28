import cv2
import mediapipe as mp

mp_hands=mp.solutions.hands
hands=mp_hands.Hands(max_num_hands=1,min_detection_confidence=0.7,min_tracking_confidence=0.7)
draw=mp.solutions.drawing_utils
cap=cv2.VideoCapture(0)
while True:
 ret,frame=cap.read()
 if not ret: break
 frame=cv2.flip(frame,1)
 rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
 results=hands.process(rgb)
 if results.multi_hand_landmarks:
  for hand in results.multi_hand_landmarks:
   draw.draw_landmarks(frame,hand,mp_hands.HAND_CONNECTIONS)
 cv2.putText(frame,'Hand Detection Demo',(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
 cv2.imshow('Hand Detection',frame)
 if cv2.waitKey(1)&0xFF==ord('q'): break
cap.release()
cv2.destroyAllWindows()
import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Drawing Utility
draw = mp.solutions.drawing_utils

# Open Webcam
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()

    if not success:
        break

    # Flip Image
    frame = cv2.flip(frame, 1)

    # Convert BGR to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect Hands
    results = hands.process(rgb)

    # Draw Landmarks
    if results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

            # Get Frame Size
            h, w, c = frame.shape

            # Draw Landmark IDs
            for id, lm in enumerate(hand.landmark):

                cx = int(lm.x * w)
                cy = int(lm.y * h)

                # Red Circle
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), cv2.FILLED)

                # Landmark Number
                cv2.putText(
                    frame,
                    str(id),
                    (cx + 5, cy - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 0),
                    1
                )

    # Heading
    cv2.putText(
        frame,
        "Hand Detection Demo",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Show Window
    cv2.imshow("Hand Detection", frame)

    # Press Q to Exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
# Count Fingers
fingers = []

if len(lmList) != 0:

    # Thumb
    if lmList[4][0] > lmList[3][0]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other Fingers
    for id in range(1, 5):
        if lmList[tipIds[id]][1] < lmList[tipIds[id]-2][1]:
            fingers.append(1)
        else:
            fingers.append(0)

    totalFingers = fingers.count(1)

    cv2.putText(
        frame,
        f"Fingers: {totalFingers}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 255),
        2
    )status = ""

if totalFingers == 0:
    status = "Closed Hand"

elif totalFingers == 5:
    status = "Open Hand"

else:
    status = "Detected"

cv2.putText(
    frame,
    status,
    (20, 110),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 255, 255),
    2
)
# FPS Counter
cTime = time.time()
fps = 1 / (cTime - pTime) if cTime != pTime else 0
pTime = cTime

cv2.putText(
    frame,
    f"FPS: {int(fps)}",
    (450, 30),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0, 255, 0),
    2
)
# Detect Hand Gesture
gesture = "Unknown"

# Open Hand
if fingers == [1, 1, 1, 1, 1]:
    gesture = "Open Hand"

# Closed Fist
elif fingers == [0, 0, 0, 0, 0]:
    gesture = "Fist"

# Peace Sign ✌
elif fingers == [0, 1, 1, 0, 0]:
    gesture = "Peace"

# Thumbs Up 👍
elif fingers == [1, 0, 0, 0, 0]:
    gesture = "Thumbs Up"

# Index Finger ☝
elif fingers == [0, 1, 0, 0, 0]:
    gesture = "Pointing"

cv2.putText(
    frame,
    f"Gesture: {gesture}",
    (20, 150),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.9,
    (255, 255, 255),
    2
)
# Thumb Tip
x1, y1 = lmList[4]

# Index Finger Tip
x2, y2 = lmList[8]

# Draw Line
cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

# Draw Circles
cv2.circle(frame, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
cv2.circle(frame, (x2, y2), 10, (255, 0, 255), cv2.FILLED)

# Middle Point
cx = (x1 + x2) // 2
cy = (y1 + y2) // 2

cv2.circle(frame, (cx, cy), 8, (0, 255, 255), cv2.FILLED)

# Calculate Distance
distance = math.hypot(x2 - x1, y2 - y1)

cv2.putText(
    frame,
    f"Distance: {int(distance)}",
    (20, 190),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0, 255, 0),
    2
)
# -----------------------------
# Draw Bounding Box
# -----------------------------
xList = []
yList = []

for point in lmList:
    xList.append(point[0])
    yList.append(point[1])

if len(xList) != 0:

    xmin = min(xList)
    xmax = max(xList)

    ymin = min(yList)
    ymax = max(yList)

    cv2.rectangle(
        frame,
        (xmin - 20, ymin - 20),
        (xmax + 20, ymax + 20),
        (0, 255, 0),
        2
    )
    # -----------------------------
# Hand Center
# -----------------------------
centerX = (xmin + xmax) // 2
centerY = (ymin + ymax) // 2

cv2.circle(
    frame,
    (centerX, centerY),
    10,
    (255, 255, 0),
    cv2.FILLED
)

cv2.putText(
    frame,
    "CENTER",
    (centerX - 30, centerY - 15),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (255, 255, 255),
    2
)
# Index Finger Tip
x, y = lmList[8]

# Convert Camera Coordinates to Screen Coordinates
mouse_x = screen_width / frame.shape[1] * x
mouse_y = screen_height / frame.shape[0] * y

# Move Mouse
pyautogui.moveTo(mouse_x, mouse_y)
cv2.putText(
    frame,
    f"Mouse: ({int(mouse_x)}, {int(mouse_y)})",
    (20, 230),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (0, 255, 255),
    2
)
# Left Click
current_time = time.time()

if distance < 35:
    if current_time - last_click > click_delay:

        pyautogui.click()

        last_click = current_time

        cv2.putText(
            frame,
            "LEFT CLICK",
            (20, 270),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            2
        )
        smooth = 0.2

current_x, current_y = pyautogui.position()

new_x = current_x + (mouse_x - current_x) * smooth
new_y = current_y + (mouse_y - current_y) * smooth

pyautogui.moveTo(new_x, new_y)
# Right Click
if fingers == [0, 1, 1, 0, 0]:

    if current_time - last_click > click_delay:

        pyautogui.rightClick()

        last_click = current_time

        cv2.putText(
            frame,
            "RIGHT CLICK",
            (20, 310),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 0, 0),
            2
        )
        # ===========================
# Scroll Up
# ===========================

if fingers == [0, 1, 1, 1, 0]:

    pyautogui.scroll(100)

    cv2.putText(
        frame,
        "SCROLL UP",
        (20, 350),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )
    # ===========================
# Scroll Down
# ===========================

if fingers == [1, 0, 0, 0, 1]:

    pyautogui.scroll(-100)

    cv2.putText(
        frame,
        "SCROLL DOWN",
        (20, 390),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 255),
        2
    )
    cv2.putText(
    frame,
    "Thumb+Index = Left Click",
    (20, 430),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (255,255,255),
    1
)

cv2.putText(
    frame,
    "Peace = Right Click",
    (20, 450),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (255,255,255),
    1
)

cv2.putText(
    frame,
    "3 Fingers = Scroll Up",
    (20, 470),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (255,255,255),
    1
)

cv2.putText(
    frame,
    "Thumb+Pinky = Scroll Down",
    (20, 490),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.5,
    (255,255,255),
    1
)
# ===========================
# Double Click
# ===========================

if fingers == [1, 1, 0, 0, 0]:

    if current_time - last_click > click_delay:

        pyautogui.doubleClick()

        last_click = current_time

        cv2.putText(
            frame,
            "DOUBLE CLICK",
            (20, 530),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 0),
            2
        )
        drag = False
        # ===========================
# Drag & Drop
# ===========================

if fingers == [0, 1, 0, 0, 0]:

    if not drag:

        pyautogui.mouseDown()

        drag = True

        cv2.putText(
            frame,
            "DRAG",
            (20, 570),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 255),
            2
        )

else:

    if drag:

        pyautogui.mouseUp()

        drag = False
        from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
# -----------------------------
# Volume Setup
# -----------------------------

devices = AudioUtilities.GetSpeakers()

interface = devices.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)

volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]
cv2.rectangle(frame, (50,150), (85,400), (0,255,0), 3)

cv2.rectangle(
    frame,
    (50,int(volBar)),
    (85,400),
    (0,255,0),
    cv2.FILLED
)

cv2.putText(
    frame,
    f"{int(volPercent)} %",
    (35,430),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0,255,0),
    2
)
# -----------------------------
# Air Canvas
# -----------------------------

drawColor = (255, 0, 255)

xp = 0
yp = 0

canvas = None
# -----------------------------
# Air Drawing
# -----------------------------

if len(lmList) != 0:

    x1, y1 = lmList[8]   # Index Finger

    # Only Index Finger Up
    if fingers == [0,1,0,0,0]:

        cv2.circle(frame, (x1,y1), 10, drawColor, cv2.FILLED)

        if xp == 0 and yp == 0:
            xp, yp = x1, y1

        cv2.line(canvas, (xp,yp), (x1,y1), drawColor, 8)

        xp, yp = x1, y1

    else:
        xp, yp = 0,0
        # -----------------------------
# Drawing Colors
# -----------------------------

PURPLE = (255, 0, 255)
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
BLACK = (0, 0, 0)

drawColor = PURPLE
cv2.rectangle(frame, (0,0), (100,60), PURPLE, cv2.FILLED)
cv2.rectangle(frame, (110,0), (210,60), BLUE, cv2.FILLED)
cv2.rectangle(frame, (220,0), (320,60), GREEN, cv2.FILLED)
cv2.rectangle(frame, (330,0), (430,60), RED, cv2.FILLED)
cv2.rectangle(frame, (440,0), (560,60), (80,80,80), cv2.FILLED)

cv2.putText(frame,"ERASE",(455,38),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,(255,255,255),2)
if len(lmList) != 0:

    x1, y1 = lmList[8]

    # Select Color
    if y1 < 60:

        if x1 < 100:
            drawColor = PURPLE

        elif x1 < 210:
            drawColor = BLUE

        elif x1 < 320:
            drawColor = GREEN

        elif x1 < 430:
            drawColor = RED

        elif x1 < 560:
            drawColor = BLACK
            thickness = 8

if drawColor == BLACK:
    thickness = 35

cv2.line(
    canvas,
    (xp, yp),
    (x1, y1),
    drawColor,
    thickness
)
key = cv2.waitKey(1)

if key == ord("s"):
    cv2.imwrite("drawing.png", canvas)
    print("Drawing Saved")

if key == ord("c"):
    canvas = np.zeros_like(frame)

if key == ord("q"):
    break
# ==============================
# Screenshot Gesture
# ==============================

if fingers == [1,1,1,0,0]:

    if current_time - last_click > 1:

        filename = f"screenshot_{shot}.png"

        pyautogui.screenshot(filename)

        shot += 1

        last_click = current_time

        cv2.putText(
            frame,
            "SCREENSHOT SAVED",
            (20,620),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,255,0),
            2
        )
        # ==========================
# Start Recording
# ==========================

if fingers == [1,1,0,1,1]:

    if not record:

        video = cv2.VideoWriter(
            "record.avi",
            fourcc,
            20,
            (frame.shape[1], frame.shape[0])
        )

        record = True
        # ==========================
# Professional Header
# ==========================

cv2.rectangle(frame, (0,0), (frame.shape[1],70), (35,35,35), cv2.FILLED)

cv2.putText(
    frame,
    "AI HAND TRACKING SYSTEM",
    (20,45),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0,255,255),
    2
)
cv2.rectangle(frame,(520,0),(640,70),(50,50,50),cv2.FILLED)

cv2.putText(
    frame,
    f"FPS : {int(fps)}",
    (535,45),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (0,255,0),
    2
)
cv2.rectangle(frame,(0,80),(180,180),(45,45,45),cv2.FILLED)

cv2.putText(
    frame,
    f"Finger : {totalFingers}",
    (15,120),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (255,255,255),
    2
)

cv2.putText(
    frame,
    gesture,
    (15,160),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (0,255,255),
    2
)
cv2.rectangle(frame,(0,190),(180,250),(45,45,45),cv2.FILLED)

cv2.putText(     frame,
    f"Distance : {int(distance)}",
    (10,230),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.6,
    (255,255,255),
    2
)
if record:

    cv2.circle(frame,(610,100),12,(0,0,255),cv2.FILLED)

    cv2.putText(
        frame,
        "REC",
        (570,108),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255,255,255),
        2
    )
       cv2.rectangle(
    frame,
    (0, frame.shape[0]-35),
    (frame.shape[1], frame.shape[0]),
    (40,40,40),
    cv2.FILLED
)

cv2.putText(
    frame,
    "Press Q = Quit | S = Save | C = Clear Canvas",
    (10, frame.shape[0]-10),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.55,
    (255,255,255),
    1
)