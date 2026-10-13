# Project Milestones & Progress

This folder tracks our progress week by week, following our team meetings and tasks assigned by our mentor.

---

## Roadmap

```
Progress/
├── README.md                                          ← (You are here)
│
├── 1_Dwell Time MWE & Prototype – 01 Oct 2026/        ← [Done] Proved dwell time extraction (+14.4% accuracy boost)
│   ├── simple_mwe.py                                  ← Python code for the demo
│   ├── prototype.html                                 ← Interactive browser demo
│   ├── FLOWCHART.md                                   ← 4-step diagram
│   └── data/                                          ← Sample data for route 021
│
├── 2_Segment Travel Times & Features – Oct 2026/      ← [Done] Prototype 5-minute road segment features
│   ├── extract_segment_features.py                    ← Feature extraction script
│   ├── segment_features_5min.parquet                  ← Prototype dataset (~549 runs)
│   └── segment_features_sample.csv                    ← 100-row preview
│
├── 3_Full Scale Features & Preprocessing – Oct 2026/  ← [Done] Full-scale dataset (118,386 samples) for ML models
│   ├── build_full_dataset.py                          ← Production pipeline script
│   ├── full_segment_features_5min.parquet             ← Full-scale training dataset (~3.1 MB)
│   └── full_segment_features_sample.csv               ← 100-row preview
│
└── 4_Baseline Travel Time Models – Oct 2026/          ← [Next] Train baseline models (Historical Avg, Kalman Filter, ANN)
```

---

## Milestone Details

### 1. Dwell Time MWE & Prototype (01 Oct 2026)
* **Goal:** Prove that we can calculate stop dwell time from low-frequency GPS pings and check if it improves arrival predictions.
* **How it works:** We put a 30-meter stop zone (15m before and 15m after each stop). Inside that zone the bus is stopped for passengers; between stops it is driving on the road.
* **Result:** Adding dwell time reduced arrival prediction error from **29.5s to 25.2s** (a **14.4% improvement**).
* **Meeting Reference:** [Minutes of Meeting — 01 Oct 2026](../Minutes%20of%20Meeting/01%20Oct%202026.md)

---

### 2. Segment Travel Times & Features Prototype (07 Oct 2026)
* **Goal:** Break down the bus route into stop-to-stop road links and calculate travel times in 5-minute intervals on a verified working sample.
* **Why this matters:** Validated the feature extraction pipeline in under 2 seconds without risking memory overload.
* **Result:** Extracted 549 segment runs across 112 road segments. Evening peak speeds dropped to ~19 km/h compared to ~30 km/h in the morning.
* **Meeting Reference:** [Minutes of Meeting — 01 Oct 2026 (Section 3)](../Minutes%20of%20Meeting/01%20Oct%202026.md)

---

### 3. Full-Scale Feature Dataset (12 Oct 2026)
* **Goal:** Scale the pipeline to process complete raw AVL tracking files across multiple days and vehicles.
* **Result:** Extracted **118,386 segment traversal samples** across **88 bus vehicles** covering **240 out of 288 5-minute daily bins**.
* **Deliverable:** `full_segment_features_5min.parquet` (~3.1 MB) ready for Priya & Nishant to train baseline and deep learning models.

---

### 4. Baseline Travel Time Models (Planned)
* **Goal:** Train and compare baseline models (Historical Average, Kalman Filter, Lasso, Random Forest, ANN) using the full-scale feature dataset generated in Milestone 3.
