import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load data: CSV where the first row = column headers = PWM values (microseconds)
Voltage = 10  # voltage setting during data collection
csv_path = f"Main\\Prop_{Voltage}VThrusts.csv"   # <- change this to your CSV if needed
df = pd.read_csv(csv_path)

# Column names are strings; convert them to floats to get numeric PWM
PWM = df.columns.astype(float)   # e.g., ['50','100'] -> array([50., 100.])

readings_df = df.apply(pd.to_numeric) # * (15.5 / 6) # Arm Correction Error Compensation for 10V data

means  = readings_df.mean(axis=0).to_numpy()               
stds   = readings_df.std(axis=0, ddof=1).to_numpy()        
counts = readings_df.count(axis=0).to_numpy()               

# Build full (x, y) datasets:
x_all, y_all = [], []

for w, col in zip(PWM, readings_df.columns):
    # Grab all readings for this PWM, drop NaNs, convert to NumPy array
    vals = readings_df[col].dropna().to_numpy()
    if vals.size > 0:
        # For N readings at this PWM, make an array [w, w, ..., w] of length N
        x_all.append(np.full(vals.size, w))
        # Store the actual readings
        y_all.append(vals)

# Concatenate list-of-arrays into single 1D arrays
x_all = np.concatenate(x_all)  # PWM repeated per reading
y_all = np.concatenate(y_all)  # raw readings per measurement


# -------------------------------------------------------------------
# Linear regression #1:
m, b = np.polyfit(x_all, y_all, 1)   # slope m, intercept b

# Predicted gram thrust from the model
y_hat = m * x_all + b

# Coefficient of determination R^2 for this fit
ss_res_rb = np.sum((y_all - y_hat) ** 2)          # residual sum of squares
ss_tot_rb = np.sum((y_all - y_all.mean()) ** 2)   # total sum of squares
r2_rb = 1 - ss_res_rb / ss_tot_rb


# Linear regression #2:
#   Model: PWM = a * gram thrust + c
a, c = np.polyfit(y_all, x_all, 1)   # slope a, intercept c

# Predicted PWM from the model
x_hat = a * y_all + c

# R^2 for the inverse fit
ss_res_wr = np.sum((x_all - x_hat) ** 2)
ss_tot_wr = np.sum((x_all - x_all.mean()) ** 2)
r2_wr = 1 - ss_res_wr / ss_tot_wr


# Print calibration equations in a compact, readable form

print(f"gram thrust = {m:.6g} * PWM + {b:.6g}   (R^2 = {r2_rb:.6g})")
print(f"PWM  = {a:.6g} * gram thrust + {c:.6g}   (R^2 = {r2_wr:.6g})")


# Plot: all individual gram thrust vs. PWM with best-fit line (gram thrust = m*PWM + b)
x_line = np.linspace(x_all.min(), x_all.max(), 200)  # smooth range of PWM
y_line = m * x_line + b                              # corresponding fitted gram thrust

plt.figure(figsize=(7, 5))

# Scatter of all individual gram thrust values
plt.scatter(x_all, y_all, s=12, alpha=0.4, label="Individual readings", color="gray")

# Error bars showing mean ± std at each PWM level
plt.errorbar(
    PWM, 
    means, 
    yerr=stds, 
    fmt='o', 
    markersize=8, 
    alpha=.9,
    capsize=5, 
    capthick=1.5,
    label="Mean ± 1 std"
)

# Best-fit line for gram thrust = m * PWM + b (linear regression)
plt.plot(
    x_line,
    y_line,
    linewidth=2,
    color='red',
    label=f"Thrust = {m:.3g}·PWM + {b:.3g}",
)

plt.xlabel("Throttle [PWM] (us)")
plt.ylabel("Thrust (gram-force)")
plt.title(f"Thrust Pulse Width Mapping ({Voltage}V)")

# Light grid to help visually line up points with the axes
plt.grid(True, which="both", linestyle="--", alpha=1)
plt.legend(loc="lower right")
plt.tight_layout()



# also add R^2 as text on the plot (top-left), then save a second copy
plt.gca().text(0.03, 0.97, f"$R^2$ = {r2_rb:.4f}", transform=plt.gca().transAxes,
               fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.6))
plt.savefig("Main\\ThrustPlot.png", dpi=300)
plt.close()
