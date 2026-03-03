import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# Hardcoded run configuration
# -----------------------------
Voltage = 10  # voltage setting during data collection
BASE_FOLDER = Path(r"c:\Users\stanl\OneDrive - Embry-Riddle Aeronautical University\Research\EDFFDM\Load Cell\LoadCellProject\Main")
SAVE_FOLDER = Path(r"c:\Users\stanl\OneDrive - Embry-Riddle Aeronautical University\Research\EDFFDM\Load Cell\LoadCellProject\Images")
FILE_NAME = "Test.csv"

csv_path = BASE_FOLDER / FILE_NAME
if not csv_path.exists():
    raise FileNotFoundError(f"CSV file not found: {csv_path}")

SAVE_FOLDER.mkdir(parents=True, exist_ok=True)
csv_stem = csv_path.stem
thrust_plot_path = SAVE_FOLDER / f"{csv_stem}_ThrustPlot.png"
current_plot_path = SAVE_FOLDER / f"{csv_stem}_CurrentPlot.png"
df = pd.read_csv(csv_path)


def parse_pwm_from_label(label, prefix):
    if not label.startswith(prefix):
        return None
    pwm_text = label[len(prefix):]
    try:
        return float(pwm_text)
    except ValueError:
        return None


mass_map = {}
current_map = {}

for col in df.columns:
    pwm_mass = parse_pwm_from_label(col, "Mass_")
    if pwm_mass is not None:
        mass_map[pwm_mass] = col
        continue

    pwm_current = parse_pwm_from_label(col, "Current_")
    if pwm_current is not None:
        current_map[pwm_current] = col


# Backward compatibility: legacy CSV where columns are directly PWM values
if not mass_map:
    legacy_pwm = []
    for col in df.columns:
        try:
            legacy_pwm.append(float(col))
        except ValueError:
            pass
    if not legacy_pwm:
        raise ValueError("No usable columns found. Expected Mass_<PWM>/Current_<PWM> or legacy numeric PWM columns.")
    legacy_pwm = sorted(legacy_pwm)
    mass_map = {pwm: str(int(pwm)) if float(int(pwm)) == pwm and str(int(pwm)) in df.columns else str(pwm) for pwm in legacy_pwm}


# Sort PWM levels and coerce each column to numeric
mass_pwm = sorted(mass_map.keys())
current_pwm = sorted(current_map.keys())

mass_stats_pwm = []
mass_means = []
mass_stds = []
mass_counts = []
x_mass_all = []
y_mass_all = []

for pwm in mass_pwm:
    col = mass_map[pwm]
    vals = pd.to_numeric(df[col], errors="coerce").dropna().to_numpy()
    if vals.size == 0:
        continue
    mass_stats_pwm.append(pwm)
    mass_means.append(vals.mean())
    mass_stds.append(vals.std(ddof=1) if vals.size > 1 else 0.0)
    mass_counts.append(vals.size)
    x_mass_all.append(np.full(vals.size, pwm))
    y_mass_all.append(vals)

if not y_mass_all:
    raise ValueError("No valid mass readings found in CSV.")

x_mass_all = np.concatenate(x_mass_all)
y_mass_all = np.concatenate(y_mass_all)
mass_stats_pwm = np.array(mass_stats_pwm)
mass_means = np.array(mass_means)
mass_stds = np.array(mass_stds)
mass_counts = np.array(mass_counts)


# Thrust regressions
m, b = np.polyfit(x_mass_all, y_mass_all, 1)
y_mass_hat = m * x_mass_all + b
ss_res_rb = np.sum((y_mass_all - y_mass_hat) ** 2)
ss_tot_rb = np.sum((y_mass_all - y_mass_all.mean()) ** 2)
r2_rb = 1 - ss_res_rb / ss_tot_rb if ss_tot_rb != 0 else np.nan

a, c = np.polyfit(y_mass_all, x_mass_all, 1)
x_mass_hat = a * y_mass_all + c
ss_res_wr = np.sum((x_mass_all - x_mass_hat) ** 2)
ss_tot_wr = np.sum((x_mass_all - x_mass_all.mean()) ** 2)
r2_wr = 1 - ss_res_wr / ss_tot_wr if ss_tot_wr != 0 else np.nan

print(f"gram thrust = {m:.6g} * PWM + {b:.6g}   (R^2 = {r2_rb:.6g})")
print(f"PWM  = {a:.6g} * gram thrust + {c:.6g}   (R^2 = {r2_wr:.6g})")


# Thrust plot
x_line = np.linspace(x_mass_all.min(), x_mass_all.max(), 200)
y_line = m * x_line + b

plt.figure(figsize=(7, 5))
plt.scatter(x_mass_all, y_mass_all, s=12, alpha=0.4, label="Individual thrust readings", color="gray")
plt.errorbar(
    mass_stats_pwm,
    mass_means,
    yerr=mass_stds,
    fmt='o',
    markersize=8,
    alpha=.9,
    capsize=5,
    capthick=1.5,
    label="Thrust mean ± 1 std"
)
plt.plot(x_line, y_line, linewidth=2, color='red', label=f"Thrust = {m:.3g}·PWM + {b:.3g}")
plt.xlabel("Throttle [PWM] (us)")
plt.ylabel("Thrust (gram-force)")
plt.title(f"Thrust Pulse Width Mapping ({Voltage}V)")
plt.grid(True, which="both", linestyle="--", alpha=1)
plt.legend(loc="lower right")
plt.gca().text(
    0.03,
    0.97,
    f"$R^2$ = {r2_rb:.4f}",
    transform=plt.gca().transAxes,
    fontsize=10,
    verticalalignment='top',
    bbox=dict(boxstyle='round', facecolor='white', alpha=0.6)
)
plt.tight_layout()
plt.savefig(thrust_plot_path, dpi=300)
plt.close()


# Current processing + plot (if current columns exist)
if current_pwm:
    current_stats_pwm = []
    current_means = []
    current_stds = []
    x_current_all = []
    y_current_all = []

    for pwm in current_pwm:
        col = current_map[pwm]
        vals = pd.to_numeric(df[col], errors="coerce").dropna().to_numpy()
        if vals.size == 0:
            continue
        current_stats_pwm.append(pwm)
        current_means.append(vals.mean())
        current_stds.append(vals.std(ddof=1) if vals.size > 1 else 0.0)
        x_current_all.append(np.full(vals.size, pwm))
        y_current_all.append(vals)

    if y_current_all:
        x_current_all = np.concatenate(x_current_all)
        y_current_all = np.concatenate(y_current_all)
        current_stats_pwm = np.array(current_stats_pwm)
        current_means = np.array(current_means)
        current_stds = np.array(current_stds)

        m_i, b_i = np.polyfit(x_current_all, y_current_all, 1)
        y_current_hat = m_i * x_current_all + b_i
        ss_res_i = np.sum((y_current_all - y_current_hat) ** 2)
        ss_tot_i = np.sum((y_current_all - y_current_all.mean()) ** 2)
        r2_i = 1 - ss_res_i / ss_tot_i if ss_tot_i != 0 else np.nan

        print(f"current = {m_i:.6g} * PWM + {b_i:.6g}   (R^2 = {r2_i:.6g})")

        x_line_i = np.linspace(x_current_all.min(), x_current_all.max(), 200)
        y_line_i = m_i * x_line_i + b_i

        plt.figure(figsize=(7, 5))
        plt.scatter(x_current_all, y_current_all, s=12, alpha=0.4, label="Individual current readings", color="gray")
        plt.errorbar(
            current_stats_pwm,
            current_means,
            yerr=current_stds,
            fmt='o',
            markersize=8,
            alpha=.9,
            capsize=5,
            capthick=1.5,
            label="Current mean ± 1 std"
        )
        plt.plot(x_line_i, y_line_i, linewidth=2, color='blue', label=f"Current = {m_i:.3g}·PWM + {b_i:.3g}")
        plt.xlabel("Throttle [PWM] (us)")
        plt.ylabel("Current")
        plt.title(f"Current Pulse Width Mapping ({Voltage}V)")
        plt.grid(True, which="both", linestyle="--", alpha=1)
        plt.legend(loc="lower right")
        plt.gca().text(
            0.03,
            0.97,
            f"$R^2$ = {r2_i:.4f}",
            transform=plt.gca().transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.6)
        )
        plt.tight_layout()
        plt.savefig(current_plot_path, dpi=300)
        plt.close()

print("Done: processed thrust and current tables from latest CSV format.")
print(f"Saved thrust plot: {thrust_plot_path}")
if current_pwm:
    print(f"Saved current plot: {current_plot_path}")
