# Milestone 1: Dwell Time MWE & Prototype (01 Oct 2026)

## 📌 Overview

In our team meeting on 28 September 2026, our mentor asked us to build a **Minimum Working Example (MWE)** to test whether we can calculate bus stop dwell times from low-frequency GPS tracking data.

On 1 October 2026, Vishal presented this working demo to the team. It proved that:
1. We can separate dwell time (time spent at stations) from moving time (driving on the road) using a **30-meter stop zone**.
2. Incorporating dwell time reduced next-stop arrival prediction error from **29.5 seconds down to 25.2 seconds**, achieving a **+14.4% accuracy improvement**.

---

## 📂 Files in this Folder

| File | Description | Usage |
| :--- | :--- | :--- |
| **[`simple_mwe.py`](simple_mwe.py)** | Python script that loads Curitiba Line 021, estimates dwell times via constrained optimization, and verifies ETA accuracy. | `python "Progress/1_Dwell Time MWE & Prototype – 01 Oct 2026/simple_mwe.py"` (~1 sec) |
| **[`prototype.html`](prototype.html)** | Interactive visual simulation showing the bus driving along stops and dwelling for passengers. | Open directly in any web browser |
| **[`FLOWCHART.md`](FLOWCHART.md)** | 4-step system architecture diagram. | View in VS Code or GitHub |
| **[`data/`](data/)** | Bundled sample parquet files for Route 021 (Anti-Horario) for zero-setup execution. | Used automatically by `simple_mwe.py` |

---

## 📊 Raw Columns Used from Datasets

The script merges route layout geometry with vehicle GPS pings on `(seq, id)`:

### 1. From `bus_itineraries.parquet` (Route Geometry)
* **`line_code`**: Bus line identifier, filtered for `'021'`.
* **`line_way`**: Direction of travel, filtered for `'Anti-Horario'`.
* **`seq`**: Stop sequence number ($0 \dots 112$) along the route.
* **`id`**: Unique bus stop ID.
* **`name`**: Bus stop name.
* **`next_stop_delta_s`**: Distance in meters from the current stop to the next stop.

### 2. From `bus_tracking.parquet` (GPS Observations)
* **`line_code`**, **`itinerary_id`**: Matched with `'021'` and `'Anti-Horario'`.
* **`vehicle`**: Bus vehicle ID, filtered for `'MB300'`.
* **`seq`**, **`id`**: Joined with the itinerary table to match GPS observations with physical stops.
* **`event_timestamp`**: Timestamp of observation, converted to elapsed seconds from trip start:
  $$t_{\text{sec}} = t_{\text{ping}} - t_{\text{start}}$$

---

## 🧮 Mathematical Model & Formulas Used

### 1. Cumulative Distance Along Route
$$\text{dist\_m}[s+1] = \text{dist\_m}[s] + \text{next\_stop\_delta\_s}[s]$$
For Route 021, the cumulative distance spans **113 stops across 38.1 km**.

### 2. 30-Meter Platform Zone Boundary
A physical platform boundary of length $2G = 30\text{m}$ ($G = 15\text{m}$ before the stop, $15\text{m}$ after the stop) is placed around each stop.  
The physical on-road moving distance between stop $s$ and $s+1$ is:
$$d_{\text{moving}}[s] = \max(10.0, \, \text{dist\_m}[s+1] - \text{dist\_m}[s] - 30.0)$$

### 3. Physical Speed Bound Constraint
Assuming a maximum allowable bus speed of $V_{\max} = 20.0\text{ m/s}$ ($\approx 72\text{ km/h}$), the minimum moving time is:
$$\text{min\_moving\_time}[s] = \frac{d_{\text{moving}}[s]}{20.0}$$

### 4. Constrained Optimization (Trajectory Resampling via L-BFGS-B)
We solve for moving times $TT_s$ ($s = 1 \dots S-1$) and stop dwell times $ST_s$ ($s = 1 \dots S$):
$$\min_{\mathbf{p}} \sum_{s=1}^S \left(\hat{t}_s - t_s^{\text{observed}}\right)^2 + 0.5 \sum_{s=1}^S \left(ST_s - 12.0\right)^2$$
* **Subject to bounds:**
  $$TT_s \ge \text{min\_moving\_time}[s]$$
  $$0.0 \le ST_s \le 60.0\text{ seconds}$$
* Here $\hat{t}_{s+1} = \hat{t}_s + ST_s + TT_s$, and $0.5 \sum (ST_s - 12.0)^2$ is a L2 regularization term anchoring low-frequency pings around the historical average (~12s).

### 5. Prediction Accuracy Benchmark (MAE)
Next-stop travel time was evaluated across two conditions:
* **Baseline (Without Dwell Time):** Uses historical mean segment travel time:
  $$\text{MAE}_{\text{baseline}} = \frac{1}{S-1} \sum_{s=1}^{S-1} |\Delta t_s - \overline{\Delta t}| = \mathbf{29.5\text{ seconds}}$$
* **Smart Model (With Dwell Time):** Combines on-road transit speed with extracted dwell time:
  $$\text{ETA}_s = \frac{\Delta x_s}{v_{\text{avg}}} + ST_s$$
  $$\text{MAE}_{\text{smart}} = \frac{1}{S-1} \sum_{s=1}^{S-1} |\Delta t_s - \text{ETA}_s| = \mathbf{25.2\text{ seconds}}$$
* **Accuracy Improvement:**
  $$\text{Improvement} = \frac{29.5 - 25.2}{29.5} \times 100\% = \mathbf{+14.4\%}$$

---

## 📈 Benchmark Results (Route 021 Anti-Horario)

* **Average Dwell Time per Stop:** **11.9 seconds**
* **Minimum Dwell Time:** **9.8 seconds**
* **Maximum Dwell Time:** **12.0 seconds**
* **Trip Time Distribution:**
  * **81.0%** of trip duration is moving on roads.
  * **19.0%** of trip duration is dwelling at stations.

---

## 🎯 How this Dwell Time Feeds into Future Algorithms

The dwell time extracted here serves as the baseline parameter and feature for the downstream modeling work assigned to Priya and Nishant:

1. **Feature Input for Segment Features (Milestone 2):** Passed as `dwell_time_sec = 11.9s` to isolate `net_moving_sec = travel_time - dwell_time`.
2. **Kalman Filter (Dynamic State Estimation):** Acts as the station state variable alongside road velocity.
3. **Machine Learning & Neural Networks (ANN / XGBoost):** Used as an explicit feature so models can learn how passenger stop delays combine with road congestion to influence total arrival time.

---

## 🚀 How to Run

```bash
python "Progress/1_Dwell Time MWE & Prototype – 01 Oct 2026/simple_mwe.py"
```
Takes ~1 second and prints complete verification analytics in the terminal.
