from flask import Flask, request, jsonify, render_template  # Import Flask components for server, request handling, and templates
from flask_cors import CORS  # Import CORS to handle cross-origin requests
import os  # Import os for file system operations

# Initialize the Flask application and specify the template folder location
app = Flask(__name__, template_folder='templates')

# Enable Cross-Origin Resource Sharing (CORS) for all routes
CORS(app)

# State variables to store the current sensor and control states
light_level = 0  # Light level value from LDR sensor
distance = 0  # Distance value from Ultrasonic sensor
temperature = 0.0  # Temperature value from DHT sensor
humidity = 0.0  # Humidity value from DHT sensor
led_status = False  # LED status (ON/OFF)
fan_speed = 0  # Fan speed level (0-180 for servo motor)
buzzer_status = False  # Buzzer status (True = Alert, False = Normal)

# Route for the main dashboard page
@app.route('/')
def index():
    # Render the dashboard.html template to display the control panel
    return render_template('dashboard.html')

# Route to update the light level data
@app.route('/update_light', methods=['POST'])
def update_light():
    global light_level  # Access the global light_level variable
    data = request.get_json()  # Receive JSON data from the POST request
    light_level = data.get('level', 0)  # Update the light level value
    # Return a response with the updated light level
    return jsonify({'status': 'success', 'light_level': light_level}), 200

# Route to update distance and buzzer status
@app.route('/update_distance', methods=['POST'])
def update_distance():
    global distance, buzzer_status  # Access global variables
    data = request.get_json()  # Receive JSON data
    distance = data.get('distance', 0)  # Update distance value
    # Set buzzer status based on the distance threshold of 20 cm
    buzzer_status = True if distance < 20 else False
    # Return a response with the updated distance
    return jsonify({'status': 'success', 'distance': distance}), 200

# Route to update temperature and humidity data
@app.route('/update_dht', methods=['POST'])
def update_dht():
    global temperature, humidity  # Access global variables
    data = request.get_json()  # Receive JSON data
    temperature = data.get('temperature', 0.0)  # Update temperature
    humidity = data.get('humidity', 0.0)  # Update humidity
    # Return a response with the updated temperature and humidity
    return jsonify({'status': 'success', 'temperature': temperature, 'humidity': humidity}), 200

# Route to control the LED
@app.route('/control_led', methods=['POST'])
def control_led():
    global led_status  # Access the global LED status variable
    data = request.get_json()  # Receive JSON data
    led_status = data.get('status', False)  # Update LED status
    # Return a response with the updated LED status
    return jsonify({'status': 'success', 'led_status': led_status}), 200

# Route to control the fan speed
@app.route('/control_fan', methods=['POST'])
def control_fan():
    global fan_speed  # Access the global fan speed variable
    data = request.get_json()  # Receive JSON data
    fan_speed = data.get('speed', 0)  # Update fan speed
    # Return a response with the updated fan speed
    return jsonify({'status': 'success', 'fan_speed': fan_speed}), 200

# Route to retrieve the current state of all devices and sensors
@app.route('/status', methods=['GET'])
def status():
    # Return all state variables as a JSON response
    return jsonify({
        'light_level': light_level,
        'distance': distance,
        'temperature': temperature,
        'humidity': humidity,
        'led_status': led_status,
        'fan_speed': fan_speed,
        'buzzer_status': buzzer_status
    }), 200

# Entry point of the Flask application
if __name__ == '__main__':
    # Check if the 'templates' folder exists. If not, create it
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # Generate the dashboard.html file with HTML content
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Smart Room Controller</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f0f0f0; padding: 20px; }
                .container { background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px #ccc; }
                .section { margin-bottom: 15px; }
                .status-label { font-weight: bold; }
            </style>
            <script>
                // JavaScript function to fetch data from the server every 2 seconds
                async function fetchData() {
                    try {
                        const response = await fetch('/status');  // Send GET request to /status route
                        const data = await response.json();  // Parse JSON response

                        // Update HTML elements with the latest sensor values
                        document.getElementById('light').innerText = data.light_level;
                        document.getElementById('distance').innerText = data.distance + " cm";
                        document.getElementById('temperature').innerText = data.temperature + " °C";
                        document.getElementById('humidity').innerText = data.humidity + " %";
                        document.getElementById('led').innerText = data.led_status ? 'ON' : 'OFF';
                        document.getElementById('fan').innerText = data.fan_speed;
                        document.getElementById('buzzer').innerText = data.buzzer_status ? 'ALERT' : 'NORMAL';

                    } catch (error) {
                        console.error("Error fetching data:", error);
                    }
                }
                // Continuously fetch data every 2 seconds
                setInterval(fetchData, 2000);
                window.onload = fetchData;
            </script>
        </head>
        <body>
            <div class="container">
                <h2>Smart Room Controller</h2>
                <div class="section"><span class="status-label">Light Level:</span> <span id="light">Loading...</span></div>
                <div class="section"><span class="status-label">Distance:</span> <span id="distance">Loading...</span></div>
                <div class="section"><span class="status-label">Temperature:</span> <span id="temperature">Loading...</span></div>
                <div class="section"><span class="status-label">Humidity:</span> <span id="humidity">Loading...</span></div>
                <div class="section"><span class="status-label">LED Status:</span> <span id="led">Loading...</span></div>
                <div class="section"><span class="status-label">Fan Speed:</span> <span id="fan">Loading...</span></div>
                <div class="section"><span class="status-label">Buzzer Status:</span> <span id="buzzer">Loading...</span></div>
            </div>
        </body>
        </html>
        """)

    # Start the Flask server, accessible to all devices on the network
    app.run(debug=True, host='0.0.0.0', port=5000)
