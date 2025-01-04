import serial
import pywt
import numpy as np

# Open serial connection to Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Adjust the port if necessary

# Initialize empty lists to store current values
ground_current = []
phc_current = []
phb_current = []
pha_current = []

# Constants for fault detection
CONSTANT = 50  # Threshold value for fault detection
NEUTRAL = 2    # Neutral current threshold

# Function to perform DWT using db4 wavelet at level 1 and extract peak values
def perform_dwt(data):
    # Apply DWT with db4 wavelet and level 1
    coeffs = pywt.dwt(data, 'db4')  # db4 wavelet, level 1
    cA, cD = coeffs  # Approximation and Detail coefficients
    
    # Extract peak values (maximum absolute value)
    peak_approx = np.max(np.abs(cA))
    peak_detail = np.max(np.abs(cD))
    
    return peak_approx, peak_detail

# Function to determine fault type
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
    if m > CONSTANT and n < CONSTANT and p > CONSTANT:
        if q > NEUTRAL:
            return "Double Line to Ground Fault (AC-G) Detected"
        else:
            return "Line to Line Fault Between Phase A and C Detected"
    if m < CONSTANT and n > CONSTANT and p > CONSTANT:
        if q > NEUTRAL:
            return "Double Line to Ground Fault (BC-G) Detected"
        else:
            return "Line to Line Fault Between Phase B and C Detected"
    if m > CONSTANT and n < CONSTANT and p < CONSTANT:
        if q > NEUTRAL:
            return "Single Line to Ground Fault in Phase A Detected"
    if m < CONSTANT and n > CONSTANT and p < CONSTANT:
        if q > NEUTRAL:
            return "Single Line to Ground Fault in Phase B Detected"
    if m < CONSTANT and n < CONSTANT and p > CONSTANT:
        if q > NEUTRAL:
            return "Single Line to Ground Fault in Phase C Detected"
    if m < CONSTANT and n < CONSTANT and p < CONSTANT:
        if q < NEUTRAL:
            return "No Fault Detected. System is Normal"
    return "Unknown Fault Detected"

# Read data from Arduino in real-time
while True:
    if ser.in_waiting > 0:
        # Read line from Arduino and parse the CSV data
        data = ser.readline().decode('utf-8').strip()
        values = data.split(',')
        
        if len(values) == 7:
            # Convert current values to floats (ignoring voltage for now)
            ground_current.append(float(values[0]))
            phc_current.append(float(values[1]))
            phb_current.append(float(values[2]))
            pha_current.append(float(values[3]))

            # Perform DWT on current values
            if len(ground_current) >= 10:  # Wait until we have enough data
                # Apply DWT to each current and extract peak values
                peak_approx_ground, peak_detail_ground = perform_dwt(ground_current)
                peak_approx_phc, peak_detail_phc = perform_dwt(phc_current)
                peak_approx_phb, peak_detail_phb = perform_dwt(phb_current)
                peak_approx_pha, peak_detail_pha = perform_dwt(pha_current)

                # Calculate max values for fault detection
                m = 10 * peak_detail_pha
                n = 10 * peak_detail_phb
                p = 10 * peak_detail_phc
                q = 10 * peak_detail_ground

                # Determine the fault type
                fault_message = detect_fault(m, n, p, q)

                # Print peak values and fault message
                print("\n=== Peak Values ===")
                print(f"Ground Current: Approx = {peak_approx_ground:.2f}, Detail = {peak_detail_ground:.2f}")
                print(f"Phase A Current: Approx = {peak_approx_pha:.2f}, Detail = {peak_detail_pha:.2f}")
                print(f"Phase B Current: Approx = {peak_approx_phb:.2f}, Detail = {peak_detail_phb:.2f}")
                print(f"Phase C Current: Approx = {peak_approx_phc:.2f}, Detail = {peak_detail_phc:.2f}")
                print("\nFault Detection:")
                print(fault_message)

                # Clear the current lists to process the next set of data
                ground_current = ground_current[1:]
                phc_current = phc_current[1:]
                phb_current = phb_current[1:]
                pha_current = pha_current[1:]
