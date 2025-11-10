import serial
import pandas as pd
import os

# Function to convert pounds to grams
def pounds_to_grams(pounds):
    return pounds * 453.592

# Configure serial
ser = serial.Serial(port='/dev/ttyS0', baudrate=115200, timeout=1)

# CSV file
filename = 'readings.csv'

# Convert a number to a string and use it as the weight_label
weight_in_grams = 0
weight_label = f"{weight_in_grams:.2f}"  # Convert to grams and format as a string
col = str(weight_label)
k = 0

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
        df.loc[:, col] = None
    print('Data collection begining')
    while True:
        line = ser.readline()
        if line:
            value = line.decode(errors='ignore').strip()
            print(value)

            # Write/overwrite latest value in this weight's column on the single row
            df.loc[k, col] = value
            k = k + 1
            # Save back to CSV

finally:
    df.to_csv(filename, index=False)
    ser.close()
