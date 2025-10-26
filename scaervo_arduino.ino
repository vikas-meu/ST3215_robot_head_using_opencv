#include <SCServo.h>

SMS_STS st;

#define S_RXD 16
#define S_TXD 17

#define SERVO1_ID 2
#define SERVO2_ID 1

void setup() {
  Serial.begin(115200); // USB serial to PC (Python)
  Serial1.begin(1000000, SERIAL_8N1, S_RXD, S_TXD); // Servo serial bus
  st.pSerial = &Serial1;
  delay(1000);

  Serial.println("SCServo Control Ready ✅");
}

void loop() {
  if (!Serial.available()) return;

  String data = Serial.readStringUntil('\n');
  data.trim();

  int commaIndex = data.indexOf(',');
  if (commaIndex < 0) return;

  int angle1 = data.substring(0, commaIndex).toInt();
  int angle2 = data.substring(commaIndex + 1).toInt();

  // Limit safety angle
  angle1 = constrain(angle1, 0, 180);
  angle2 = constrain(angle2, 0, 180);

  // Convert degrees → SCServo position
  int pos1 = map(angle1, 0, 180, 0, 2000);
  int pos2 = map(angle2, 0, 180, 0, 2000);

  // Send high-resolution move command
  st.WritePosEx(SERVO1_ID, pos1, 1500, 50);
  st.WritePosEx(SERVO2_ID, pos2, 1500, 50);
}
