#Adding Libraries 
import serial
import socket
import threading
import json
import time
import pywt
import numpy as np
import csv
import os 
# Serial Port Communication Setup
arduino_port = '/dev/ttyUSB0'  
baud_rate = 9600

# Constants for fault detection
CONSTANT = 50  # For Phase Constant That might need to be changed based on requirement
NEUTRAL = 2    # Neutral Constant That might need to be changed based on requirement

# Constants For Data Receiving 
# Update sensor_data to include DWT results
sensor_data = {
    "Ground_Current": 0.0,
    "Phase_C_Current": 0.0,
    "Phase_B_Current": 0.0,
    "Phase_A_Current": 0.0,
    "Phase_A_Voltage": 0.0,
    "Phase_B_Voltage": 0.0,
    "Phase_C_Voltage": 0.0,
    "DWT_Peak_A": 0.0,
    "DWT_Peak_B": 0.0,
    "DWT_Peak_C": 0.0,
    "DWT_Peak_Ground": 0.0,
    "Fault_Type": "No Fault Detected",
    "Status": "Normal"
}

# Update the read_serial_data function to calculate and update DWT readings
# Update the read_serial_data function to include maximum current values during DWT analysis
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
                        # Perform DWT on each phase and ground
                        cA_a, cD_a, max_current_a = perform_dwt(current_data["PhaseA"])
                        cA_b, cD_b, max_current_b = perform_dwt(current_data["PhaseB"])
                        cA_c, cD_c, max_current_c = perform_dwt(current_data["PhaseC"])
                        cA_g, cD_g, max_current_g = perform_dwt(current_data["Ground"])

                        # Update sensor_data with DWT results and maximum current values
                        sensor_data["DWT_Peak_A"] = cA_a
                        sensor_data["DWT_Peak_B"] = cA_b
                        sensor_data["DWT_Peak_C"] = cA_c
                        sensor_data["DWT_Peak_Ground"] = cA_g
                        sensor_data["Max_Current_A"] = max_current_a
                        sensor_data["Max_Current_B"] = max_current_b
                        sensor_data["Max_Current_C"] = max_current_c
                        sensor_data["Max_Current_Ground"] = max_current_g

                        # Detect faults using DWT results
                        fault = detect_fault(cA_a, cA_b, cA_c, cA_g)
                        sensor_data["Fault_Type"] = fault
                        sensor_data["Status"] = "Fault Detected" if fault != "No Fault Detected" else "Normal"

                        # Keep the last few entries for continuity
                        for key in current_data:
                            current_data[key] = current_data[key][1:]
    except Exception as e:
        print(f"Serial error: {e}")


def perform_dwt(data):
    # Perform DWT and return the wavelet coefficients and the maximum current value
    coeffs = pywt.dwt(data, 'db4')
    cA, cD = coeffs
    max_current = np.max(np.abs(data))  # Get the maximum current value during the DWT
    return np.max(np.abs(cA)), np.max(np.abs(cD)), max_current  # Return both DWT peaks and max current

#Return values are the peak values for 5 second time length 

# Function to Detect Fault
def detect_fault(m, n, p, q):
    if m > CONSTANT and n > CONSTANT and p > CONSTANT:
        if q > NEUTRAL:
            return "Three Phase to Ground Fault (ABC-G) Detected"
        else:
            return "Three Phase Fault (ABC) Detected"
    
    if m > CONSTANT and n > CONSTANT and p < CONSTANT:
        if q > NEUTRAL:
            return "Double Line to Ground Fault (AB-G) Detected"
        else:
            return "Line to Line Fault Between Phase A and B Detected"
    
    if m > CONSTANT and p > CONSTANT and n < CONSTANT:
        if q > NEUTRAL:
            return "Double Line to Ground Fault (AC-G) Detected"
        else:
            return "Line to Line Fault Between Phase A and C Detected"
    
    if n > CONSTANT and p > CONSTANT and m < CONSTANT:
        if q > NEUTRAL:
            return "Double Line to Ground Fault (BC-G) Detected"
        else:
            return "Line to Line Fault Between Phase B and C Detected"
    
    if m > CONSTANT and n < CONSTANT and p < CONSTANT:
        if q > NEUTRAL:
            return "Single Line to Ground Fault (A-G) Detected"
        else:
            return "No Fault Detected"
    
    if n > CONSTANT and m < CONSTANT and p < CONSTANT:
        if q > NEUTRAL:
            return "Single Line to Ground Fault (B-G) Detected"
        else:
            return "No Fault Detected"
    
    if p > CONSTANT and m < CONSTANT and n < CONSTANT:
        if q > NEUTRAL:
            return "Single Line to Ground Fault (C-G) Detected"
        else:
            return "No Fault Detected"
    
    return "No Fault Detected"
lock = threading.Lock()

import csv
import os

# Define the CSV filename
csv_filename = "sensor_data.csv"

# Define the header for the CSV file
csv_header = ["Ground_Current", "Phase_C_Current", "Phase_B_Current", "Phase_A_Current", 
              "Phase_A_Voltage", "Phase_B_Voltage", "Phase_C_Voltage", "DWT_Peak_A", 
              "DWT_Peak_B", "DWT_Peak_C", "DWT_Peak_Ground", "Max_Current_A", "Max_Current_B", 
              "Max_Current_C", "Max_Current_Ground", "Fault_Type", "Status"]

# Check if the file exists, if not create it and write the header
if not os.path.isfile(csv_filename):
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)

def save_to_csv():
    # This function assumes 'sensor_data' is a dictionary containing the current values
    try:
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write the data from the sensor_data dictionary
            row = [
                sensor_data["Ground_Current"],
                sensor_data["Phase_C_Current"],
                sensor_data["Phase_B_Current"],
                sensor_data["Phase_A_Current"],
                sensor_data["Phase_A_Voltage"],
                sensor_data["Phase_B_Voltage"],
                sensor_data["Phase_C_Voltage"],
                sensor_data["DWT_Peak_A"],
                sensor_data["DWT_Peak_B"],
                sensor_data["DWT_Peak_C"],
                sensor_data["DWT_Peak_Ground"],
                sensor_data["Max_Current_A"],
                sensor_data["Max_Current_B"],
                sensor_data["Max_Current_C"],
                sensor_data["Max_Current_Ground"],
                sensor_data["Fault_Type"],
                sensor_data["Status"]
            ]
            writer.writerow(row)
    except Exception as e:
        print(f"Error saving to CSV: {e}")


# Call save_to_csv in your loop where data is read and processed
# HTML / Website Content 
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
            font-family: 'Poppins', sans-serif;
            color: #ffffff;
            overflow-x: hidden;
            min-height: 100vh;
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
            font-weight: bold;
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
            border: 2px solid #0074D9;
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

        /* Added CSS for DWT Peaks */
        .dwt-container {
            display: flex;
            justify-content: space-between;
            width: 100%;
            gap: 15px;
            margin-bottom: 20px;
        }

        .dwt-reading {
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

        .dwt-reading span {
            font-size: 1.4rem;
            font-weight: bold;
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
        <img src="https://raw.githubusercontent.com/EchoSniper/IUB_FYDP_Smart_3Phase_Montioring_System/refs/heads/main/Logo.png" alt="IUB Logo" class="logo">
        <div class="content">
            <h1>Distribution Line Monitoring System</h1>
            <h2>Location: Independent University, Bangladesh</h2>
            <p>Constructed by "IUB EEE Grid Guardians"</p>
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
                <h3>Max Current Readings</h3>
                <div class="reading">Phase A Max Current: <span id="currentA">--</span> A</div>
                <div class="reading">Phase B Max Current: <span id="currentB">--</span> A</div>
                <div class="reading">Phase C Max Current: <span id="currentC">--</span> A</div>
            </div>
        </div>

        <!-- DWT Peak Values -->
        <div class="dwt-container">
            <div class="dwt-reading">DWT Peak Phase A: <span id="dwtPeakA">--</span></div>
            <div class="dwt-reading">DWT Peak Phase B: <span id="dwtPeakB">--</span></div>
            <div class="dwt-reading">DWT Peak Phase C: <span id="dwtPeakC">--</span></div>
            <div class="dwt-reading">DWT Peak Ground: <span id="dwtPeakGround">--</span></div>
        </div>

        <div class="status-container">
            <div class="status">Status: <span id="status">Normal</span></div>
            <div class="status">Fault Type: <span id="faultType">No Fault Detected</span></div>
        </div>
        <div class="clock" id="clock">Last Checked: 12:00:00</div>
    </div>

    <script>
        // DWT-based fault detection logic
        function evaluateFault(data) {
            let status = "Normal";
            let faultType = "No Fault Detected";

            // Check for faults based on DWT Peak values
            if (data.DWT_Peak_A > 50 && data.DWT_Peak_B > 50 && data.DWT_Peak_C > 50) {
                if (data.DWT_Peak_Ground > 2) {
                    status = "Fault Detected";
                    faultType = "Three Phase to Ground Fault (ABC-G) Detected";
                } else {
                    status = "Fault Detected";
                    faultType = "Three Phase Fault (ABC) Detected";
                }
            } else if (data.DWT_Peak_A > 50 && data.DWT_Peak_B > 50) {
                if (data.DWT_Peak_Ground > 2) {
                    status = "Fault Detected";
                    faultType = "Double Line to Ground Fault (AB-G) Detected";
                } else {
                    status = "Fault Detected";
                    faultType = "Line to Line Fault Between Phase A and B Detected";
                }
            }

            // Update UI
            document.getElementById("status").innerText = status;
            document.getElementById("faultType").innerText = faultType;
        }

    async function fetchData() {
        try {
            const response = await fetch("/data");  // Fetch data from backend
            const data = await response.json();

            // Apply condition for voltage values below 10
            const voltageA = data.Phase_A_Voltage < 10 ? 0 : data.Phase_A_Voltage;
            const voltageB = data.Phase_B_Voltage < 10 ? 0 : data.Phase_B_Voltage;
            const voltageC = data.Phase_C_Voltage < 10 ? 0 : data.Phase_C_Voltage;

            // Apply condition for current values below 0.1
            const currentA = data.Max_Current_A < 0.3 ? 0 : data.Max_Current_A;
            const currentB = data.Max_Current_B < 0.3 ? 0 : data.Max_Current_B;
            const currentC = data.Max_Current_C < 0.3 ? 0 : data.Max_Current_C;

            // Update voltage and current readings
            document.getElementById("voltageA").innerText = voltageA.toFixed(2);
            document.getElementById("voltageB").innerText = voltageB.toFixed(2);
            document.getElementById("voltageC").innerText = voltageC.toFixed(2);

            // Display maximum current readings
            document.getElementById("currentA").innerText = currentA.toFixed(2);
            document.getElementById("currentB").innerText = currentB.toFixed(2);
            document.getElementById("currentC").innerText = currentC.toFixed(2);

            // Update DWT Peak values
            document.getElementById("dwtPeakA").innerText = data.DWT_Peak_A.toFixed(2);
            document.getElementById("dwtPeakB").innerText = data.DWT_Peak_B.toFixed(2);
            document.getElementById("dwtPeakC").innerText = data.DWT_Peak_C.toFixed(2);
            document.getElementById("dwtPeakGround").innerText = data.DWT_Peak_Ground.toFixed(2);

            // Evaluate the fault status based on DWT Peaks
            evaluateFault(data);
        } catch (error) {
            console.error("Error fetching data:", error);
        }
    }


        // Fetch data every 3 seconds to update the display
        setInterval(fetchData, 3000);

        // Update the clock display every second
        setInterval(() => {
            document.getElementById("clock").innerText = `Last Checked: ${new Date().toLocaleTimeString()}`;
        }, 1000);
    </script>
</body>
</html>


"""
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

