from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

# State variables
light_level = 0
distance = 0
temperature = 0.0
humidity = 0.0
led_status = False
fan_speed = 0
buzzer_status = False

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/update_light', methods=['POST'])
def update_light():
    global light_level
    data = request.get_json()
    light_level = data.get('level', 0)
    return jsonify({'status': 'success', 'light_level': light_level}), 200

@app.route('/update_distance', methods=['POST'])
def update_distance():
    global distance, buzzer_status
    data = request.get_json()
    distance = data.get('distance', 0)
    
    # Buzzer triggers if distance is less than 20 cm
    buzzer_status = True if distance < 20 else False
    return jsonify({'status': 'success', 'distance': distance}), 200

@app.route('/update_dht', methods=['POST'])
def update_dht():
    global temperature, humidity
    data = request.get_json()
    temperature = data.get('temperature', 0.0)
    humidity = data.get('humidity', 0.0)
    return jsonify({'status': 'success', 'temperature': temperature, 'humidity': humidity}), 200

@app.route('/control_led', methods=['POST'])
def control_led():
    global led_status
    data = request.get_json()
    led_status = data.get('status', False)
    return jsonify({'status': 'success', 'led_status': led_status}), 200

@app.route('/control_fan', methods=['POST'])
def control_fan():
    global fan_speed
    data = request.get_json()
    fan_speed = data.get('speed', 0)
    return jsonify({'status': 'success', 'fan_speed': fan_speed}), 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'light_level': light_level,
        'distance': distance,
        'temperature': temperature,
        'humidity': humidity,
        'led_status': led_status,
        'fan_speed': fan_speed,
        'buzzer_status': buzzer_status
    }), 200

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create the dashboard.html file with the updated content
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
                .section h2 { margin-bottom: 10px; }
                .status-label { font-weight: bold; }
            </style>
            <script>
                async function fetchData() {
                    try {
                        const response = await fetch('/status');
                        const data = await response.json();
                        
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
                
                setInterval(fetchData, 2000);
                window.onload = fetchData;
            </script>
        </head>
        <body>
            <div class="container">
                <h2>Smart Room Controller</h2>
                <div class="section">
                    <span class="status-label">Light Level:</span> <span id="light">Loading...</span>
                </div>
                <div class="section">
                    <span class="status-label">Distance:</span> <span id="distance">Loading...</span>
                </div>
                <div class="section">
                    <span class="status-label">Temperature:</span> <span id="temperature">Loading...</span>
                </div>
                <div class="section">
                    <span class="status-label">Humidity:</span> <span id="humidity">Loading...</span>
                </div>
                <div class="section">
                    <span class="status-label">LED Status:</span> <span id="led">Loading...</span>
                </div>
                <div class="section">
                    <span class="status-label">Fan Speed:</span> <span id="fan">Loading...</span>
                </div>
                <div class="section">
                    <span class="status-label">Buzzer Status:</span> <span id="buzzer">Loading...</span>
                </div>
            </div>
        </body>
        </html>
        """)

    app.run(debug=True, host='0.0.0.0', port=5000)
