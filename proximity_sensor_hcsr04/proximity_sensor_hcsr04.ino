// ------------------------------------------------------------
// Proximity Sensor Mini-Project (HC-SR04 Version)
// Sensor valid range: 23 cm to 312 cm
// ------------------------------------------------------------

// HC-SR04 has SEPARATE Trig and Echo pins
const int trigPin = 2;
const int echoPin = 6;

// Buzzer output pin
const int buzzerPin = 12;

// Stores echo travel time (microseconds)
long durationMicroseconds;

// Stores calculated distance (cm)
float distanceCM;

void setup() {
  // Trig sends the ultrasonic pulse → OUTPUT
  pinMode(trigPin, OUTPUT);
  // Echo receives the return signal → INPUT
  pinMode(echoPin, INPUT);
  // Buzzer sends sound → OUTPUT
  pinMode(buzzerPin, OUTPUT);

  // Start serial monitor for debugging
  Serial.begin(9600);
}

void loop() {
  // ---------------------------
  // TRIGGER THE SENSOR
  // ---------------------------
  // Ensure clean LOW start
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // HC-SR04 requires a 10µs HIGH pulse to trigger
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  // End trigger pulse
  digitalWrite(trigPin, LOW);

  // ---------------------------
  // LISTEN FOR ECHO
  // ---------------------------
  // Measure how long the echo pin stays HIGH
  durationMicroseconds = pulseIn(echoPin, HIGH);

  // Convert time to distance in cm
  // Speed of sound ≈ 0.034 cm/µs
  // Divide by 2 because sound travels out and back
  distanceCM = durationMicroseconds * 0.034 / 2.0;

  // Print distance for debugging
  Serial.print("Distance (cm): ");
  Serial.println(distanceCM);

  // ------------------------------------------------
  // DISTANCE LOGIC (Adjusted to 23–312 cm limits)
  // ------------------------------------------------

  // OUT OF RANGE (too far OR no object detected)
  if (distanceCM > 399 || distanceCM <= 0) {
    // No beeping if object is out of detectable range
    noTone(buzzerPin);
    delay(200);
  }

  // TOO CLOSE (below minimum reliable detection)
  else if (distanceCM < 2) {
    // Continuous high warning tone
    tone(buzzerPin, 2200);
  }

  // FAR RANGE (200–312 cm)
  else if (distanceCM >= 20 && distanceCM <= 399) {
    // Low pitch + slow beeping
    tone(buzzerPin, 400);
    delay(100);
    noTone(buzzerPin);
    delay(800);
  }

  // MEDIUM RANGE (100–199 cm)
  else if (distanceCM >= 10 && distanceCM < 20) {
    // Medium pitch + medium speed beeping
    tone(buzzerPin, 900);
    delay(100);
    noTone(buzzerPin);
    delay(400);
  }

  // CLOSE RANGE (23–99 cm)
  else {
    // High pitch + fast beeping
    tone(buzzerPin, 1500);
    delay(100);
    noTone(buzzerPin);
    delay(150);
  }

  // Small stabilization delay
  delay(30);
}
