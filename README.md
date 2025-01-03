# Distribution Line Monitoring System

A project developed for real-time monitoring of electrical distribution lines, built with Arduino and Python. The system measures voltage and current across different phases, providing data through a web interface for visualization.

## Features

- **Real-Time Monitoring**: Measures voltage and current for multiple phases.
- **Web Interface**: Displays live data with a clean and modern interface.
- **Fault Detection**: Includes status updates and fault detection mechanisms.
- **Data Communication**: Integrates Arduino with Python for efficient serial communication.

## Table of Contents

- [Overview](#overview)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
- [Web Interface](#web-interface)
- [Contributors](#contributors)

## Overview

This project monitors the voltage and current of distribution lines using ZMPT101B sensors and presents the readings through a web interface. It is designed to enhance operational visibility for distribution line operators and researchers.

## Hardware Requirements

- **Arduino Board** (e.g., Arduino Uno/Nano)
- **ZMPT101B Voltage Sensors**
- **ACS712 Current Sensors**
- Breadboard, jumper wires, and power supply.

## Software Requirements

- Arduino IDE
- Python 3.x
- Python Libraries:
  - `serial`
  - `socket`
  - `threading`
  - `json`

## Project Structure


## How to Run

### 1. Setup Arduino
- Connect the ZMPT101B and ACS712 sensors to the Arduino as per the circuit diagram.
- Upload the `Arduino_Code.ino` file to the Arduino using Arduino IDE.

### 2. Configure Python Server
- Update the `arduino_port` variable in `server.py` with your Arduino's serial port (e.g., `/dev/ttyUSB0`).
- Install the required Python libraries:
  ```bash
  pip install pyserial
