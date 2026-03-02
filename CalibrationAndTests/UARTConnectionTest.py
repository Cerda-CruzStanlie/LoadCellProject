import serial
import time

# === CONFIGURATION ===
PORT = '/dev/ttyS0'       # Change this to your serial port (e.g., '/dev/ttyUSB0' on Linux/Mac)
BAUD = 115200       # Must match your ESP32 UART baud rate
TIMEOUT = 1         # seconds

# === MAIN LOOP ===
def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
        print(f"Connected to {PORT} at {BAUD} baud.")
        time.sleep(2)  # Wait for ESP32 to reset (optional)
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode(errors='ignore').strip()
                if line:
                    print(f"Received: {line}")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        try:
            ser.close()
        except:
            pass

if __name__ == "__main__":
    main()

