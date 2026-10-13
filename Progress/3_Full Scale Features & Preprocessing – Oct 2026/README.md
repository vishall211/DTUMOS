# Milestone 3: Full-Scale Features & Preprocessing (12 Oct 2026)

## 📌 Overview

This dedicated folder contains the **complete, full-scale feature extraction pipeline** and the production dataset for machine learning model development.

It unifies the methodology established in:
* **Milestone 1:** Stop dwell time extraction (~11.9s baseline) and physical speed constraints.
* **Milestone 2:** Stop-to-stop road link segmentation, 5-minute time binning ($0 \dots 287$), and congestion index calculation.

By processing the raw Curitiba AVL tracking files at scale, it provides a massive, high-variance dataset capturing dozens of vehicles across different days and traffic periods.

---

## 📂 Files in this Folder

| File | Format | Description |
| :--- | :--- | :--- |
| **[`build_full_dataset.py`](build_full_dataset.py)** | Python Script | Complete end-to-end extraction pipeline. Auto-locates raw tracking files, links stop geometry, extracts traversals, computes 5-minute bins and congestion indices, and exports clean Parquet/CSV files. |
| **[`full_segment_features_5min.parquet`](full_segment_features_5min.parquet)** | Parquet (~3.1 MB) | **The primary dataset for ML models.** Contains **118,386 segment traversal runs** across 88 unique bus vehicles and 112 road links. |
| **[`full_segment_features_sample.csv`](full_segment_features_sample.csv)** | CSV (~18 KB) | 100-row preview for quick visual inspection in Excel or VS Code. |

---

## 📊 Dataset Analytics & Traffic Summary

| Metric | Full Production Value |
| :--- | :--- |
| **Total Traversal Samples** | **118,386** |
| **Unique Bus Vehicles** | **88 buses** |
| **Distinct Road Segments** | **112** |
| **5-Minute Time Bins Covered** | **240 / 288 bins** across the 24-hour day |
| **Average Segment Length** | **340.3 meters** |
| **Average Traversal Time** | **69.1 seconds** |
| **Overall Average Speed** | **23.3 km/h** |

### Traffic Period Distribution:
* **Morning Peak (07:00–09:30):** 968 traversals | Average Speed: **30.45 km/h** | Avg Travel Time: **50.3s** | Congestion Index: **0.75**
* **Evening Peak (17:00–19:30):** 15,721 traversals | Average Speed: **22.63 km/h** | Avg Travel Time: **70.1s** | Congestion Index: **1.01**
* **Off-Peak:** 101,697 traversals | Average Speed: **23.30 km/h** | Avg Travel Time: **69.1s** | Congestion Index: **1.00**

---

## 🧮 Summary of Features Included

| Column Name | Category | Description |
| :--- | :--- | :--- |
| **`travel_time_sec`** | **Target ($y$)** | Actual time taken to cross the road segment (seconds). |
| `trip_id` | Identifier | Unique identifier per trip run (e.g. `TRIP_0042_MB300`). |
| `vehicle` | Identifier | Bus identifier (e.g. `MB300`, `BB302`). |
| `segment_id` | Spatial ID | Unique road segment ID (e.g. `SEG_001_002`). |
| `from_stop_seq`, `to_stop_seq` | Spatial ID | Starting and ending stop sequence numbers. |
| `from_stop_name`, `to_stop_name` | Metadata | Departure and arrival stop names. |
| `distance_m` | Physical | Exact road segment distance in meters. |
| `dwell_time_sec` | Physical | Baseline station dwell time ($11.9\text{s}$). |
| `net_moving_sec` | Physical | Pure driving time ($\text{travel\_time} - \text{dwell\_time}$). |
| `speed_kmh` | Physical | Traversal speed in km/h. |
| `departure_time`, `arrival_time` | Temporal | Exact timestamps. |
| `time_bin_5min` | Temporal | 5-minute interval index ($0 \dots 287$). |
| `time_slot` | Temporal | Formatted time window (e.g. `07:15-07:20`). |
| `hour`, `minute` | Temporal | Hour ($0 \dots 23$) and minute ($0 \dots 59$). |
| `day_of_week`, `day_index` | Calendar | Day name and index ($0 \dots 6$). |
| `is_weekend` | Calendar | $1$ for weekend, $0$ for weekday. |
| `is_peak_hour` | Traffic Context | $1$ for rush hour, $0$ for off-peak. |
| `peak_period` | Traffic Context | Morning Peak, Evening Peak, or Off-Peak. |
| `segment_hist_mean_sec` | Traffic Context | Historical average travel time for that specific link. |
| `congestion_index` | Traffic Context | Congestion ratio ($>1.0$ indicates traffic congestion). |

---

## 🚀 How to Run or Re-Generate the Full Dataset

To process the full dataset, simply run:

```bash
python "Progress/3_Full Scale Features & Preprocessing – Oct 2026/build_full_dataset.py"
```

The script reads the raw Parquet files directly from `Datasets/Curitibaresearch_Bus-linear-interpolation/` and generates `full_segment_features_5min.parquet` in under 10 seconds.

---

## 💻 Python Quick Start for Model Training (Priya & Nishant)

Here is how the modeling team loads and splits the full dataset in Python:

```python
import pandas as pd

# 1. Load the full feature dataset (118,386 samples)
df = pd.read_parquet("Progress/3_Full Scale Features & Preprocessing – Oct 2026/full_segment_features_5min.parquet")

# 2. Sort chronologically (CRITICAL: prevents temporal data leakage!)
df = df.sort_values("departure_time").reset_index(drop=True)

# 3. Chronological 70% Train / 30% Test split
split_idx = int(0.70 * len(df))
train_df = df.iloc[:split_idx].copy()
test_df  = df.iloc[split_idx:].copy()

# 4. Define features (X) and target (y)
features = [
    "distance_m",
    "dwell_time_sec",
    "time_bin_5min",
    "hour",
    "minute",
    "day_index",
    "is_peak_hour",
    "segment_hist_mean_sec"
]
target = "travel_time_sec"

X_train, y_train = train_df[features], train_df[target]
X_test,  y_test  = test_df[features],  test_df[target]

print(f"✓ Training set: {len(X_train):,} samples")
print(f"✓ Testing set:  {len(X_test):,} samples")
```

