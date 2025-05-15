#include <WiFi.h>                     // Include WiFi library for ESP32
#include <HTTPClient.h>               // Include HTTPClient library for sending data to server
#include <ArduinoJson.h>              // Include ArduinoJson library to handle JSON data
#include <ESP32Servo.h>               // Include ESP32Servo library to control servo motors
#include <DHT.h>                     // Include DHT library for temperature and humidity sensor

// WiFi Credentials
const char* ssid = "Home Wifi[2Ghz]";  // Your WiFi SSID
const char* password = "wBhoaL7CZu";   // Your WiFi password

// Server URL
const char* serverUrl = "http://192.168.1.100:5000/update_sensors";  // Flask server URL for data update

// Pin Definitions
const int LDR_PIN = 34;      // Analog pin for LDR (light detection)
const int DHT_PIN = 26;      // Digital pin for DHT11 (temperature and humidity)
const int ULTRASONIC_TRIG = 12; // Digital pin for ultrasonic trigger
const int ULTRASONIC_ECHO = 13; // Digital pin for ultrasonic echo
const int BUTTON_PIN = 27;   // Digital pin for Button (motion simulation)
const int LED_PIN = 2;       // Digital pin for LED (lighting control)
const int FAN_SERVO_PIN = 25;  // PWM pin for fan servo motor
const int DOOR_SERVO_PIN = 14; // PWM pin for door servo motor
const int BUZZER_PIN = 15;   // Digital pin for Buzzer (alert)

// Servo Objects
Servo fanServo;              // Servo object for fan control
Servo doorServo;             // Servo object for door control

// DHT Sensor
#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);  // Initialize DHT sensor

// Sensor Variables
int lightLevel = 0;          // Variable to store light level
float temperature = 0.0;     // Variable to store temperature
int distance = 0;            // Variable to store ultrasonic distance
bool ledStatus = false;      // LED on/off status
bool buttonPressed = false;  // Button press status
unsigned long lastButtonPress = 0;   // Last button press time
const unsigned long debounceDelay = 300;  // Debounce delay for button

// WiFi Reconnection Function
void connectWiFi() {
  while (WiFi.status() != WL_CONNECTED) {  // Loop until connected
    Serial.print(".");
    WiFi.begin(ssid, password);         // Attempt WiFi connection
    delay(1000);
  }
  Serial.println("\nConnected to WiFi");
}

// Setup function
void setup() {
  Serial.begin(115200);                // Initialize serial communication
  pinMode(LED_PIN, OUTPUT);            // Set LED pin as output
  pinMode(BUZZER_PIN, OUTPUT);         // Set buzzer pin as output
  pinMode(ULTRASONIC_TRIG, OUTPUT);    // Set ultrasonic trigger pin as output
  pinMode(ULTRASONIC_ECHO, INPUT);     // Set ultrasonic echo pin as input
  pinMode(BUTTON_PIN, INPUT_PULLUP);   // Set button pin as input with pull-up resistor

  // Attach servos
  fanServo.attach(FAN_SERVO_PIN);      // Attach fan servo
  doorServo.attach(DOOR_SERVO_PIN);    // Attach door servo

  dht.begin();                        // Initialize DHT sensor
  connectWiFi();                      // Connect to WiFi
}

// Function to read LDR value
int readLDR() {
  return analogRead(LDR_PIN);          // Read and return LDR value
}

// Function to read Ultrasonic sensor
int readUltrasonic() {
  digitalWrite(ULTRASONIC_TRIG, LOW);  // Ensure trigger is low
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_TRIG, HIGH); // Send trigger pulse
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG, LOW);  // Stop trigger
  int duration = pulseIn(ULTRASONIC_ECHO, HIGH);  // Measure echo duration
  int distance = duration * 0.034 / 2; // Calculate distance in cm
  return distance;
}

// Function to control door based on distance
void controlDoor() {
  if (distance <= 30) {
    doorServo.write(180);  // Open door
    digitalWrite(BUZZER_PIN, HIGH);  // Activate buzzer
  } else {
    doorServo.write(0);    // Close door
    digitalWrite(BUZZER_PIN, LOW);   // Deactivate buzzer
  }
}

// Function to control LED based on button press
void controlLED() {
  unsigned long currentTime = millis();
  if (digitalRead(BUTTON_PIN) == LOW && (currentTime - lastButtonPress) > debounceDelay) {
    buttonPressed = !buttonPressed;
    ledStatus = buttonPressed;
    digitalWrite(LED_PIN, ledStatus ? HIGH : LOW);  // Toggle LED
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
  lightLevel = readLDR();               // Get light level
  distance = readUltrasonic();          // Get distance
  temperature = dht.readTemperature();  // Get temperature

  if (isnan(temperature)) {             // Check for valid temperature
    temperature = 0.0;
  }

  controlLED();                        // Control LED based on button
  controlFan();                        // Control fan based on temperature
  controlDoor();                       // Control door based on distance

  sendData();                          // Send sensor data to server
  delay(2000);                         // Wait before next loop
}

