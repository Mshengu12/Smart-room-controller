#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <DHT.h>

// WiFi Credentials
const char* ssid = "Home Wifi[2Ghz]";
const char* password = "wBhoaL7CZu";

// Server URL
const char* serverUrl = "http://192.168.1.100:5000/update_sensors";

// Pin Definitions
const int LDR_PIN = 34;      // Analog pin for LDR
const int DHT_PIN = 26;      // Digital pin for DHT11
const int ULTRASONIC_TRIG = 12;
const int ULTRASONIC_ECHO = 13;
const int BUTTON_PIN = 27;   // Digital pin for Button
const int LED_PIN = 2;       // Digital pin for LED
const int FAN_SERVO_PIN = 25;  // PWM pin for Fan Servo
const int DOOR_SERVO_PIN = 14; // PWM pin for Door Servo
const int BUZZER_PIN = 15;   // Digital pin for Buzzer

// Servo Objects
Servo fanServo;
Servo doorServo;

// DHT Sensor
#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);

// Sensor Variables
int lightLevel = 0;
float temperature = 0.0;
int distance = 0;
bool ledStatus = false;
bool buttonPressed = false;
unsigned long lastButtonPress = 0;
const unsigned long debounceDelay = 300; // Debounce delay

// WiFi Reconnection Function
void connectWiFi() {
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    WiFi.begin(ssid, password);
    delay(1000);
  }
  Serial.println("\nConnected to WiFi");
}

// Setup function
void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(ULTRASONIC_TRIG, OUTPUT);
  pinMode(ULTRASONIC_ECHO, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Attach servos
  fanServo.attach(FAN_SERVO_PIN);
  doorServo.attach(DOOR_SERVO_PIN);

  // Initialize DHT sensor
  dht.begin();

  // Connect to WiFi
  connectWiFi();
}

// Function to read LDR value
int readLDR() {
  return analogRead(LDR_PIN);
}

// Function to read Ultrasonic sensor
int readUltrasonic() {
  digitalWrite(ULTRASONIC_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG, LOW);
  int duration = pulseIn(ULTRASONIC_ECHO, HIGH);
  int distance = duration * 0.034 / 2;
  return distance;
}

// Function to control door based on ultrasonic distance
void controlDoor() {
  if (distance <= 30) {
    doorServo.write(180);  // Open door
    digitalWrite(BUZZER_PIN, HIGH);
  } else {
    doorServo.write(0);    // Close door
    digitalWrite(BUZZER_PIN, LOW);
  }
}

// Function to control LED based on button press
void controlLED() {
  unsigned long currentTime = millis();
  if (digitalRead(BUTTON_PIN) == LOW && (currentTime - lastButtonPress) > debounceDelay) {
    buttonPressed = !buttonPressed;
    ledStatus = buttonPressed;
    digitalWrite(LED_PIN, ledStatus ? HIGH : LOW);
    lastButtonPress = currentTime;
  }
}

// Function to control fan based on temperature
void controlFan() {
  if (temperature <= 15) {
    fanServo.write(90);   // Medium speed
  } else if (temperature >= 20) {
    fanServo.write(180);  // Full speed
  } else {
    fanServo.write(0);    // Off
  }
}

// Function to send data to the Flask server
void sendData() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Create JSON payload
    DynamicJsonDocument jsonDoc(256);
    jsonDoc["light_level"] = lightLevel;
    jsonDoc["distance"] = distance;
    jsonDoc["led_status"] = ledStatus;
    jsonDoc["temperature"] = temperature;

    String jsonString;
    serializeJson(jsonDoc, jsonString);

    int httpResponseCode = http.POST(jsonString);
    Serial.print("Server Response: ");
    Serial.println(httpResponseCode);

    http.end();
  } else {
    Serial.println("WiFi Disconnected. Reconnecting...");
    connectWiFi();
  }
}

// Main loop function
void loop() {
  // Read sensors
  lightLevel = readLDR();
  distance = readUltrasonic();
  temperature = dht.readTemperature();

  // Check for valid temperature reading
  if (isnan(temperature)) {
    temperature = 0.0;
  }

  // Control devices
  controlLED();
  controlFan();
  controlDoor();

  // Send data to server
  sendData();

  // Delay before next read
  delay(2000);
}
