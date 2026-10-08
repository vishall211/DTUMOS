# Data Preparation & Preprocessing: Simple Team Guide

**Project:** DTUMOS (Digital Twin for Urban Mobility Systems)  
**Author:** Vishal Singh  
**For:** Nishant & Priya (Modeling Team)  

---

## 📌 Summary

Our mentor assigned me the **Data Preparation and Preprocessing** task.

Here is what I did, what data is ready for you right now, and what we should do next:

1. **Found & Downloaded the Dataset:** We are using the Curitiba Bus dataset (Brazil). The full data is ~5 GB.
2. **Calculated Stop Dwell Time:** Figured out how much time buses spend stopped at stations for passengers (~12 seconds per stop). Adding this made arrival predictions **14.4% more accurate**.
3. **Created 5-Minute Road Segment Features:** Divided the route into stop-to-stop road links and calculated travel times for each 5-minute time window of the day.
4. **Current Status (Important!):** Right now, I used a **small sample** (Route 021) to build and test the pipeline. This small sample is ready for you now so you can start coding models immediately without downloading 5 GB of files!

---

## ⚠️ Why is the current dataset small? (And what to do next)

You might open `segment_features_5min.parquet` and see only **549 rows** and think: *"Is this enough for machine learning?"*

### Why it's small right now:
* The full dataset is **5.1 GB** and takes a long time to process.
* To avoid crashing computers and wasting time, I created a **small working sample** first.
* This proves that the feature extraction logic works from end to end.

### 🗺️ The Plan: What to do next (Step-by-Step)

```
[Phase 1: Right Now (Small Sample)]
  • Vishal gives Priya & Nishant the small 549-row dataset.
  • Priya & Nishant write their model code (Historical Avg, Kalman Filter, ANN, etc.).
  • Fast debugging: code runs in 2 seconds!
        │
        ▼
[Phase 2: Code Verified]
  • Both models run without errors on the sample.
        │
        ▼
[Phase 3: Scale Up to Full Dataset]
  • Vishal runs the extraction script on more bus lines / full days.
  • Generates a large dataset (thousands of rows).
  • Priya & Nishant re-run their verified code on the large dataset for final results!
```

---

## 💡 About Train/Test Split: What should we do?

### Question 1: Should we use 70% for training and 30% for testing?
**Yes!** 70% train and 30% test is the standard way to do it.

**Important Rule:**  
Do **NOT** shuffle rows randomly!  
Because this is time data, sort the data by time:
* **First 70% (past trips):** Use for Training.
* **Last 30% (future trips):** Use for Testing.

This tests if the model can predict the future using data from the past.

---

### Question 2: Should Priya take half of the 70% (35%) and Nishant take the other half (35%)?
**No, do not split the data between teammates!**

Here is why in simple terms:
* Imagine Priya trains on easy morning data with light traffic, and Nishant trains on evening rush-hour data with heavy jams.
* If Priya gets better accuracy, you won't know if her model is smarter, or if her data was just easier!
* **Correct way:** Both Priya and Nishant should use the **SAME 70% training data** and test on the **SAME 30% testing data**.
* **What you should divide instead is the MODELS:**
  * **Priya's models:** Historical Average, Linear/Lasso Regression, Random Forest.
  * **Nishant's models:** Kalman Filter, Neural Network (ANN/MLP), XGBoost.
* That way, we can put all models side-by-side on the exact same test data and see which one actually wins!

---

## 📂 Where is the Data?

### 1. Ready-to-Use Feature Data (Start here!)
You do **not** need the raw 5 GB files. Just use this:
* **Parquet file (recommended):**  
  `Progress/2_Segment Travel Times & Features – Oct 2026/segment_features_5min.parquet`
* **CSV preview (to open in Excel):**  
  `Progress/2_Segment Travel Times & Features – Oct 2026/segment_features_sample.csv`

### 2. Full Raw Dataset (Only if you need it)
* **Google Drive:** Hosted on our shared team Google Drive.
* **Or download via script:**
  ```bash
  python "Code/Dataset – Curitiba Bus Linear Interpolation.py"
  ```

---

## 🚀 5-Line Python Code for Priya and Nishant

Here is how you can load the data and split it 70/30 in Python right now:

```python
import pandas as pd

# 1. Load the features
df = pd.read_parquet("Progress/2_Segment Travel Times & Features – Oct 2026/segment_features_5min.parquet")

# 2. Sort by time (no random shuffle!)
df = df.sort_values("departure_time").reset_index(drop=True)

# 3. 70% train / 30% test split
split_point = int(0.70 * len(df))
train_df = df.iloc[:split_point]
test_df = df.iloc[split_point:]

# 4. Features (X) and Target (y)
features = ["distance_m", "time_bin_5min", "hour", "is_peak_hour", "dwell_time_sec", "segment_hist_mean_sec"]
X_train, y_train = train_df[features], train_df["travel_time_sec"]
X_test, y_test = test_df[features], test_df["travel_time_sec"]

print(f"Ready! Training rows: {len(X_train)}, Testing rows: {len(X_test)}")
```

---

## 📝 Status Updates for Mentor's GitHub Issues

### Issue 1: Data Preparation

* **Assigned to:** Vishal Singh  
* **Status:** Completed & Sample Ready for Modeling  

1. **Dataset:** Used the Curitiba BRT GPS dataset from Hugging Face (`curitibaresearch/bus-linear-interpolation`).
2. **Storage:** Full raw data is ~5.1 GB and is stored on our shared Google Drive (git-ignored).
3. **Automated Pipeline:** Wrote a Python script (`Code/Dataset – Curitiba Bus Linear Interpolation.py`) that organizes raw itineraries and GPS tracking files.
4. **Working Sample:** Created a lightweight sample for Route 021 in `Progress/1_Dwell Time MWE & Prototype – 01 Oct 2026/data/` so the team can run everything locally without downloading 5 GB.

---

### Issue 2: Data Preprocessing

* **Assigned to:** Vishal Singh  
* **Status:** Completed (Prototype Features Ready for Priya & Nishant)  

1. **Dwell Time Calculation (Milestone 1):**
   - Created a 30m zone around stops to separate passenger wait time from road driving time.
   - Result: Bus spends ~12s at each stop (19% of trip). Factoring this in improved arrival predictions by **+14.4%**.

2. **Road Segment & 5-Min Features (Milestone 2):**
   - Broke trips into stop-to-stop road links.
   - Grouped travel times into 5-minute time slots (0–287) and flagged morning/evening rush hours.
   - Cleaned feature file is saved at: `Progress/2_Segment Travel Times & Features – Oct 2026/segment_features_5min.parquet`.

3. **Next Steps for Modeling (Priya & Nishant):**
   - **Current Data:** A small sample (549 segment runs) is provided so Priya and Nishant can build and debug their baseline models (Historical Avg, Kalman Filter, ANN) quickly.
   - **Split Strategy:** Standard 70% Train / 30% Test split sorted by time. Both teammates should train on the same 70% data so we can compare models fairly.
   - **Scaling Up:** Once their model code runs smoothly on this sample, we will run the pipeline across more routes for the final large dataset.
