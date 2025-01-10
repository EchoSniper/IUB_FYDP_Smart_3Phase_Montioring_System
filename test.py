# Adding Libraries 
import serial
import socket
import threading
import json
import time
import pywt
import numpy as np
import csv

# Serial Port Communication Setup
arduino_port = '/dev/ttyUSB0'  
baud_rate = 9600

# Constants for fault detection
CONSTANT = 50  # For Phase Constant That might need to be changed based on requirement
NEUTRAL = 2    # Neutral Constant That might need to be changed based on requirement

# Constants For Data Receiving 
sensor_data = {
    "Ground_Current": 0.0,
    "Phase_C_Current": 0.0,
    "Phase_B_Current": 0.0,
    "Phase_A_Current": 0.0,
    "Phase_A_Voltage": 0.0,
    "Phase_B_Voltage": 0.0,
    "Phase_C_Voltage": 0.0,
    "Fault_Type": "No Fault Detected",
    "Status": "Normal",
    "DWT_Peak_A": 0.0,
    "DWT_Peak_B": 0.0,
    "DWT_Peak_C": 0.0,
    "DWT_Peak_Ground": 0.0
}

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

        .dwt-container {
            margin-top: 20px;
            display: flex;
            justify-content: center;
            gap: 20px;
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
        }

        .dwt-reading span {
            font-weight: bold;
            font-size: 1.4rem;
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

        <div class="dwt-container">
            <div class="dwt-reading">DWT Peak for Phase A: <span id="dwtPeakA">--</span></div>
            <div class="dwt-reading">DWT Peak for Phase B: <span id="dwtPeakB">--</span></div>
            <div class="dwt-reading">DWT Peak for Phase C: <span id="dwtPeakC">--</span></div>
            <div class="dwt-reading">DWT Peak for Ground: <span id="dwtPeakGround">--</span></div>
        </div>
    </div>

    <script>
        // DWT-based fault detection logic
        function evaluateFault(data) {
            let status = "Normal";
            let faultType = "No Fault Detected";

            // Check for overcurrent faults
            if (data.Phase_A_Current > 100 || data.Phase_B_Current > 100 || data.Phase_C_Current > 100) {
                status = "Fault Detected";
                let overcurrentPhases = [];
                if (data.Phase_A_Current > 100) overcurrentPhases.push("Phase A");
                if (data.Phase_B_Current > 100) overcurrentPhases.push("Phase B");
                if (data.Phase_C_Current > 100) overcurrentPhases.push("Phase C");
                faultType = `Overcurrent Fault: ${overcurrentPhases.join(", ")}`;
            }

            // Check for undervoltage faults
            else if (data.Phase_A_Voltage < 200 || data.Phase_B_Voltage < 200 || data.Phase_C_Voltage < 200) {
                status = "Fault Detected";
                let undervoltPhases = [];
                if (data.Phase_A_Voltage < 200) undervoltPhases.push("Phase A");
                if (data.Phase_B_Voltage < 200) undervoltPhases.push("Phase B");
                if (data.Phase_C_Voltage < 200) undervoltPhases.push("Phase C");
                faultType = `Undervoltage Fault: ${undervoltPhases.join(", ")}`;
            }

            // Check for overvoltage faults
            else if (data.Phase_A_Voltage > 250 || data.Phase_B_Voltage > 250 || data.Phase_C_Voltage > 250) {
                status = "Fault Detected";
                let overvoltPhases = [];
                if (data.Phase_A_Voltage > 250) overvoltPhases.push("Phase A");
                if (data.Phase_B_Voltage > 250) overvoltPhases.push("Phase B");
                if (data.Phase_C_Voltage > 250) overvoltPhases.push("Phase C");
                faultType = `Overvoltage Fault: ${overvoltPhases.join(", ")}`;
            }

            // Update the status and fault type
            document.getElementById("status").innerText = status;
            document.getElementById("faultType").innerText = faultType;
        }

        async function fetchData() {
            try {
                const response = await fetch("/data");
                const data = await response.json();

                // Update readings
                document.getElementById("voltageA").innerText = data.Phase_A_Voltage.toFixed(2);
                document.getElementById("voltageB").innerText = data.Phase_B_Voltage.toFixed(2);
                document.getElementById("voltageC").innerText = data.Phase_C_Voltage.toFixed(2);
                document.getElementById("currentA").innerText = data.Phase_A_Current.toFixed(2);
                document.getElementById("currentB").innerText = data.Phase_B_Current.toFixed(2);
                document.getElementById("currentC").innerText = data.Phase_C_Current.toFixed(2);

                // Apply fault detection logic
                evaluateFault(data);

                // Display DWT peak values
                document.getElementById("dwtPeakA").innerText = data.DWT_Peak_A.toFixed(2);
                document.getElementById("dwtPeakB").innerText = data.DWT_Peak_B.toFixed(2);
                document.getElementById("dwtPeakC").innerText = data.DWT_Peak_C.toFixed(2);
                document.getElementById("dwtPeakGround").innerText = data.DWT_Peak_Ground.toFixed(2);

                // Update the clock
                const currentTime = new Date();
                document.getElementById("clock").innerText = "Last Checked: " + currentTime.toLocaleTimeString();
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        }

        // Fetch data every second
        setInterval(fetchData, 1000);
    </script>
</body>
</html>
""" 
def perform_dwt(data):
    coeffs = pywt.dwt(data, 'db4')
    cA, cD = coeffs
    return np.max(np.abs(cA)), np.max(np.abs(cD))

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
                        sensor_data["Status"] = "Fault Detected" if fault != "No Fault Detected" else "Normal"

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


#Data For Further Analysis 
#Naming  CSV files
wavelet_csv_file = "wavelet_data.csv"
waveform_csv_file = "waveform_data.csv"

# Writing Headers to CSV files 
def initialize_csv():
    with open(wavelet_csv_file, "w", newline="") as wf:
        wavelet_writer = csv.writer(wf)
        wavelet_writer.writerow(["PhaseA_cA", "PhaseA_cD", "PhaseB_cA", "PhaseB_cD", 
                                  "PhaseC_cA", "PhaseC_cD", "Ground_cA", "Ground_cD"])
    
    with open(waveform_csv_file, "w", newline="") as wf:
        waveform_writer = csv.writer(wf)
        waveform_writer.writerow(["PhaseA", "PhaseB", "PhaseC", "Ground"])

# Save wavelet transformation data to CSV
def save_wavelet_data(cA_a, cD_a, cA_b, cD_b, cA_c, cD_c, cA_g, cD_g):
    with open(wavelet_csv_file, "a", newline="") as wf:
        wavelet_writer = csv.writer(wf)
        wavelet_writer.writerow([cA_a, cD_a, cA_b, cD_b, cA_c, cD_c, cA_g, cD_g])

# Save waveform data to CSV
def save_waveform_data(phaseA, phaseB, phaseC, ground):
    with open(waveform_csv_file, "a", newline="") as wf:
        waveform_writer = csv.writer(wf)
        waveform_writer.writerow([phaseA, phaseB, phaseC, ground])

# Modify the read_serial_data function to include CSV logging
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
                        cA_a, cD_a = perform_dwt(current_data["PhaseA"])
                        cA_b, cD_b = perform_dwt(current_data["PhaseB"])
                        cA_c, cD_c = perform_dwt(current_data["PhaseC"])
                        cA_g, cD_g = perform_dwt(current_data["Ground"])

                        # Save wavelet data to CSV
                        save_wavelet_data(cA_a, cD_a, cA_b, cD_b, cA_c, cD_c, cA_g, cD_g)

                        # Save waveform data to CSV
                        save_waveform_data(
                            current_data["PhaseA"][-1],
                            current_data["PhaseB"][-1],
                            current_data["PhaseC"][-1],
                            current_data["Ground"][-1]
                        )

                        # Detect faults
                        fault = detect_fault(10 * cA_a, 10 * cA_b, 10 * cA_c, 10 * cA_g)
                        sensor_data["Fault_Type"] = fault
                        sensor_data["Status"] = "Fault Detected" if fault != "No Fault Detected" else "Normal"

                        # Keep the last few entries for continuity
                        for key in current_data:
                            current_data[key] = current_data[key][1:]
    except Exception as e:
        print(f"Serial error: {e}")

# Initialize CSV files
initialize_csv()
