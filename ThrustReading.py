import serial
import pandas as pd
import os
import time
import socket
import numpy as np

arm = 45.5

# Functions
def value_to_grams(value): # Convert raw sensor value to grams
    return 5.5/arm*0.00522*float(value)

def has_internet(host="8.8.8.8", port=53, timeout=1): # Check internet connectivity
    """Return True if we can reach the internet (DNS server), else False."""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError: # Network is unreachable
        print("No internet connection.") # May never be seen
        return False

# CSV file
filename = 'Prop_16VThrusts.csv'

#  PWM label
PWM = int(input('PWM level:\t'))
columb_label = f"{PWM}"  # Create column label based off PWM value

k = 0
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

    # Ensure the column for this weight exists
    if columb_label not in df.columns: # Columb not exist -> create it
        print(f"Creating new column: {columb_label}")
        time.sleep(1)  # Wait a bit for user to read the message
        df[columb_label] = pd.Series(dtype='float')
    else:  # Clear any existing values in that column
        print(f"Clearing existing values in column: {columb_label}")
        time.sleep(1)  # Wait a bit for user to read the message
        df.loc[:, columb_label] = np.nan
        
    # Configure serial
    ser2 = serial.Serial(port='/dev/ttyS0', baudrate=115200, timeout=1)
    while has_internet():
        line = ser2.readline()
        if line:
                # Wait for ESC to spin up
                print("Waiting for ESC to spin up...")
                # Send PWM value to ESC to prevent stall
                tare = line
                tare = value_to_grams(tare.decode(errors='ignore').strip())
                for t in range(5):
                    PWM_wind = int(round(float(PWM-1000)*(t+1)/5))+1000
                    print(f'PWM = {PWM_wind}')
                    ser2.write(PWM_wind.to_bytes(2, "big", signed=False)) # Send PWM value to ESC 
                    time.sleep(3)
                time.sleep(1)
                ser2.close()
                ser2 = serial.Serial(port='/dev/ttyS0', baudrate=115200, timeout=1)
                break
    while has_internet():
        line = ser2.readline()
        if line:
            value = line.decode(errors='ignore').strip()
            grams = (value_to_grams(value)- tare)
            print(f'grams:{grams}\tobtained:{value_to_grams(value)}\ttare:{tare}')
            df.loc[k, columb_label] = grams # Write to structured DataFrame
            k = k + 1 # Increment row counter

        # Send PWM value to ESC to prevent stall
        ser2.write(PWM.to_bytes(2, "big", signed=False)) # Send PWM value to ESC 

        if k >= 100: # Collect 100 readings then stop
            break

finally:
    df.to_csv(filename, index=False)
    try:
        PWM = 1000  # Failsafe PWM
        ser2.write(PWM.to_bytes(2, "big", signed=False)) # Send PWM value to ESC (Failsafe 2)
    except NameError:
        pass
    ser2.close()

