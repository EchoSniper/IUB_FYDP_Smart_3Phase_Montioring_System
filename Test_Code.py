import serial
import socket
import threading
import json
import time

# Serial communication setup
arduino_port = '/dev/ttyUSB0'  # Replace with your Arduino's port
baud_rate = 9600
sensor_data = {
    "Phase_A_Voltage": 0.0,
    "Phase_A_Current": 0.0,
    "Phase_B_Voltage": 0.0,
    "Phase_B_Current": 0.0,
    "Phase_C_Voltage": 0.0,
    "Phase_C_Current": 0.0,
}

# HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Distribution Line Monitoring System</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #001f3f, #0074D9, #7FDBFF);
            font-family: 'Poppins', sans-serif; /* Rounded and modern font */
            color: #ffffff;
            overflow-x: hidden;
            min-height: 100vh; /* Ensure full-screen background */
        }

        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
            width: 100%;
            max-width: 1200px;
            margin: 0;
            overflow: hidden;
        }

        .logo {
            width: 150px;
            margin-bottom: 10px;
        }

        h1, h2, p, .clock {
            font-weight: bold; /* Make the text bold */
        }

        h1 {
            font-size: 2rem;
            margin: 5px 0;
            text-align: center;
        }

        h2 {
            font-size: 1.5rem;
            margin: 5px 0;
            color: #d1d1d1;
            text-align: center;
        }

        p {
            font-size: 1.2rem;
            margin: 5px 0;
            text-align: center;
        }

        .readings-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            width: 100%;
            gap: 15px;
            margin-bottom: 20px;
        }

        .voltage-container, .current-container {
            flex: 1;
            min-width: 45%;
            text-align: center;
        }

        .reading {
            background-color: #333;
            border: 2px solid #0074D9;
            padding: 15px;
            border-radius: 10px;
            font-size: 1.2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 5px;
            margin-bottom: 10px;
        }

        .reading span {
            font-size: 1.4rem;
            font-weight: bold;
        }

        .status-container {
            display: flex;
            justify-content: space-around;
            width: 100%;
            gap: 15px;
            margin-bottom: 20px;
        }

        .status {
            background-color: #333;
            border: 2px solid #2ECC40;
            padding: 15px;
            border-radius: 10px;
            font-size: 1.2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 5px;
            width: 45%;
        }

        .status span {
            font-weight: bold;
        }

        .clock {
            font-size: 1.2rem;
            font-weight: bold;
            margin-top: 15px;
            text-align: center;
        }

        @media (min-width: 768px) {
            h1 {
                font-size: 3rem;
            }

            h2 {
                font-size: 1.8rem;
            }

            p {
                font-size: 1.4rem;
            }

            .clock {
                font-size: 1.5rem;
            }

            .voltage-container, .current-container {
                min-width: 48%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="https://raw.githubusercontent.com/EchoSniper/IUB_FYDP_Finalized_Codes/refs/heads/main/image-removebg-preview.png" alt="IUB Logo" class="logo">
        <div class="content">
            <h1>Distribution Line Monitoring System</h1>
            <h2>Independent University, Bangladesh</h2>
            <p>Constructed by "IUB EEE GridGuardians"</p>
            <p>Raafiu Ashiquzzaman Mahmood, Md. Roman Khan, Taremun Arefin, Salma Islam Mim</p>
        </div>
        <div class="readings-container">
            <div class="voltage-container">
                <h3>Voltage Readings</h3>
                <div class="reading">Phase A Voltage: <span id="voltageA">--</span> V</div>
                <div class="reading">Phase B Voltage: <span id="voltageB">--</span> V</div>
                <div class="reading">Phase C Voltage: <span id="voltageC">--</span> V</div>
            </div>
            <div class="current-container">
                <h3>Current Readings</h3>
                <div class="reading">Phase A Current: <span id="currentA">--</span> A</div>
                <div class="reading">Phase B Current: <span id="currentB">--</span> A</div>
                <div class="reading">Phase C Current: <span id="currentC">--</span> A</div>
            </div>
        </div>
        <div class="status-container">
            <div class="status">Status: <span id="status">Normal</span></div>
            <div class="status">Fault Type: <span id="faultType">No Fault Detected</span></div>
        </div>
        <div class="clock" id="clock">Last Checked: 12:00:00</div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').innerText = 'Last Checked: ' + now.toLocaleTimeString();
        }

        function fetchData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('voltageA').textContent = data.Phase_A_Voltage;
                    document.getElementById('voltageB').textContent = data.Phase_B_Voltage;
                    document.getElementById('voltageC').textContent = data.Phase_C_Voltage;
                    document.getElementById('currentA').textContent = data.Phase_A_Current;
                    document.getElementById('currentB').textContent = data.Phase_B_Current;
                    document.getElementById('currentC').textContent = data.Phase_C_Current;
                    document.getElementById('status').textContent = "Normal";  // Customize based on your logic
                    document.getElementById('faultType').textContent = "No Fault Detected";  // Customize based on your logic
                })
                .catch(error => console.error('Error fetching data:', error));
        }

        setInterval(updateClock, 1000);
        setInterval(fetchData, 1000);
    </script>
</body>
</html>
"""

# Web server configuration
ip_address = "192.168.68.110"  # Listen on all interfaces
port = 2010

def read_serial_data():
    """Continuously read data from the Arduino and update the global sensor_data dictionary."""
    global sensor_data
    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        print("Connected to Arduino...")
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"Received data: {line}")
                    values = list(map(float, line.split(",")))
                    if len(values) == 6:  # Ignore ground current
                        sensor_data["Phase_A_Voltage"] = max(0, values[0] if values[0] >= 50 else 0)
                        sensor_data["Phase_A_Current"] = values[1]
                        sensor_data["Phase_B_Voltage"] = max(0, values[2] if values[2] >= 50 else 0)
                        sensor_data["Phase_B_Current"] = values[3]
                        sensor_data["Phase
