# Coded by Raafiu Ashiquzzaman Mahmood 2010732
import numpy as np
import pandas as pd
import pywt
import matplotlib.pyplot as plt

# Load Data from CSV File
filename = 'TwoPhaseGround.csv'  
data = pd.read_csv(filename, header=None)

# Assigning columns to phases
R = data.iloc[:, 0].values  # Phase A (Column 1)
B = data.iloc[:, 1].values  # Phase B (Column 2)
Y = data.iloc[:, 2].values  # Phase C (Column 3)
N = data.iloc[:, 3].values  # Ground (Column 4)

# Applying Wavelet Decomposition of Current Reading
def wavelet_decomposition(signal):
    coeffs = pywt.wavedec(signal, 'db4', level=1)
    return coeffs[1]  # Detail coefficients (Level 1)

coefA = wavelet_decomposition(R)
coefB = wavelet_decomposition(B)
coefC = wavelet_decomposition(Y)
coefN = wavelet_decomposition(N)
# Max Value of Coefficients
m = max(coefA)
n = max(coefB)
p = max(coefC)
q = max(coefN)

print('Max Values:')
print(f'Phase A: {m}')
print(f'Phase B: {n}')
print(f'Phase C: {p}')
print(f'Ground: {q}')


# Conditions for Fault Types
constant = 200
neutral = 2

if m > constant and n > constant and p > constant and q > neutral:
    print("Three Phase to Ground Fault is Detected")
elif m > constant and n > constant and p > constant and q < neutral:
    print("Three Phase Fault is Detected")
elif m > constant and n > constant and p < constant and q > neutral:
    print("Double Line to Ground Fault (AB-G) is Detected")
elif m > constant and n < constant and p > constant and q > neutral:
    print("Double Line to Ground Fault (AC-G) is Detected")
elif m < constant and n > constant and p > constant and q > neutral:
    print("Double Line to Ground Fault (BC-G) is Detected")
elif m > constant and n > constant and p < constant and q < neutral:
    print("Line to Line Fault Between Phase A and B is Detected")
elif m > constant and n < constant and p > constant and q < neutral:
    print("Line to Line Fault Between Phase A and C is Detected")
elif m < constant and n > constant and p > constant and q < neutral:
    print("Line to Line Fault Between Phase B and C is Detected")
elif m > constant and n < constant and p < constant and q > neutral:
    print("Single Line to Ground Fault in Phase A is Detected")
elif m < constant and n > constant and p < constant and q > neutral:
    print("Single Line to Ground Fault in Phase B is Detected")
elif m < constant and n < constant and p > constant and q > neutral:
    print("Single Line to Ground Fault in Phase C is Detected")
elif m < constant and n < constant and p < constant and q < neutral:
    print("No Fault is Detected. System is Normal")

# Graph Plot
plt.figure(figsize=(10, 8))

plt.subplot(4, 1, 1)
plt.plot(coefA)
plt.title('Detail Coefficients for Phase A')
plt.xlabel('Coefficient Index')
plt.ylabel('Amplitude')

plt.subplot(4, 1, 2)
plt.plot(coefB)
plt.title('Detail Coefficients for Phase B')
plt.xlabel('Coefficient Index')
plt.ylabel('Amplitude')

plt.subplot(4, 1, 3)
plt.plot(coefC)
plt.title('Detail Coefficients for Phase C')
plt.xlabel('Coefficient Index')
plt.ylabel('Amplitude')

plt.subplot(4, 1, 4)
plt.plot(coefN)
plt.title('Detail Coefficients for Ground')
plt.xlabel('Coefficient Index')
plt.ylabel('Amplitude')

plt.tight_layout()
plt.show()






