# Milestone 2: 5-Minute Road Segment Features (07 Oct 2026)

## Why we made this

In our meeting on 1 October 2026, the mentor suggested that predicting arrival times over full trips is too coarse. Instead, we should:
1. Divide bus routes into smaller stop-to-stop road segments.
2. Group travel times into **5-minute intervals** with the time of day attached.
3. Use this data so our machine learning models can learn how traffic speeds change during morning and evening rush hours.

This folder contains the script and the dataset that Priya and Nishant will use to train our baseline models.

---

## Files in this folder

| File | What it is |
| :--- | :--- |
| **`extract_segment_features.py`** | Python script that cuts bus trips into stop-to-stop road links and tags them with 5-minute time slots and traffic categories. |
| **`segment_features_5min.parquet`** | The complete feature dataset saved in Parquet format (~46 KB), ready for model training. |
| **`segment_features_sample.csv`** | First 100 rows in CSV format so you can easily open and check the columns in Excel or VS Code. |

---

## What each column means

| Column | Type | Explanation | Example |
| :--- | :--- | :--- | :--- |
| `trip_id` | text | Unique trip identifier | `TRIP_001_MB300` |
| `vehicle` | text | Bus number | `MB300` |
| `segment_id` | text | Road segment between two consecutive stops | `SEG_001_002` |
| `from_stop_seq` | int | Starting stop number | `1` |
| `to_stop_seq` | int | Ending stop number | `2` |
| `from_stop_name` | text | Name of the starting stop | `Rua Ver. Garcia Rodrigues...` |
| `to_stop_name` | text | Name of the ending stop | `Rua Pedro Fabri, 241...` |
| `distance_m` | float | Length of this road segment in meters | `331.0` |
| `departure_time` | timestamp | Time the bus left the starting stop | `2017-07-07 23:27:21` |
| `arrival_time` | timestamp | Time the bus reached the next stop | `2017-07-07 23:28:26` |
| **`travel_time_sec`** | float | **Target ($y$):** Actual time taken to cross the segment (in seconds) | `64.8` |
| `dwell_time_sec` | float | Estimated wait time at the station (~11.9s from Milestone 1) | `11.9` |
| `net_moving_sec` | float | Pure driving time (`travel_time - dwell_time`) | `52.9` |
| `speed_kmh` | float | Average speed on this segment in km/h | `18.4` |
| **`time_bin_5min`** | int | 5-minute time slot of the day ($0 \dots 287$) | `281` |
| `time_slot` | text | Human-readable 5-minute window | `23:25-23:30` |
| `hour` | int | Hour of the day (0 to 23) | `23` |
| `minute` | int | Minute of the hour (0 to 59) | `27` |
| `day_of_week` | text | Day of the week | `Friday` |
| `is_peak_hour` | int | 1 if morning or evening rush hour, else 0 | `0` |
| `peak_period` | text | "Morning Peak", "Evening Peak", or "Off-Peak" | `Off-Peak` |
| `segment_hist_mean_sec` | float | Average historical travel time for this specific road segment | `68.2` |
| `congestion_index` | float | Ratio of actual travel time to historical average (>1.0 means traffic delay) | `0.95` |

---

## Key numbers from Curitiba Route 021

* **Total samples extracted:** 549 segment runs across 112 unique road segments.
* **Morning Peak (07:00 to 09:30):** Buses moved faster, averaging **30.1 km/h** with **44.9s** per segment.
* **Evening Peak (17:00 to 19:30):** Heavy traffic, average speed dropped to **19.4 km/h** and travel times jumped to **80.3s** per segment.

---

## How to run the feature extraction script

```bash
python "Progress/2_Segment Travel Times & Features – Oct 2026/extract_segment_features.py"
```

## How to load the data in Python for training models

```python
import pandas as pd

# Load the prepared dataset
df = pd.read_parquet("Progress/2_Segment Travel Times & Features – Oct 2026/segment_features_5min.parquet")

# Features to feed into your model
features = ["distance_m", "time_bin_5min", "hour", "day_index", "is_peak_hour", "dwell_time_sec", "segment_hist_mean_sec"]
X = df[features]

# Target variable: travel time in seconds
y = df["travel_time_sec"]

print(f"Loaded {len(X)} training samples!")
```
