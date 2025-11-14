import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# === Load CSV (assumes first row are column headers = weights in grams) ===
path = "CalibrationReadings.csv"   
df = pd.read_csv(path)

# Convert header strings to float weights
weights = df.columns.astype(float)

# Convert all cell values to numeric
readings_df = df.apply(pd.to_numeric)

# === Per-weight stats (column-wise) ===
means  = readings_df.mean(axis=0).to_numpy()
stds   = readings_df.std(axis=0, ddof=1).to_numpy()
counts = readings_df.count(axis=0).to_numpy()



# Weight as a function of reading (weight = a*reading + c)
a, c = np.polyfit(means, weights, 1)
x_hat = a * means + c

# --- Coefficient of determination (R^2) ---
# R^2 = 1 - SS_res/SS_tot where SS_res = sum((y - y_hat)^2)
ss_res = np.sum((weights - x_hat) ** 2)
ss_tot = np.sum((weights - np.mean(weights)) ** 2)
r2 = 1.0 - ss_res / ss_tot if ss_tot != 0 else float('nan')
print(f"R^2: {r2:.6f}")


# === Plot: readings vs weight with best-fit line and error bars ===
x_line = np.linspace(means.min(), means.max(), 200)
y_line = a * x_line + c

plt.figure(figsize=(7, 5))
# Scatter plot with error bars showing ±1 std per weight
weight_uncertainty = 0.01 
plt.errorbar(means, weights, xerr=stds, yerr=weight_uncertainty, fmt='o', markersize=8, alpha=.9, 
             label="Mean ± 1 std", capsize=5, capthick=1.5)
plt.plot(x_line, y_line, linewidth=2, color='red',
         label=f"Weight = {a:.3g}·Reading + {c:.3g}")
plt.xlabel("Signal Reading (1)")
plt.ylabel("Weight (gram-force)")
plt.title("Load-Cell Calibration with Reading Uncertainty")
plt.grid(True, which="both", linestyle="--", alpha=1)
plt.legend(loc="best")
plt.tight_layout()
# also add R^2 as text on the plot (top-left)
plt.gca().text(0.03, 0.97, f"$R^2$ = {r2:.4f}", transform=plt.gca().transAxes,
               fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.6))
# Save plot to file
plt.savefig("Calibration.png", dpi=300)
