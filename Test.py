import serial
import socket
import threading
import json
import time
import pywt
import numpy as np

# Serial communication setup
arduino_port = '/dev/ttyUSB0'  # Update this based on your system
baud_rate = 9600

# Constants for fault detection
CONSTANT = 50  # Threshold value for fault detection
NEUTRAL = 2    # Neutral current threshold

# Sensor data and fault type
sensor_data = {
    "Ground_Current": 0.0,
    "Phase_C_Current": 0.0,
    "Phase_B_Current": 0.0,
    "Phase_A_Current": 0.0,
    "Phase_A_Voltage": 0.0,
    "Phase_B_Voltage": 0.0,
    "Phase_C_Voltage": 0.0,
    "Fault_Type": "No Fault Detected"
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
        /* CSS styles omitted for brevity, use the same styles as in your original code */
    </style>
</head>
<body>
    <div class="container">
        <img src="https://raw.githubusercontent.com/EchoSniper/IUB_FYDP_Finalized_Codes/refs/heads/main/IUB_Logo.png" alt="IUB Logo" class="logo">
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
            <div class="status">Status: <span id="faultType">No Fault Detected</span></div>
        </div>
        <div class="clock" id="clock">Last Checked: 12:00:00</div>
    </div>

    <script>
        async function fetchData() {
            try {
                const response = await fetch('/data');
                const data = await response.json();

                // Update readings
                document.getElementById('currentA').innerText = data.Phase_A_Current.toFixed(2);
                document.getElementById('currentB').innerText = data.Phase_B_Current.toFixed(2);
                document.getElementById('currentC').innerText = data.Phase_C_Current.toFixed(2);
                document.getElementById('voltageA').innerText = data.Phase_A_Voltage.toFixed(2);
                document.getElementById('voltageB').innerText = data.Phase_B_Voltage.toFixed(2);
                document.getElementById('voltageC').innerText = data.Phase_C_Voltage.toFixed(2);
                document.getElementById('faultType').innerText = data.Fault_Type;
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }

        setInterval(fetchData, 5000);

        function updateClock() {
            const now = new Date();
            document.getElementById('clock').innerText = 'Last Checked: ' + now.toLocaleTimeString();
        }

        setInterval(updateClock, 1000);
    </script>
</body>
</html>
"""

# Function to perform DWT
def perform_dwt(data):
    coeffs = pywt.dwt(data, 'db4')
    cA, cD = coeffs
    return np.max(np.abs(cA)), np.max(np.abs(cD))

# Function to detect fault
def detect_fault(m, n, p, q):
    if m > CONSTANT and n > CONSTANT and p > CONSTANT:
        if q > NEUTRAL:
            return "Three Phase to Ground Fault Detected"
        else:
            return "Three Phase Fault Detected"
    if m > CONSTANT and n > CONSTANT and p < CONSTANT:
        if q > NEUTRAL:
            return "Double Line to Ground Fault (AB-G) Detected"
        else:
            return "Line to Line Fault Between Phase A and B Detected"
    # Other conditions...
    return "Unknown Fault Detected"

def read_serial_data():
    global sensor_data
    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        print("Connected to Arduino...")
        current_data = {"Ground": [], "PhaseA": [], "PhaseB": [], "PhaseC": []}

        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"Received: {line}")
                values = list(map(float, line.split(",")))
                if len(values) == 7:
                    sensor_data["Ground_Current"] = values[0]
                    sensor_data["Phase_C_Current"] = values[1]
                    sensor_data["Phase_B_Current"] = values[2]
                    sensor_data["Phase_A_Current"] = values[3]
                    sensor_data["Phase_A_Voltage"] = values[4]
                    sensor_data["Phase_B_Voltage"] = values[5]
                    sensor_data["Phase_C_Voltage"] = values[6]

                    current_data["Ground"].append(values[0])
                    current_data["PhaseA"].append(values[3])
                    current_data["PhaseB"].append(values[2])
                    current_data["PhaseC"].append(values[1])

                    if len(current_data["Ground"]) >= 10:
                        m, _ = perform_dwt(current_data["PhaseA"])
                        n, _ = perform_dwt(current_data["PhaseB"])
                        p, _ = perform_dwt(current_data["PhaseC"])
                        q, _ = perform_dwt(current_data["Ground"])

                        fault = detect_fault(10 * m, 10 * n, 10 * p, 10 * q)
                        sensor_data["Fault_Type"] = fault

                        for key in current_data:
                            current_data[key] = current_data[key][1:]
    except Exception as e:
        print(f"Serial error: {e}")

def handle_client(client_socket):
    request = client_socket.recv(1024).decode()
    if "GET /data" in request:
        response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
        response += json.dumps(sensor_data)
    else:
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
        response += html_content
    client_socket.sendall(response.encode())
    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.68.110", 2010))
    server_socket.listen(5)
    print("Server running at http://192.168.68.110:2010/")
    while True:
        client_socket, _ = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

# Run the serial reader and server in separate threads
threading.Thread(target=read_serial_data, daemon=True).start()
start_server()
