# Data Preparation & Preprocessing: Team Handoff Guide

**Project:** Digital Twin for Urban Mobility Systems (DTUMOS)  
**Task Owner:** Vishal Singh (Data Preparation & Preprocessing)  
**Modeling Team:** Nishant & Priya  

---

## 1. Project Background & Mentor Assignment

Our mentor assigned me the **Data Preparation and Data Preprocessing** task for the DTUMOS project.

The goal of this phase was to process raw public transit GPS tracking data into clean, structured features that capture real-world traffic dynamics:

* **Data Sourcing & Ingestion:** Download and organize the Curitiba BRT dataset (~5.1 GB).
* **Dwell Time Extraction (Milestone 1):** Measure how long buses remain stopped at stations for passenger boarding/alighting (~12 seconds per stop), which improved arrival predictions by **+14.4%**.
* **Segment Traversal & 5-Minute Binning (Milestone 2):** Break routes into stop-to-stop road links and calculate travel times, speeds, and traffic congestion indicators across 5-minute time slots (0–287).
* **Current Status:** A working prototype feature dataset is ready for Route 021 (`segment_features_5min.parquet`).

---

## 2. Why the Current Dataset is Small (And What to Do Next)

The current feature file contains **549 segment runs**.

### Why it is a small sample right now
* The complete Curitiba dataset is **~5.1 GB** across thousands of files. Processing everything upfront is slow and can crash laptops with limited memory.
* To make testing and debugging quick and safe, I built and validated the complete pipeline on a clean **working sample (Route 021)** first.

### Step-by-step roadmap

```
[Phase 1: Now — Small Sample]
  • Priya & Nishant use the 549-row dataset (segment_features_5min.parquet).
  • Write and debug baseline models (Historical Avg, Kalman Filter, ANN, etc.).
  • Code runs in ~2 seconds for fast iteration and debugging.
                    │
                    ▼
[Phase 2: Code Verification]
  • Verify that all model scripts run end-to-end without errors.
                    │
                    ▼
[Phase 3: Scaling Up]
  • Vishal runs the feature extraction script across more routes and full days.
  • Generates a large-scale dataset (thousands of rows).
  • Priya & Nishant re-run their verified model code on the full dataset.
```

---

## 3. Dataset Splitting & Modeling Guidelines

### Q1: Should we use 70% for training and 30% for testing?
**Yes.** A 70% Train / 30% Test split is standard practice.

> [!IMPORTANT]
> **Do not use a random shuffle!**  
> Bus transit is time-series data. Randomly shuffling rows causes **data leakage** (e.g., predicting travel time at 08:10 using data from 08:05 on the exact same trip).  
> **Rule:** Sort by time (`departure_time`):
> * **First 70% (past trips):** Training set.
> * **Last 30% (future trips):** Testing set.

---

### Q2: Should Priya take half of the training data and Nishant take the other half?
**No, do not split the training data between teammates.**

* If Priya trains on morning data (smooth traffic) and Nishant trains on evening rush hours (heavy congestion), you cannot fairly compare which model performed better.
* Both teammates must train on the **exact same 70% training data** and evaluate on the **exact same 30% testing data** for a fair, apples-to-apples comparison.
* **What you should divide instead is the model architectures:**
  * **Priya's models:** Historical Average baseline, Lasso Regression, Random Forest.
  * **Nishant's models:** Kalman Filter, Neural Network (ANN/MLP), XGBoost.

---

## 4. Dataset Files & Locations

### Clean Feature Dataset (Start here for modeling)
* **Parquet format (recommended for Python):**  
  `Progress/2_Segment Travel Times & Features – Oct 2026/segment_features_5min.parquet`
* **CSV preview (100 rows, for Excel / VS Code):**  
  `Progress/2_Segment Travel Times & Features – Oct 2026/segment_features_sample.csv`

### Full Raw Dataset (Optional)
* Stored on the shared Google Drive folder (git-ignored).
* Or re-download via the automated ingestion script:
  ```bash
  python "Code/Dataset – Curitiba Bus Linear Interpolation.py"
  ```

---

## 5. Python Quick Start (For Priya & Nishant)

```python
import pandas as pd

# 1. Load the pre-extracted features
df = pd.read_parquet("Progress/2_Segment Travel Times & Features – Oct 2026/segment_features_5min.parquet")

# 2. Sort chronologically (prevents data leakage)
df = df.sort_values("departure_time").reset_index(drop=True)

# 3. Chronological 70/30 train/test split
split_idx = int(0.70 * len(df))
train_df = df.iloc[:split_idx].copy()
test_df = df.iloc[split_idx:].copy()

# 4. Feature columns (X) and Target (y)
feature_cols = [
    "distance_m",
    "time_bin_5min",
    "hour",
    "minute",
    "is_peak_hour",
    "dwell_time_sec",
    "segment_hist_mean_sec"
]
target_col = "travel_time_sec"

X_train, y_train = train_df[feature_cols], train_df[target_col]
X_test, y_test = test_df[feature_cols], test_df[target_col]

print(f"Data ready! Training samples: {len(X_train)} | Testing samples: {len(X_test)}")
```

---

## 6. Module Status Report: Data Preparation

* **Task Owner:** Vishal Singh
* **Assigned Task:** Data Identification, Acquisition & Geometry Preparation
* **Downstream Team:** Nishant & Priya (Modeling)
* **Related Issue:** Data Preparation
* **Documentation:** `DATA_PREPARATION_AND_PREPROCESSING.md`

#### 1. Background & Mentor Assignment
In our team meetings, our mentor assigned me to handle the **Data Preparation** phase for DTUMOS. The objective was to source a reliable public transit dataset with both spatial route layouts (itineraries) and continuous GPS tracking data, and build an automated ingestion pipeline.

#### 2. Dataset Selection & Architecture
* **Selected Dataset:** Curitiba BRT (Brazil) dataset (`curitibaresearch/bus-linear-interpolation` on Hugging Face).
* **Dataset Characteristics:**
  * Contains Snappy-compressed Parquet files totaling **~5.1 GB**.
  * Organized into `bus_itineraries/` (1,303 files, route shapes & stop distances) and `bus_tracking/` (1,224 files, vehicle GPS pings).
* **Storage & Git Hygiene:**
  * Raw files are excluded from Git via `.gitignore` to avoid repository bloat, and are stored on our shared Google Drive.

#### 3. Work Completed
1. **Automated Pipeline Script:** Built `Code/Dataset – Curitiba Bus Linear Interpolation.py`, which downloads the dataset and sorts files into geometry and tracking folders based on schema validation.
2. **Route Geometry Preparation:** Extracted complete stop sequences, GPS coordinates, and cumulative stop distances (`next_stop_delta_s`) for Route 021 (Anti-Horario, 113 stops across 38.1 km).
3. **Working Sample:** Created a lightweight sample for Route 021 in `Progress/1_Dwell Time MWE & Prototype – 01 Oct 2026/data/` so teammates can run tests in under 2 seconds without downloading 5 GB.

#### 4. Deliverables Ready
* Pipeline Script: `Code/Dataset – Curitiba Bus Linear Interpolation.py`
* Working Sample: `Progress/1_Dwell Time MWE & Prototype – 01 Oct 2026/data/`
* Documentation: `DATA_PREPARATION_AND_PREPROCESSING.md`

---

## 7. Module Status Report: Data Preprocessing & Feature Engineering

* **Task Owner:** Vishal Singh
* **Assigned Task:** Feature Engineering, Dwell Time Extraction & Modeling Handoff
* **Downstream Team:** Nishant & Priya (Modeling)
* **Related Issue:** Data Preprocessing
* **Documentation:** `DATA_PREPARATION_AND_PREPROCESSING.md`

#### 1. Background & Scope
Following the mentor's direction, the goal of this preprocessing stage was to transform raw GPS pings into structured tabular features that capture real-world bus dynamics: isolating **station dwell times** and **road traffic patterns across 5-minute time windows**.

#### 2. Preprocessing & Feature Pipeline
1. **Dwell Time Calculation (Milestone 1):**
   * Applied a 30m buffer (15m before and after each stop) to isolate passenger boarding/alighting time.
   * Finding: Bus spends ~12 seconds per stop (19% of total trip time).
   * Result: Incorporating dwell time improved next-stop arrival prediction accuracy by **+14.4%** (error dropped from 29.5s to 25.2s).
2. **Road Link Segmentation (Milestone 2):**
   * Divided routes into stop-to-stop road segments ($S_i \to S_{i+1}$).
   * Measured distance, actual traversal time, observed speed, and net moving time.
3. **5-Minute Time Binning & Traffic Features:**
   * Binned each day into 288 slots of 5 minutes each (0–287).
   * Tagged morning peak (07:00–09:30), evening peak (17:00–19:30), and off-peak hours.
   * Computed historical segment mean time and congestion index (actual time vs. historical average).

#### 3. Current Dataset Status (Working Prototype Sample)
* To ensure Priya and Nishant can build and debug their baseline models quickly without memory issues, I generated a verified prototype sample of **549 segment runs across 112 unique road segments** (`segment_features_5min.parquet`).
* Scripts run in ~2 seconds, allowing fast iteration and clean debugging.

#### 4. Recommended Modeling Strategy & Handoff
* **Train / Test Split:** Standard 70% Train / 30% Test split sorted by time (`departure_time`) to prevent temporal data leakage.
* **Work Division:** Both Priya and Nishant will train on the **same 70% training data** and evaluate on the **same 30% test data** so that model comparisons are fair and consistent.
* **Model Assignments:**
  * Priya: Historical Average baseline, Lasso Regression, Random Forest.
  * Nishant: Kalman Filter, Neural Network (ANN/MLP), XGBoost.

#### 5. Next Steps
1. Priya and Nishant implement their candidate models using `segment_features_5min.parquet`.
2. Once the baseline scripts are verified, I will run the feature extraction pipeline on additional routes and dates to provide the full dataset for final evaluation.
