import serial
import socket
import threading
import json
import time

# Serial communication setup
arduino_port = '/dev/ttyUSB0'  # Update this based on your system
baud_rate = 9600
sensor_data = {
    "Phase_A_Voltage": 0.0,
    "Phase_A_Current": 0.0,
    "Phase_B_Voltage": 0.0,
    "Phase_B_Current": 0.0,
    "Phase_C_Voltage": 0.0,
    "Phase_C_Current": 0.0
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
        body { font-family: Arial, sans-serif; background-color: #333; color: #fff; text-align: center; padding: 20px; }
        .container { margin: 0 auto; width: 80%; max-width: 600px; }
        .data { margin: 10px 0; }
        .data span { font-weight: bold; color: #0f0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Distribution Line Monitoring</h1>
        <div class="data">Phase A Voltage: <span id="voltageA">--</span> V</div>
        <div class="data">Phase A Current: <span id="currentA">--</span> A</div>
        <div class="data">Phase B Voltage: <span id="voltageB">--</span> V</div>
        <div class="data">Phase B Current: <span id="currentB">--</span> A</div>
        <div class="data">Phase C Voltage: <span id="voltageC">--</span> V</div>
        <div class="data">Phase C Current: <span id="currentC">--</span> A</div>
    </div>
    <script>
        async function fetchData() {
            try {
                const response = await fetch('/data');
                const data = await response.json();
                document.getElementById('voltageA').innerText = data.Phase_A_Voltage.toFixed(2);
                document.getElementById('currentA').innerText = data.Phase_A_Current.toFixed(2);
                document.getElementById('voltageB').innerText = data.Phase_B_Voltage.toFixed(2);
                document.getElementById('currentB').innerText = data.Phase_B_Current.toFixed(2);
                document.getElementById('voltageC').innerText = data.Phase_C_Voltage.toFixed(2);
                document.getElementById('currentC').innerText = data.Phase_C_Current.toFixed(2);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        setInterval(fetchData, 1000);
    </script>
</body>
</html>
"""

# Web server configuration
ip_address = "0.0.0.0"
port = 2010

def read_serial_data():
    """Read data from the Arduino and update global sensor_data."""
    global sensor_data
    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        print("Connected to Arduino...")
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"Received: {line}")
                values = list(map(float, line.split(",")))
                if len(values) == 6:
                    sensor_data["Phase_A_Voltage"] = values[0]
                    sensor_data["Phase_A_Current"] = values[1]
                    sensor_data["Phase_B_Voltage"] = values[2]
                    sensor_data["Phase_B_Current"] = values[3]
                    sensor_data["Phase_C_Voltage"] = values[4]
                    sensor_data["Phase_C_Current"] = values[5]
    except Exception as e:
        print(f"Serial error: {e}")

def handle_client(client_socket):
    """Handle client HTTP requests."""
    request = client_socket.recv(1024).decode()
    if "GET /data" in request:
        response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
        response += json.dumps(sensor_data)
    else:
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
        response += html_content
    client_socket.sendall(response.encode())
    client_socket.close()

def start_web_server():
    """Start the web server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip_address, port))
    server.listen(5)
    print(f"Server running on {ip_address}:{port}...")
    while True:
        client_socket, _ = server.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    threading.Thread(target=read_serial_data, daemon=True).start()
    start_web_server()
