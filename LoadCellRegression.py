import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# === Load CSV (assumes first row are column headers = weights in grams) ===
path = "readings.csv"   # <- change this
df = pd.read_csv(path)

# Convert header strings to float weights
weights = df.columns.astype(float)

# Convert all cell values to numeric
readings_df = df.apply(pd.to_numeric)

# === Per-weight stats (column-wise) ===
means  = readings_df.mean(axis=0).to_numpy()
stds   = readings_df.std(axis=0, ddof=1).to_numpy()
counts = readings_df.count(axis=0).to_numpy()


# === Build (x,y) pairs using ALL readings ===
x_all, y_all = [], []
for w, col in zip(weights, readings_df.columns):
    vals = readings_df[col].dropna().to_numpy()
    if vals.size:
        x_all.append(np.full(vals.size, w))
        y_all.append(vals)

x_all = np.concatenate(x_all)  # weights repeated per reading
y_all = np.concatenate(y_all)  # readings

# === Linear fits ===
# 1) Reading as a function of weight (reading = m*weight + b)
m, b = np.polyfit(x_all, y_all, 1)
y_hat = m * x_all + b
r2_rb = 1 - np.sum((y_all - y_hat)**2) / np.sum((y_all - y_all.mean())**2)

# 2) Weight as a function of reading (weight = a*reading + c)
a, c = np.polyfit(y_all, x_all, 1)
x_hat = a * y_all + c
r2_wr = 1 - np.sum((x_all - x_hat)**2) / np.sum((x_all - x_all.mean())**2)

print(f"reading = {m:.6g} * weight + {b:.6g}   (R^2 = {r2_rb:.6g})")
print(f"weight  = {a:.6g} * reading + {c:.6g}   (R^2 = {r2_wr:.6g})")

# === Plot: readings vs weight with best-fit line (reading = m*weight + b) ===
x_line = np.linspace(x_all.min(), x_all.max(), 200)
y_line = m * x_line + b

plt.figure(figsize=(7,5))
plt.scatter(x_all, y_all, s=12, alpha=0.6, label="All readings")
plt.plot(x_line, y_line, linewidth=2,
         label=f"reading = {m:.3g}·weight + {b:.3g}\n$R^2$={r2_rb:.4f}")
plt.xlabel("Weight (g)")
plt.ylabel("Reading (counts)")
plt.title("Load-Cell Calibration")
plt.grid(True, which="both", linestyle="--", alpha=0.5)  # ← grid lines
plt.legend(loc="best")
plt.tight_layout()

# Save first (useful for SSH/headless); show if you’re local
plt.savefig("plot.png", dpi=300)
