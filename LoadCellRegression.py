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


# === Plot: readings vs weight with best-fit line and error bars ===
x_line = np.linspace(means.min(), means.max(), 200)
y_line = a * x_line + c

plt.figure(figsize=(7, 5))
# Scatter plot with error bars showing ±1 std per weight
weight_uncertainty = 0.01 
plt.errorbar(means, weights, xerr=stds, yerr=weight_uncertainty, fmt='o', markersize=8, alpha=0.6, 
             label="Mean ± 1 std", capsize=5, capthick=1.5)
plt.plot(x_line, y_line, linewidth=2, color='red',
         label=f"weight = {a:.3g}·reading + {c:.3g}")
plt.xlabel("Reading (counts)")
plt.ylabel("Weight (grams)")
plt.title("Load-Cell Calibration with Reading Uncertainty")
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.legend(loc="best")
plt.tight_layout()
plt.savefig("Calibration.png", dpi=300)
