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
    "Phase_C_Current": 0.0
}

# Web server configuration
ip_address = "192.168.68.110"  # Adjust to your server IP
port = 2010

def read_serial_data():
    """Continuously read data from the Arduino and update the global sensor_data dictionary."""
    global sensor_data
    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        print("Connected to Arduino...")
        while True:
            try:
                # Read a line from the serial port
                line = ser.readline().decode('utf-8').strip()
                if line:
                    # Display the raw serial data on the console
                    print(f"Raw Serial Data: {line}")

                    # Parse the serial data
                    values = list(map(float, line.split(",")))
                    if len(values) == 6:
                        # Update sensor data
                        sensor_data["Phase_A_Voltage"] = max(0.0, values[0])  # Replace negative values with 0
                        sensor_data["Phase_A_Current"] = values[1]
                        sensor_data["Phase_B_Voltage"] = max(0.0, values[2])  # Replace negative values with 0
                        sensor_data["Phase_B_Current"] = values[3]
                        sensor_data["Phase_C_Voltage"] = max(0.0, values[4])  # Replace negative values with 0
                        sensor_data["Phase_C_Current"] = values[5]

                        # Display parsed sensor data
                        print("Parsed Data:", sensor_data)
            except Exception as e:
                print(f"Error parsing serial data: {e}")
            time.sleep(0.1)
    except Exception as e:
        print(f"Error connecting to serial port: {e}")

def handle_client(client_socket):
    """Handle incoming HTTP requests from clients."""
    request = client_socket.recv(1024).decode()
    if "GET /data" in request:
        client_socket.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
        client_socket.sendall(json.dumps(sensor_data).encode())
    else:
        client_socket.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n")
        client_socket.sendall(b"<h1>404 Not Found</h1>")
    client_socket.close()

def start_web_server():
    """Start the web server to serve the sensor data."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip_address, port))
    server.listen(5)
    print(f"Server listening on {ip_address}:{port}...")
    
    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    # Start serial reading in a separate thread
    serial_thread = threading.Thread(target=read_serial_data)
    serial_thread.start()

    # Start web server
    start_web_server()
