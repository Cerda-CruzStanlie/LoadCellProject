import serial
import pandas as pd
import os
import time
import socket
import numpy as np
import argparse

arm = 45.5

# Functions
def value_to_grams(value): # Convert raw sensor value to grams
    return 15.5/arm*(0.00522*float(value)+1.65*1000)

def has_internet(host="8.8.8.8", port=53, timeout=1): # Check internet connectivity
    """Return True if we can reach the internet (DNS server), else False."""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError: # Network is unreachable
        print("No internet connection.") # May never be seen
        return False

# CSV file
filename = 'Test'

#  PWM label
PWM = int(input('PWM level:\t'))
columb_label = f"Mass_{PWM}"  # Create column label for mass based off PWM value
current_label = f"Current_{PWM}"  # Create column label for current for this run
wind_label = f"WindSpeed_{PWM}"  # Wind speed recorded at end of this run

k = 0
Current = []
MForce = []
n = 100 #length
try:
    # Load existing CSV or create a new one
    if os.path.exists(filename): # Check if the file exists
        print(f"File {filename} exists, attempting to load.")
        time.sleep(1)  # Wait a bit for user to read the message
        try: # Load existing CSV file
            print(f"Loading existing CSV file: {filename}")
            time.sleep(1)  # Wait a bit for user to read the message
            df = pd.read_csv(filename)
        except pd.errors.EmptyDataError: # Handle empty CSV file
            print(f"CSV file is empty, creating new DataFrame.")
            time.sleep(1)  # Wait a bit for user to read the message
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()
        print(f"CSV file {filename} does not exist, creating a new one.")
        time.sleep(1)  # Wait a bit for user to read the message
        df.to_csv(filename, index=False)

    # Ensure the columns for this run exist (mass and current)
    for label in (columb_label, current_label):
        if label not in df.columns:
            print(f"Creating new column: {label}")
            time.sleep(0.3)
            df[label] = pd.Series(dtype='float')
        else:
            print(f"Clearing existing values in column: {label}")
            time.sleep(0.3)
            df.loc[:, label] = np.nan
        
    # Configure serial
    ser = serial.Serial(port='/dev/ttyS0', baudrate=115200, timeout=1)
    # spin‑up: grab initial reading and wind the ESC slowly so the motor doesn’t stall
    while has_internet():
        line = ser.readline()
        if line:
            print("Waiting for ESC to spin up...")
            tare = value_to_grams(line.decode(errors='ignore').strip())
            for t in range(5):
                PWM_wind = int(round(float(PWM-1000)*(t+1)/5))+1000
                print(f'PWM = {PWM_wind}')
                ser.write(PWM_wind.to_bytes(2, "big", signed=False))
                time.sleep(3)
            time.sleep(1)
            # reopen to flush any junk left in the buffer
            ser.close()
            ser = serial.Serial(port='/dev/ttyS0', baudrate=115200, timeout=1)
            break

    # main acquisition loop — read two lines per iteration
    while has_internet():
        line = ser.readline()
        if not line:
            continue
        val1 = line.decode(errors='ignore').strip()

        line = ser.readline()
        if not line:
            continue
        val2 = line.decode(errors='ignore').strip()

        grams = (value_to_grams(val1) - tare)
        print(f'grams:{grams}\tobtained:{value_to_grams(val1)}\ttare:{tare}')
        MForce.append(grams)
        Current.append(val2)
        k += 1

        # Send PWM value to ESC to prevent stall
        ser.write(PWM.to_bytes(2, "big", signed=False))

        if k >= 100: # Collect 100 readings then stop
            break

finally:
    # Write mass and current side-by-side for this run
    df[columb_label] = pd.Series(MForce)
    df[current_label] = pd.Series(Current)

    # Ask user for end-of-experiment wind speed and store it for this run
    wind_speed = np.nan
    if len(MForce) > 0:
        while True:
            wind_input = input("Enter anemometer wind speed at end of run (m/s):\t").strip()
            try:
                wind_speed = float(wind_input)
                break
            except ValueError:
                print("Invalid number. Please enter wind speed as a numeric value (example: 3.25).")

    if wind_label not in df.columns:
        df[wind_label] = pd.Series(dtype='float')
    else:
        df.loc[:, wind_label] = np.nan

    if not np.isnan(wind_speed):
        df[wind_label] = pd.Series([wind_speed] * len(MForce))

    try:
        PWM = 1000  # Failsafe PWM
        ser.write(PWM.to_bytes(2, "big", signed=False)) # Send PWM value to ESC (Failsafe 2)
    except NameError:
        pass
    ser.close()
    
    df.to_csv(filename, index=False)

