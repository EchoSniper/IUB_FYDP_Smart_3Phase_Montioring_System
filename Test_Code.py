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
        /* Styling code here */
    </style>
</head>
<body>
    <div class="container">
        <!-- Content here -->
        <h3>Phase A Voltage: <span id="voltageA"></span> V</h3>
        <h3>Phase A Current: <span id="currentA"></span> A</h3>
        <h3>Phase B Voltage: <span id="voltageB"></span> V</h3>
        <h3>Phase B Current: <span id="currentB"></span> A</h3>
        <h3>Phase C Voltage: <span id="voltageC"></span> V</h3>
        <h3>Phase C Current: <span id="currentC"></span> A</h3>
        <h3>Status: <span id="status"></span></h3>
        <h3>Fault Type: <span id="faultType"></span></h3>
        <div id="clock"></div>
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
                    if len(values) == 6:  # Ignore ground current, and use values for Phase A, B, and C
                        sensor_data["Phase_A_Voltage"] = max(0, values[0] if values[0] >= 50 else 0)
                        sensor_data["Phase_A_Current"] = values[1]
                        sensor_data["Phase_B_Voltage"] = max(0, values[2] if values[2] >= 50 else 0)
                        sensor_data["Phase_B_Current"] = values[3]
                        sensor_data["Phase_C_Voltage"] = max(0, values[4] if values[4] >= 50 else 0)
                        sensor_data["Phase_C_Current"] = values[5]
            except ValueError as e:
                print("Error reading data:", e)
            time.sleep(1)
    except serial.SerialException as e:
        print(f"Error connecting to Arduino: {e}")

def handle_client(client_socket):
    """Handle incoming client requests."""
    try:
        request = client_socket.recv(1024).decode('utf-8')
        if request.startswith("GET /data"):  # Check if the request is for data
            client_socket.sendall("HTTP/1.1 200 OK\r\n".encode())
            client_socket.sendall("Content-Type: application/json\r\n\r\n".encode())
            client_socket.sendall(json.dumps(sensor_data).encode())  # Send sensor data as JSON
        else:
            client_socket.sendall("HTTP/1.1 200 OK\r\n".encode())
            client_socket.sendall("Content-Type: text/html\r\n\r\n".encode())
            client_socket.sendall(html_content.encode())  # Send the HTML page
    except Exception as e:
        print("Error handling client:", e)
    finally:
        client_socket.close()

def start_server():
    """Start the web server to serve the data."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((ip_address, port))
        server_socket.listen(5)
        print(f"Server listening on {ip_address}:{port}")
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            handle_client(client_socket)

# Start both the serial data reading and web server
if __name__ == "__main__":
    # Start serial reading in a separate thread
    threading.Thread(target=read_serial_data, daemon=True).start()
    # Start web server
    start_server()
