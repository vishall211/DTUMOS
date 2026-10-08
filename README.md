# Digital Twin for Urban Mobility Systems (DTUMOS)

A research project focused on predicting bus arrival times and estimating stop dwell times (the time buses spend stopped for passengers) using low-frequency GPS tracking data.

---

## What this project is about

Standard transit apps usually predict bus arrival times using simple distance and speed, ignoring how long the bus actually stays stopped at stations. By calculating dwell time at each bus stop and dividing routes into 5-minute road segments, our models achieve much higher arrival time accuracy.

---

## Folder Structure

```
.
├── Progress/                     # Sprint milestones and deliverables
│   ├── 1_Dwell Time MWE & Prototype – 01 Oct 2026/
│   │   ├── simple_mwe.py         # Working dwell time script (~1 sec to run)
│   │   ├── prototype.html        # Interactive animated browser demo
│   │   ├── FLOWCHART.md          # 4-step diagram of how the system works
│   │   └── data/                 # Sample data for route 021
│   │
│   └── 2_Segment Travel Times & Features – Oct 2026/
│       ├── extract_segment_features.py     # Generates 5-minute road features
│       ├── segment_features_5min.parquet   # Dataset for training ML models
│       └── segment_features_sample.csv     # 100-row preview in CSV
│
├── Code/                         # Dataset preparation scripts
├── Datasets/                     # Local data folder (git-ignored, contains full ~5GB Curitiba dataset)
├── Minutes of Meeting/           # Team meeting notes from each week
├── Resources/                    # Research papers, preliminary reports, and Notion exports
├── DATA_PREPARATION_AND_PREPROCESSING.md  # Data pipeline documentation & ML team handoff guide
└── requirements.txt              # Python dependencies
```

---

## Quick Start

### 1. Set up the Python environment
```bash
# Activate your virtual environment
source .venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Run the Dwell Time benchmark (Milestone 1)
```bash
python "Progress/1_Dwell Time MWE & Prototype – 01 Oct 2026/simple_mwe.py"
```
Or double-click [`Progress/1_Dwell Time MWE & Prototype – 01 Oct 2026/prototype.html`](Progress/1_Dwell%20Time%20MWE%20%26%20Prototype%20%E2%80%93%2001%20Oct%202026/prototype.html) to open the interactive simulation in your browser.

### 3. Generate 5-Minute Segment Features (Milestone 2)
```bash
python "Progress/2_Segment Travel Times & Features – Oct 2026/extract_segment_features.py"
```
This processes the route into stop-to-stop segments and creates `segment_features_5min.parquet` for model training.

---

## Datasets

1. **Curitiba BRT (Brazil) — Main Dataset:**
   * This is our primary dataset for modeling.
   * Full data is ~5.1 GB and stored locally in `Datasets/` (git-ignored).
   * A small sample is included in `Progress/1_Dwell Time MWE & Prototype – 01 Oct 2026/data/` so anyone can test the code immediately without downloading the full files.

2. **Delhi Bus Transit Data (India):**
   * We plan to test model generalization on Indian bus data in later stages.
   * Rather than storing streaming data here, live collection is automated in a separate repository using GitHub Actions and cron jobs: [Delhi-Bus-Data-Automation](https://github.com/vishall211/Delhi-Bus-Data-Automation).
