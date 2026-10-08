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
├── 2_Segment Travel Times & Features – Oct 2026/      ← [Done] Extracted 5-minute road segment features
│   ├── extract_segment_features.py                    ← Feature extraction script
│   ├── segment_features_5min.parquet                  ← Dataset for training ML models
│   └── segment_features_sample.csv                    ← 100-row preview
│
└── 3_Baseline Travel Time Models – Oct 2026/          ← [Next] Train baseline models (Historical Avg, Kalman Filter, ANN)
```

---

## Milestone Details

### 1. Dwell Time MWE & Prototype (01 Oct 2026)
* **Goal:** Prove that we can calculate stop dwell time from low-frequency GPS pings and check if it improves arrival predictions.
* **How it works:** We put a 30-meter stop zone (15m before and 15m after each stop). Inside that zone the bus is stopped for passengers; between stops it is driving on the road.
* **Result:** Adding dwell time reduced arrival prediction error from **29.5s to 25.2s** (a **14.4% improvement**).
* **Meeting Reference:** [Minutes of Meeting — 01 Oct 2026](../Minutes%20of%20Meeting/01%20Oct%202026.md)

---

### 2. Segment Travel Times & Features (07 Oct 2026)
* **Goal:** Break down the bus route into stop-to-stop road links and calculate travel times in 5-minute intervals.
* **Why this matters:** Traffic changes throughout the day (morning rush vs evening rush). By tagging travel times with time of day and peak hours, our ML models can learn realistic road speeds.
* **Result:** Extracted 549 segment runs across 112 road segments. Evening peak speeds dropped to ~19 km/h compared to ~30 km/h in the morning.
* **Meeting Reference:** [Minutes of Meeting — 01 Oct 2026 (Section 3)](../Minutes%20of%20Meeting/01%20Oct%202026.md)

---

### 3. Baseline Travel Time Models (Planned)
* **Goal:** Build and compare 3 baseline models (Historical Average, Kalman Filter, and ANN) using the feature dataset generated in Milestone 2.
