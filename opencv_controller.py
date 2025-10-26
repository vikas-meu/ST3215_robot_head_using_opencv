import cv2
import mediapipe as mp
import numpy as np
import serial
import time

# ✅ Serial to ESP32 (update port if needed)
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_draw = mp.solutions.drawing_utils
drawing_spec = mp_draw.DrawingSpec(thickness=1, circle_radius=1)
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.8, 
                                  min_tracking_confidence=0.8)

cap = cv2.VideoCapture(1)
ws, hs = 600, 600
cap.set(3, ws)
cap.set(4, hs)

if not cap.isOpened():
    print("Camera error")
    exit()

def calculate_head_movement(nose, left_eye, right_eye):
    face_center_x = (left_eye[0] + right_eye[0]) / 2
    yaw = np.interp(nose[0], [face_center_x - 50, face_center_x + 50], [180, 0])
    
    eye_level_y = (left_eye[1] + right_eye[1]) / 2
    pitch = np.interp(nose[1], [eye_level_y - 50, eye_level_y + 90], [0, 180])
    return yaw, pitch

def smooth(current, target, factor=0.1):
    return current*(1-factor) + target*factor

current_yaw = 180
current_pitch = 180

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    if results.multi_face_landmarks:
        face = results.multi_face_landmarks[0].landmark
        
        nose = [face[1].x * ws, face[1].y * hs]
        left_eye = [face[33].x * ws, face[33].y * hs]
        right_eye = [face[263].x * ws, face[263].y * hs]

        target_yaw, target_pitch = calculate_head_movement(nose, left_eye, right_eye)

        current_yaw = smooth(current_yaw, target_yaw)
        current_pitch = smooth(current_pitch, target_pitch)

        yaw_i = int(np.clip(current_yaw, 0, 180))
        pitch_i = int(np.clip(current_pitch, 0, 180))

        # ✅ Send servo commands to ESP32
        cmd = f"{yaw_i},{pitch_i}\n"
        ser.write(cmd.encode())

        cv2.putText(img, f"Yaw:{yaw_i} Pitch:{pitch_i}", (20,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)

    cv2.imshow("Head Tracking Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
