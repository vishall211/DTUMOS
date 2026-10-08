# Milestone 1: Dwell Time MWE & Prototype (01 Oct 2026)

## Why we made this

In our team meeting on 28 September 2026, our mentor asked us to build a **Minimum Working Example (MWE)** to test whether we can calculate bus dwell times from low-frequency GPS tracking data. 

On 1 October 2026, I (Vishal )presented this working demo to the team. It proved that:
1. We can separate dwell time (time spent at stations) from moving time (driving on the road) using a 30-meter stop zone.
2. Including dwell time dropped our arrival prediction error from **29.5 seconds down to 25.2 seconds**, which is about **14.4% more accurate**.

---

## Files in this folder

| File | What it is | How to use |
| :--- | :--- | :--- |
| **`simple_mwe.py`** | Python script that loads Curitiba Line 021, estimates dwell times, and checks arrival accuracy. | Run `python "Progress/1_Dwell Time MWE & Prototype – 01 Oct 2026/simple_mwe.py"` (takes ~1 sec) |
| **`prototype.html`** | Interactive visual prototype showing the bus driving along stops and dwelling for passengers. | Double-click to open in any web browser |
| **`FLOWCHART.md`** | 4-step diagram explaining the process in plain English. | View in VS Code or GitHub preview |
| **`data/`** | Small sample data for route 021 so anyone can run the script without downloading the full 5 GB dataset. | Used automatically by `simple_mwe.py` |

---

## How Dwell Time is calculated

1. **The 30-meter Stop Zone:** We set a 30-meter boundary around each bus stop (15 meters before the stop and 15 meters after).
2. **Inside vs. Outside:**
   * When the bus is inside the 30-meter boundary, it is **dwelling** (passengers boarding or getting off).
   * When the bus is outside the boundary, it is **moving** on the road.
3. **Trip Breakdown (Line 021 Anti-Horario):**
   * Average dwell time per stop: **11.9 seconds**
   * **81.0%** of the trip is driving on roads.
   * **19.0%** of the trip is stopped at stations.

---

## How to run the script

```bash
python "Progress/1_Dwell Time MWE & Prototype – 01 Oct 2026/simple_mwe.py"
```
It takes about 1 second and prints out the results directly in your terminal.
