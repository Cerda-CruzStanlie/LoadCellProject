# Load Cell Thrust Measurement Thrust Stand
Raspberry Pi–based load cell rig for thrust measurement and calibration.

Project Overview
- Measures thrust using a load cell and **HX711 amplifier**.
- Runs data acquisition on a ESP32 and sends it via serial link to Raspberry Pi.
- Logs readings to CSV and provides Python tools for calibration and plotting.
- Designed for undergraduate research and lab use (e.g., EDF / propeller testing).
You can use this repository to:
- Calibrate a new load cell.
- Run thrust tests at different PWM / throttle commands.
- Generate plots for reports and papers.
  
Demo / Screenshots

Photo of the rig.
  ![Load cell test stand](Images/ThrustStand.jpg)
  Screenshot of terminal or plot of thrust vs time.

Hardware
  Bullet list of components with links:
    Load cell specs
      HX711 board
      ESP32 / Pi model
      PSU, ESC, motor, etc.
  Mention wiring at a high level and link to a wiring diagram in /docs or /images.

Software & Repo Structure
  Short description of languages + main tools (Python, Arduino, etc.).
  Brief “what lives where”:
    src/ – data acquisition scripts
    calibration/ – calibration scripts/notebooks
    docs/ – diagrams, poster, etc.
    
Getting Started
  Prerequisites (OS, Python version, Arduino core, etc.).
  Installation (clone repo, install requirements).
  Configuration (edit a config file, serial port, calibration constant).

Usage
  How to:
    Run the main script.
      To Calibrate the load cell system
    Start a calibration run.
    Log data to CSV.
  Examples and expected outputs.
  
Calibration
  Clear step-by-step procedure.
  Link to calibration script/notebook.
  Mention where the calibration factor is stored.

Data Logging & Analysis
  Where CSVs get saved.
  Column meanings.
  Link to plotting/analysis scripts.

Known Limitations / TODO / Roadmap
  Power supply limits, noise sources, “future work” ideas.

How to Give Feedback / Contribute
  Perfect spot to link your feedback form.
  Basic instructions if someone wants to open issues or PRs.
