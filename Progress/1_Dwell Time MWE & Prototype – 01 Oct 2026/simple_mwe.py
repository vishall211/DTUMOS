"""
=============================================================================
DTUMOS: Simple Minimum Working Example (Curitiba Bus Dataset Only)
=============================================================================
This simple script shows:
1. Loading real bus route and GPS pings from the Curitiba BRT dataset.
2. Calculating how long the bus stops at each station (Dwell Time).
3. Predicting travel time to the next stop with and without dwell time.
=============================================================================
"""

import os
import glob
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy.optimize import minimize


def run_simple_mwe():
    print("=" * 70)
    print("🚍 CURITIBA BUS: SIMPLE MINIMUM WORKING EXAMPLE")
    print("=" * 70)

    # Find project root and local sample data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    local_data_dir = os.path.join(script_dir, "data")

    curitiba_dir = os.path.join(project_root, "Datasets", "Curitibaresearch_Bus-linear-interpolation")
    itin_dir = os.path.join(curitiba_dir, "bus_itineraries")
    track_dir = os.path.join(curitiba_dir, "bus_tracking")

    # ---------------------------------------------------------
    # STEP 1: Load Route Itinerary (Curitiba Route 021)
    # ---------------------------------------------------------
    print("\n[Step 1] Loading Curitiba Bus Route (Line 021 - Anti-Horario)...")
    itin_files = glob.glob(os.path.join(itin_dir, "*.parquet"))
    if not itin_files:
        local_itin = os.path.join(local_data_dir, "bus_itineraries.parquet")
        if os.path.exists(local_itin):
            itin_files = [local_itin]
        else:
            print("❌ Error: No itinerary files found in:", itin_dir)
            return

    # Read the first parquet file containing Route 021
    df_itin = pq.read_table(itin_files[0]).to_pandas()
    route = df_itin[(df_itin["line_code"] == "021") & (df_itin["line_way"] == "Anti-Horario")]
    route = route.drop_duplicates("seq").sort_values("seq").reset_index(drop=True)

    # Compute distance along the route for each stop
    route["dist_m"] = 0.0
    for i in range(len(route) - 1):
        route.loc[i + 1, "dist_m"] = route.loc[i, "dist_m"] + float(route.loc[i, "next_stop_delta_s"])

    print(f"  ✓ Route loaded: {len(route)} stops")
    print(f"  ✓ Total route length: {route['dist_m'].iloc[-1] / 1000.0:.1f} km")
    print("\n  Sample Stops:")
    for _, row in route.head(4).iterrows():
        print(f"    - Stop #{int(row['seq'])}: {row['name'][:28]:<28} | Distance: {row['dist_m']:>7.1f}m")

    # ---------------------------------------------------------
    # STEP 2: Load Bus GPS Tracking Data (Bus MB300)
    # ---------------------------------------------------------
    print("\n[Step 2] Loading GPS tracking pings for Bus MB300...")
    track_files = sorted(glob.glob(os.path.join(track_dir, "*.parquet")))
    if not track_files:
        local_track = os.path.join(local_data_dir, "bus_tracking.parquet")
        if os.path.exists(local_track):
            track_files = [local_track]
        else:
            print("❌ Error: No tracking files found in:", track_dir)
            return

    df_track = pq.read_table(track_files[0]).to_pandas()
    bus_pings = df_track[
        (df_track["line_code"] == "021") &
        (df_track["itinerary_id"] == "Anti-Horario") &
        (df_track["vehicle"] == "MB300")
    ].sort_values("event_timestamp").reset_index(drop=True)

    print(f"  ✓ Found {len(bus_pings)} GPS pings for Bus MB300")

    # Match pings with stops
    trip = pd.merge(bus_pings, route[["seq", "id", "dist_m", "name"]], on=["seq", "id"]).sort_values("event_timestamp").reset_index(drop=True)
    trip["time_sec"] = (pd.to_datetime(trip["event_timestamp"]).astype("int64") // 10**9)
    trip["time_sec"] = trip["time_sec"] - trip["time_sec"].iloc[0]  # Start at 0 seconds

    stops_in_trip = len(trip)
    print(f"  ✓ Trip covers {stops_in_trip} stops from '{trip['name'].iloc[0]}' to '{trip['name'].iloc[-1]}'")
    print(f"  ✓ Total trip time recorded: {trip['time_sec'].iloc[-1]:.0f} seconds (~{trip['time_sec'].iloc[-1]/60:.1f} minutes)")

    # ---------------------------------------------------------
    # STEP 3: Calculate Dwell Time at Each Stop
    # ---------------------------------------------------------
    print("\n[Step 3] Calculating Dwell Time at each bus stop...")
    print("  (Dwell Time = how many seconds the bus stays stopped for passengers)")

    # For each stop s:
    # Total segment time = Moving Time on road + Dwell Time at stop
    S = stops_in_trip
    stop_positions = trip["dist_m"].to_numpy()
    observed_times = trip["time_sec"].to_numpy()

    # Physical constraints:
    # 1. Moving speed <= 20 m/s (~72 km/h) -> Moving Time >= segment_distance / 20
    # 2. Dwell time >= 0
    # We solve for: TT (moving times) and ST (dwell times)
    min_moving_times = np.zeros(S - 1)
    for s in range(S - 1):
        dist = max(10.0, stop_positions[s + 1] - stop_positions[s] - 30.0)
        min_moving_times[s] = dist / 20.0  # max 20 m/s speed

    # Quick optimization to find exact dwell times
    def objective(p):
        TT = p[:S - 1]
        ST = p[S - 1:]
        # Reconstruct arrival times at each stop
        sim_times = np.zeros(S)
        for i in range(S - 1):
            sim_times[i + 1] = sim_times[i] + ST[i] + TT[i]
        # Match observed GPS arrival times + regularize dwell around 12 seconds
        error_obs = np.sum((sim_times - observed_times) ** 2)
        dwell_penalty = 0.5 * np.sum((ST - 12.0) ** 2)
        return error_obs + dwell_penalty

    # Initial guess
    total_time = observed_times[-1]
    est_dwell_each = 12.0
    p0 = np.concatenate([min_moving_times + 20.0, np.full(S, est_dwell_each)])

    # Bounds: moving time >= min_moving_time, dwell time >= 0
    bounds = [(min_moving_times[i], None) for i in range(S - 1)] + [(0.0, 60.0) for _ in range(S)]

    res = minimize(objective, p0, method="L-BFGS-B", bounds=bounds)
    p_opt = res.x

    moving_times = p_opt[:S - 1]
    dwell_times = p_opt[S - 1:]

    total_moving = np.sum(moving_times)
    total_dwell = np.sum(dwell_times)
    dwell_pct = (total_dwell / (total_moving + total_dwell)) * 100.0

    print(f"\n  📊 DWELL TIME RESULTS:")
    print(f"  • Average Dwell Time per Stop:   {np.mean(dwell_times):.1f} seconds")
    print(f"  • Minimum Dwell Time:            {np.min(dwell_times):.1f} seconds")
    print(f"  • Maximum Dwell Time:            {np.max(dwell_times):.1f} seconds")
    print(f"  • Total Time Moving on Road:     {total_moving:.1f} seconds ({100 - dwell_pct:.1f}%)")
    print(f"  • Total Time Stopped at Stations:{total_dwell:.1f} seconds ({dwell_pct:.1f}%)")

    print("\n  Sample Dwell Times for the first 5 stops:")
    for s in range(min(5, S)):
        print(f"    - Stop #{s+1} ({trip['name'].iloc[s][:25]}): Dwell Time = {dwell_times[s]:>4.1f} seconds")

    # ---------------------------------------------------------
    # STEP 4: Predict Next Stop Arrival Time (ETA)
    # ---------------------------------------------------------
    print("\n[Step 4] Predicting Arrival Time to Next Stop (TTE)...")

    # Compare:
    # 1. Simple Average Baseline (guesses average segment time)
    # 2. Smart Model (uses segment distance + extracted dwell time)
    actual_segment_times = np.diff(observed_times)
    baseline_predictions = np.full(len(actual_segment_times), np.mean(actual_segment_times))

    # Smart prediction = distance / avg_speed + estimated dwell
    avg_speed = np.mean([
        (stop_positions[i+1] - stop_positions[i]) / moving_times[i]
        for i in range(len(moving_times))
    ])
    smart_predictions = np.array([
        ((stop_positions[i+1] - stop_positions[i]) / avg_speed) + dwell_times[i]
        for i in range(len(actual_segment_times))
    ])

    mae_baseline = np.mean(np.abs(actual_segment_times - baseline_predictions))
    mae_smart = np.mean(np.abs(actual_segment_times - smart_predictions))

    print(f"  • Average Error without Dwell Time:  {mae_baseline:.1f} seconds")
    print(f"  • Average Error WITH Dwell Time:     {mae_smart:.1f} seconds")
    improvement = ((mae_baseline - mae_smart) / mae_baseline) * 100.0
    print(f"  ✓ Accuracy Improvement:             +{improvement:.1f}% more accurate!")

    print("\n" + "=" * 70)
    print("✅ SIMPLE MINIMUM WORKING EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_simple_mwe()
