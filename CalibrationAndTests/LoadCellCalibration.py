import serial
import pandas as pd
import os
import numpy as np
# Function to convert pounds to grams
def pounds_to_grams(pounds):
    return pounds * 453.592

# CSV file
filename = 'CalibrationAndTests\\CalibrationReadings.csv'

# Convert a number to a string and use it as the weight_label

grams_inp = float(input('Grams:\t'))
pound_inp = pounds_to_grams(float(input('Pounds:\t')))
weight_in_grams = pound_inp + grams_inp
weight_label = f"{weight_in_grams:.2f}"  # Convert to grams and format as a string
col = str(weight_label)

# Configure serial
ser = serial.Serial(port='/dev/ttyS0', baudrate=115200, timeout=1)

values = []
n = 100 #length
try:
    # Load existing CSV or create a new one
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()
        df.to_csv(filename, index=False)

    # Ensure the column for this weight exists
    if col not in df.columns: 
        df[col] = pd.Series(dtype='float')
    else:  # Clear any existing values in that column
        df.loc[:, col] = np.nan
    print('Data collection begining')
    while len(values) < n:
        line = ser.readline()
        if line:
            val = float(line.decode(errors='ignore').strip())
            print(val)
            values.append(val)

finally:
    df[col] = pd.Series(values)
    df.to_csv(filename, index=False) # Save back to CSV
    ser.close()

