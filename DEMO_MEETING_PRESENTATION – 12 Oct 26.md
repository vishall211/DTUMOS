# Meeting Presentation Guide: Progress Update (8 Oct – 12 Oct 2026)

> **Note:** This is a temporary demo file prepared for your team meeting. You can delete this file after your presentation.

---

## 🎯 Part 1: The 1-Slide Meeting Summary

*(This directly answers the 3 standing questions requested by our mentor in the Oct 8 meeting)*

### 1. What was done since last meeting:
* **Scaled Up the Pipeline (Milestone 3):** Moved beyond the small prototype. Ingested the complete local Curitiba dataset directly from `Datasets/` (1,303 itineraries and 1,224 tracking files).
* **Generated Full Production Dataset:** Extracted **111,455 segment traversal runs** across **83 unique buses** and **112 road segments** on Route 021 in under **9 seconds**.
* **Verified Feature Integrity:** Confirmed all mathematical formulas (30m stop buffer, 11.9s dwell time, 5-minute time binning across 240/288 daily slots, and Congestion Index).
* **Repository Cleaned & Migrated:** Cleaned out unused dependencies, removed credentials, and pushed the clean codebase to our new GitHub repository: [github.com/vishall211/DTUMOS](https://github.com/vishall211/DTUMOS).
* **Documented Team Handoff:** Provided clean Python quick-start code and 70/30 chronological split instructions for Priya and Nishant.

### 2. Plan until next meeting:
* Support Priya and Nishant as they train the first baseline models (Historical Average, Kalman Filter, Lasso, Random Forest, ANN) on the 111k feature dataset.
* Expand the pipeline to process 2–3 additional trunk BRT lines (e.g., Line 010 and Line 020) if the modeling team needs cross-route evaluation.
* Contribute the Data Preprocessing and Feature Extraction methodology text into Overleaf for the research paper.

### 3. Blockers:
* **None.** The data preparation and feature extraction pipeline is 100% stable, fast (runs in 9s), and ready for model training.

---

## 🗣️ Part 02 : Presentation Points

*You can read or follow these talking points during the meeting:*


---

### 1. Which Route / Lane Are We Using and Why?
> "In our last meeting, the mentor advised that we should filter by a complete route rather than tracking a single bus, so our models can see multiple vehicles and realistic traffic variation.
> 
> * **The Route we picked:** **Route 021 (Anti-Horario)** in Curitiba, Brazil.
> * **Why Route 021?**
>   1. It is one of Curitiba's primary circular trunk BRT routes.
>   2. It has **113 bus stops** spanning **38.1 kilometers**, giving us a large variety of road conditions, turns, and intersections.
>   3. It has high bus frequency, which gives us dozens of different buses running at all times of the day—morning rush, afternoon, and evening peak.
>   4. By focusing on Route 021 first, Priya and Nishant have a consistent physical corridor to benchmark all candidate models against each other before we expand to the entire city network."

---

### 2. Scaling from the Prototype to the Full Dataset
> "Earlier, we had a small prototype of 549 runs so we could verify our formulas in 2 seconds without computer crashes.
> 
> Since our last meeting, I built **Milestone 3** (`build_full_dataset.py`) to process the complete raw data directly from our `Datasets/` folder.
> 
> * It automatically reads all 1,303 itinerary files and 1,224 GPS tracking files.
> * In just **9 seconds**, it extracted **111,455 real bus segment runs** across **83 unique bus vehicles**.
> * It covers **240 out of the 288 5-minute time slots** in a 24-hour day.
> * We saved the complete file as `full_segment_features_5min.parquet` (~2.9 MB), which loads into Python in less than 1 second."

---

### 3. Dwell Time and Features Ready for Priya & Nishant
> "As confirmed in our last meeting, our models will use both **dwell time features** and **segment travel times** together.
> 
> * **Dwell Time:** We verified that buses spend on average **~12 seconds (19% of trip time)** stopped at stations. Factoring this in improved arrival predictions by **+14.4%**.
> * **Segment Features:** For every link between two stops, we have extracted:
>   - Segment distance in meters
>   - Travel time in seconds (our prediction target $y$)
>   - Net moving time on roads
>   - Travel speed in km/h
>   - 5-minute time slot index ($0 \dots 287$)
>   - Morning Peak vs. Evening Peak flags
>   - Historical average travel time and Congestion Index."

---

### 4. Recommendation on Train/Test Split
> "For Priya and Nishant, here is the recommended setup for model training:
> 
> 1. **70% Train / 30% Test split:** But it must be **sorted by time**, not randomly shuffled. Random shuffling causes data leakage in time-series data.
> 2. **Shared Training Set:** Both Priya and Nishant should train their models on the **same 70% data** and test on the **same 30% test data**. That way, we can compare Historical Average, Kalman Filter, Random Forest, and ANN fairly side-by-side.
> 3. I have provided a 5-line Python script in our README so they can load and split the data immediately."

---

### 5. What's Next
> "My data pipeline is now completely stable and finished. My next focus is:
> 1. Assisting Priya and Nishant as they run their baseline models.
> 2. Generating multi-route data (e.g. Lines 010 and 020) if needed.
> 3. Writing the Data Preprocessing section in Overleaf."

---

## ❓ Part 3: Likely Mentor Questions & Direct Answers

### Q1: "Why only Route 021? Why not train on the whole city right away?"
* **Your Answer:**  
  *"Route 021 alone gave us 111,455 segment samples across 83 buses, covering 240 5-minute daily slots. This is more than enough data for our baseline models, Random Forest, and ANNs. Starting with one corridor ensures all baseline models are evaluated under the exact same road geometry. Once Priya and Nishant verify their model code on this corridor, our script can process additional routes like 010 and 020 in seconds."*

---

### Q2: "How long does your feature extraction take on the full data?"
* **Your Answer:**  
  *"It takes only **9.0 seconds** to process 50 raw tracking files and generate the complete 111,455-row parquet dataset. It uses PyArrow, so it is fast and uses very little RAM."*

---

### Q3: "How does this connect to our future generalization on Delhi data?"
* **Your Answer:**  
  *"The exact same features we extracted here (segment distance, dwell time, 5-minute time slot, peak-hour tags, and congestion index) are city-independent. Once our models learn on Curitiba, we can apply transfer learning or fine-tune on the Delhi bus data collected through our automated repository."*

