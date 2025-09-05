"""
Author: Rafael A Castro
Website: www.castron.com
Project: Digital Logic, Embedded, & Firmware - Physics
AS7341 Spectrometer Real-Time Plot
Open Source - Contributions Welcome :)
"""

import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# ---- Configuration ----
COM_PORT = "COM16"
BAUD_RATE = 115200
wavelengths = ["415", "445", "480", "515", "555", "590", "630", "680"]

# Gradient colors for each wavelength bar (start -> end)
bar_colors = [
    [(148 / 255, 0, 211 / 255), (75 / 255, 0, 130 / 255)],  # Violet -> Indigo
    [(75 / 255, 0, 130 / 255), (0, 0, 1)],  # Indigo -> Blue
    [(0, 0, 1), (0, 1, 1)],  # Blue -> Cyan
    [(0, 1, 1), (0, 1, 0)],  # Cyan -> Green
    [(0, 1, 0), (1, 1, 0)],  # Green -> Yellow
    [(1, 1, 0), (1, 127 / 255, 0)],  # Yellow -> Orange
    [(1, 127 / 255, 0), (1, 0, 0)],  # Orange -> Red
    [(1, 0, 0), (148 / 255, 0, 211 / 255)],  # Red -> Violet wrap
]

# ---- Initialize serial ----
ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)

# ---- Dark calibration ----
print("Place sensor in darkness for calibration...")
dark_values = np.zeros(len(wavelengths))
for _ in range(10):
    if ser.in_waiting > 0:
        line = ser.readline().decode("utf-8").strip()
        if ":" in line:
            name, value = line.split(":")
            wl = name.split()[-1].replace("nm", "").strip()
            if wl in wavelengths:
                index = wavelengths.index(wl)
                dark_values[index] += int(value)
dark_values /= 10
print("Dark calibration done:", dark_values)

# ---- Initialize plot ----
fig, ax = plt.subplots(figsize=(12, 6))
bars = []
for i, wl in enumerate(wavelengths):
    # Use a colormap for gradient
    cmap = LinearSegmentedColormap.from_list(f"bar{i}", bar_colors[i])
    bar = ax.bar(wl, 0, color=cmap(0.5))  # mid color
    bars.append(bar[0])

ax.set_ylim(0, 1.2)
ax.set_ylabel("Normalized Intensity")
ax.set_xlabel("Wavelength (nm)")
ax.set_title("AS7341 Real-time Spectrum (Visible Light)")
plt.grid(True, linestyle="--", alpha=0.4)

# Footer
footer_text = (
    "Designed by Rafael A Castro - www.castron.org - "
    "Digital Logic, Embedded & Firmware - Physics -  "
    "AS7341 - Spectrometer Real-Time Plot - Open Source - contributions welcomed :)"
)
plt.figtext(
    0.5,
    0.01,
    footer_text,
    wrap=True,
    horizontalalignment="center",
    fontsize=8,
    color="gray",
)

# ---- Smoothing ----
smoothed = np.zeros(len(wavelengths))
alpha = 0.2


# ---- Update function ----
def update(frame):
    global smoothed
    readings = np.zeros(len(wavelengths))
    while ser.in_waiting > 0:
        line = ser.readline().decode("utf-8").strip()
        if ":" in line:
            name, value = line.split(":")
            wl = name.split()[-1].replace("nm", "").strip()
            if wl in wavelengths:
                index = wavelengths.index(wl)
                readings[index] = max(int(value) - dark_values[index], 0)

    max_val = max(readings) if max(readings) > 0 else 1
    normalized = readings / max_val
    smoothed = alpha * normalized + (1 - alpha) * smoothed

    # Update bars with gradient shading
    for i, bar in enumerate(bars):
        cmap = LinearSegmentedColormap.from_list(f"bar{i}", bar_colors[i])
        bar.set_height(smoothed[i])
        bar.set_color(cmap(smoothed[i]))  # gradient intensity based on value

    return bars


# ---- Start animation ----
ani = animation.FuncAnimation(fig, update, interval=50, blit=False)
plt.show()
ser.close()
