# Milestone 2: 5-Minute Road Segment Features (07 Oct 2026)

## 📌 Overview

In our team meeting on 1 October 2026, our mentor noted that predicting arrival times across full bus trips is too coarse. The team was instructed to:
1. Divide bus routes into consecutive **stop-to-stop road links**.
2. Group travel times into **5-minute intervals** across the 24-hour day.
3. Compute traffic congestion indices to allow machine learning models (Priya & Nishant) to capture morning and evening rush-hour variations.

This folder contains the extraction script and the pre-computed feature dataset for training baseline and advanced models.

---

## 📂 Files in this Folder

| File | Format | Description |
| :--- | :--- | :--- |
| **[`extract_segment_features.py`](extract_segment_features.py)** | Python Script | Cuts bus runs into stop-to-stop segments, extracts speed, computes dwell and net moving times, tags 5-minute bins, and calculates congestion index. |
| **[`segment_features_5min.parquet`](segment_features_5min.parquet)** | Parquet (~46 KB) | Complete tabular feature dataset ready for model training. |
| **[`segment_features_sample.csv`](segment_features_sample.csv)** | CSV (~15 KB) | 100-row preview viewable directly in GitHub or Excel. |

---

## 📊 Raw Columns Used from Datasets

The feature pipeline ingests and joins the Curitiba dataset on `(seq, id)`:

### 1. From `bus_itineraries.parquet` (Route Geometry)
* **`line_code`**, **`line_way`**: Filtered for Route 021 Anti-Horario.
* **`seq`**, **`id`**: Stop sequence numbers and unique stop IDs, used to detect consecutive stop transitions where $\Delta \text{seq} = \text{seq}_{i+1} - \text{seq}_i == 1$.
* **`name`**: Origin and destination stop names (`from_stop_name`, `to_stop_name`).
* **`latitude`**, **`longitude`**: Spatial coordinates of stops.
* **`next_stop_delta_s`**: Inter-stop physical distance in meters, accumulated to compute link distance $d_m$.

### 2. From `bus_tracking.parquet` (GPS Observations)
* **`vehicle`**: Grouped by vehicle ID to reconstruct individual bus trips.
* **`line_code`**, **`itinerary_id`**: Matched with Route 021 Anti-Horario.
* **`seq`**, **`id`**: Matched with route geometry.
* **`event_timestamp`**: Timestamp converted to datetime (`dt`) to compute traversal duration $\Delta t = t_{\text{arrival}} - t_{\text{departure}}$.

---

## 🧮 Mathematical Formulas & Logic Used

### 1. Consecutive Segment Validation Filter
A traversal is valid if:
$$\Delta \text{seq} = 1, \quad 10.0\text{s} \le \Delta t \le 600.0\text{s}, \quad d_m > 0$$
(Filters out GPS loss, depot turnarounds, or corrupted pings).

### 2. Speed Calculation
$$v_{\text{mps}} = \frac{d_m}{\Delta t}, \quad v_{\text{km/h}} = v_{\text{mps}} \times 3.6$$

### 3. Net Moving Time (Separating Stop Dwell Time)
Using the average dwell time extracted in Milestone 1 ($11.9\text{s}$):
$$\text{net\_moving\_sec} = \max(1.0, \, \text{round}(\Delta t - 11.9, \, 1))$$

### 4. 5-Minute Time Interval Binning ($0 \dots 287$)
The 24-hour day is discretized into 288 5-minute bins:
$$\text{time\_bin\_5min} = \left\lfloor \frac{\text{hour} \times 60 + \text{minute}}{5} \right\rfloor \in [0, 287]$$
* Example: $07:12 \implies \lfloor (7 \times 60 + 12) / 5 \rfloor = \lfloor 432 / 5 \rfloor = \mathbf{86}$ (slot `07:10-07:15`).

### 5. Peak-Hour Classification
$$\text{is\_peak\_hour} = \begin{cases} 1 & \text{if } (07:00 \le t \le 09:30) \text{ or } (17:00 \le t \le 19:30) \\ 0 & \text{otherwise (Off-Peak)} \end{cases}$$

### 6. Historical Segment Baseline & Congestion Index
$$\text{segment\_hist\_mean\_sec} = \frac{1}{N_{\text{seg}}} \sum_{k=1}^{N_{\text{seg}}} \text{travel\_time\_sec}_k$$
$$\text{congestion\_index} = \frac{\text{travel\_time\_sec}}{\text{segment\_hist\_mean\_sec}}$$
* $\text{CI} > 1.0 \implies$ Delay / traffic congestion.
* $\text{CI} < 1.0 \implies$ Free-flowing traffic.

---

## 📋 Complete Extracted Features Breakdown

| Feature Name | Type | Category | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| **`travel_time_sec`** | `float` | **Target ($y$)** | Actual time taken to cross the segment (seconds). | `64.8` |
| `trip_id` | `string` | Identifier | Unique identifier per trip. | `TRIP_001_MB300` |
| `vehicle` | `string` | Identifier | Bus identifier. | `MB300` |
| `segment_id` | `string` | Spatial ID | Segment identifier between two consecutive stops. | `SEG_001_002` |
| `from_stop_seq` | `int` | Spatial ID | Starting stop sequence number. | `1` |
| `to_stop_seq` | `int` | Spatial ID | Ending stop sequence number. | `2` |
| `from_stop_name` | `string` | Metadata | Name of departure stop. | `Rua Ver. Garcia Rodrigues...` |
| `to_stop_name` | `string` | Metadata | Name of arrival stop. | `Rua Pedro Fabri, 241...` |
| `distance_m` | `float` | Physical Feature | Exact road length in meters. | `331.0` |
| `dwell_time_sec` | `float` | Physical Feature | Dwell time at station (~11.9s from Milestone 1). | `11.9` |
| `net_moving_sec` | `float` | Physical Feature | Pure road driving time ($\text{travel\_time} - \text{dwell\_time}$). | `52.9` |
| `speed_kmh` | `float` | Physical Feature | Observed average traversal speed in km/h. | `18.4` |
| `departure_time` | `timestamp` | Temporal | Timestamp when bus departed the first stop. | `2017-07-07 23:27:21` |
| `arrival_time` | `timestamp` | Temporal | Timestamp when bus reached the next stop. | `2017-07-07 23:28:26` |
| `time_bin_5min` | `int` | Temporal Feature | 5-minute time bin index ($0 \dots 287$). | `281` |
| `time_slot` | `string` | Temporal Feature | Human-readable 5-minute window. | `23:25-23:30` |
| `hour` | `int` | Temporal Feature | Hour of day ($0 \dots 23$). | `23` |
| `minute` | `int` | Temporal Feature | Minute of hour ($0 \dots 59$). | `27` |
| `day_of_week` | `string` | Calendar Feature | Day name. | `Friday` |
| `day_index` | `int` | Calendar Feature | Day index ($0 = \text{Monday}, \dots, 6 = \text{Sunday}$). | `4` |
| `is_weekend` | `int` | Calendar Feature | $1$ for Saturday/Sunday, $0$ for weekdays. | `0` |
| `is_peak_hour` | `int` | Traffic Context | $1$ for rush hour, $0$ for off-peak. | `0` |
| `peak_period` | `string` | Traffic Context | Label: Morning Peak, Evening Peak, or Off-Peak. | `Off-Peak` |
| `segment_hist_mean_sec` | `float` | Traffic Context | Historical average travel time on this road link. | `68.2` |
| `congestion_index` | `float` | Traffic Context | Delay ratio ($>1.0$ indicates traffic congestion). | `0.95` |

---

## 📈 Summary Analytics (Curitiba Route 021 Sample)

* **Total Samples:** 549 segment runs across 112 unique road segments.
* **Average Segment Distance:** 339.0 meters.
* **Average Segment Travel Time:** 74.2 seconds.
* **Overall Average Speed:** 21.7 km/h.
* **Traffic Variations Captured:**
  * **Morning Peak (07:00–09:30):** Average speed **30.1 km/h**, travel time **44.9s**, Congestion Index **0.70**.
  * **Evening Peak (17:00–19:30):** Average speed dropped to **19.4 km/h**, travel time **80.3s**, Congestion Index **1.14**.
  * **Top Bottleneck Link:** `SEG_018_019` averaged **189.4s** (Speed: 4.13 km/h, Congestion Index: **3.38**).

---

## 🎯 How Features Map to Future Algorithms (Priya & Nishant)

```
Target Variable (y):  travel_time_sec

1. HISTORICAL AVERAGE BASELINE:
   Inputs: segment_id, time_bin_5min, is_peak_hour

2. KALMAN FILTER (Dynamic State Estimation):
   State Vector: [velocity, dwell_time]
   Inputs: distance_m, dwell_time_sec, segment_hist_mean_sec

3. LASSO / RIDGE REGRESSION:
   Inputs: distance_m, dwell_time_sec, time_bin_5min, is_peak_hour, segment_hist_mean_sec

4. TREE-BASED MODELS (Random Forest / XGBoost / LightGBM):
   Inputs: distance_m, dwell_time_sec, time_bin_5min, hour, minute, day_index,
           is_peak_hour, segment_hist_mean_sec, congestion_index, from_stop_seq, to_stop_seq

5. DEEP LEARNING (ANN / MLP & Transformers):
   Continuous Inputs: distance_m, dwell_time_sec, segment_hist_mean_sec
   Entity Embeddings: segment_id, time_bin_5min, day_index
```

---

## 🚀 Python Loading & Splitting Quick Start

```python
import pandas as pd

# Load the prepared feature dataset
df = pd.read_parquet("Progress/2_Segment Travel Times & Features – Oct 2026/segment_features_5min.parquet")

# Chronological 70% Train / 30% Test split (prevents temporal data leakage)
df = df.sort_values("departure_time").reset_index(drop=True)
split_idx = int(0.70 * len(df))
train_df = df.iloc[:split_idx].copy()
test_df = df.iloc[split_idx:].copy()

features = ["distance_m", "time_bin_5min", "hour", "day_index", "is_peak_hour", "dwell_time_sec", "segment_hist_mean_sec"]
X_train, y_train = train_df[features], train_df["travel_time_sec"]
X_test, y_test = test_df[features], test_df["travel_time_sec"]

print(f"Loaded {len(X_train)} training samples and {len(X_test)} testing samples!")
```
