"""
=============================================================================
DTUMOS — Milestone 2: Segment-Wise Travel Time & Feature Engineering
=============================================================================
Purpose:
  1. Divides bus routes into consecutive stop-to-stop road segments.
  2. Measures actual traversal times, distances, speeds, and dwell times.
  3. Bins data into 5-minute time intervals across the 24-hour day.
  4. Generates temporal, spatial, and congestion features for model training.

Meeting Reference:
  - Minutes of Meeting 01 Oct 2026 (Section 3: Road Segments & 5-min intervals)
  - Minutes of Meeting 05 Oct 2026 (Modeling preparation for Priya & Nishant)
=============================================================================
"""

import os
import glob
import numpy as np
import pandas as pd
import pyarrow.parquet as pq


def build_segment_features():
    print("=" * 75)
    print("🚦 MILESTONE 2: ROAD SEGMENT TRAVEL TIMES & 5-MINUTE FEATURE EXTRACTION")
    print("=" * 75)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_dir = script_dir

    # 1. Locate Datasets
    curitiba_itin_dir = os.path.join(project_root, "Datasets", "Curitibaresearch_Bus-linear-interpolation", "bus_itineraries")
    curitiba_track_dir = os.path.join(project_root, "Datasets", "Curitibaresearch_Bus-linear-interpolation", "bus_tracking")
    sample_data_dir = os.path.join(project_root, "Progress", "1_Dwell Time MWE & Prototype – 01 Oct 2026", "data")

    # Load itineraries
    itin_files = glob.glob(os.path.join(curitiba_itin_dir, "*.parquet"))
    if not itin_files:
        sample_itin = os.path.join(sample_data_dir, "bus_itineraries.parquet")
        if os.path.exists(sample_itin):
            itin_files = [sample_itin]
        else:
            raise FileNotFoundError("No itinerary files found.")

    print(f"\n[Step 1] Loading Route Itinerary (Line 021 Anti-Horario)...")
    df_itin = pq.read_table(itin_files[0]).to_pandas()
    route = df_itin[(df_itin["line_code"] == "021") & (df_itin["line_way"] == "Anti-Horario")]
    route = route.drop_duplicates("seq").sort_values("seq").reset_index(drop=True)

    # Compute cumulative distance for each stop along the route
    route["dist_m"] = 0.0
    for i in range(len(route) - 1):
        route.loc[i + 1, "dist_m"] = route.loc[i, "dist_m"] + float(route.loc[i, "next_stop_delta_s"])

    print(f"  ✓ Route loaded: {len(route)} stops | Length: {route['dist_m'].iloc[-1]/1000:.1f} km")

    # Load tracking GPS pings
    track_files = sorted(glob.glob(os.path.join(curitiba_track_dir, "*.parquet")))
    if not track_files:
        sample_track = os.path.join(sample_data_dir, "bus_tracking.parquet")
        if os.path.exists(sample_track):
            track_files = [sample_track]
        else:
            raise FileNotFoundError("No tracking files found.")

    print(f"\n[Step 2] Ingesting GPS tracking observations across all vehicles...")
    df_track = pq.read_table(track_files[0]).to_pandas()
    df_track = df_track[(df_track["line_code"] == "021") & (df_track["itinerary_id"] == "Anti-Horario")]
    print(f"  ✓ Found {len(df_track)} GPS pings across {df_track['vehicle'].nunique()} vehicles")

    # Merge tracking with route geometry
    merged = pd.merge(
        df_track,
        route[["seq", "id", "dist_m", "name", "latitude", "longitude"]],
        on=["seq", "id"]
    ).sort_values(["vehicle", "event_timestamp"]).reset_index(drop=True)
    merged["dt"] = pd.to_datetime(merged["event_timestamp"])

    # -------------------------------------------------------------------------
    # Step 3: Segment Traversal Extraction
    # -------------------------------------------------------------------------
    print(f"\n[Step 3] Segmenting bus runs into physical stop-to-stop links...")
    records = []
    trip_id = 0

    for vehicle, grp in merged.groupby("vehicle"):
        grp = grp.sort_values("dt").reset_index(drop=True)
        if len(grp) < 2:
            continue

        trip_id += 1
        for i in range(len(grp) - 1):
            s1 = grp.iloc[i]
            s2 = grp.iloc[i + 1]

            dt_sec = (s2["dt"] - s1["dt"]).total_seconds()
            d_m = s2["dist_m"] - s1["dist_m"]
            d_seq = s2["seq"] - s1["seq"]

            # Filter valid consecutive stop transitions (10s to 10 mins)
            if d_seq == 1 and 10.0 <= dt_sec <= 600.0 and d_m > 0:
                speed_mps = d_m / dt_sec
                speed_kmh = speed_mps * 3.6

                hour = s1["dt"].hour
                minute = s1["dt"].minute

                # 5-minute interval bin (0 to 287 throughout the 24h day)
                bin_5min = (hour * 60 + minute) // 5
                slot_start = f"{hour:02d}:{(minute // 5) * 5:02d}"
                slot_end = f"{hour:02d}:{min(59, (minute // 5) * 5 + 5):02d}"
                time_slot_str = f"{slot_start}-{slot_end}"

                # Peak-hour classification
                # Morning peak: 07:00 - 09:30 | Evening peak: 17:00 - 19:30
                if (7 <= hour < 9) or (hour == 9 and minute <= 30):
                    peak_period = "Morning Peak (07:00-09:30)"
                    is_peak = 1
                elif (17 <= hour < 19) or (hour == 19 and minute <= 30):
                    peak_period = "Evening Peak (17:00-19:30)"
                    is_peak = 1
                else:
                    peak_period = "Off-Peak"
                    is_peak = 0

                # Estimated dwell time from Milestone 1 benchmark (~11.9s)
                est_dwell = 11.9
                net_moving_time = max(1.0, round(dt_sec - est_dwell, 1))

                records.append({
                    "trip_id": f"TRIP_{trip_id:03d}_{vehicle}",
                    "vehicle": vehicle,
                    "line_code": s1["line_code"],
                    "from_stop_seq": int(s1["seq"]),
                    "to_stop_seq": int(s2["seq"]),
                    "segment_id": f"SEG_{int(s1['seq']):03d}_{int(s2['seq']):03d}",
                    "from_stop_name": s1["name"],
                    "to_stop_name": s2["name"],
                    "distance_m": round(d_m, 1),
                    "departure_time": s1["dt"],
                    "arrival_time": s2["dt"],
                    "travel_time_sec": round(dt_sec, 1),
                    "dwell_time_sec": est_dwell,
                    "net_moving_sec": net_moving_time,
                    "speed_kmh": round(speed_kmh, 2),
                    "time_bin_5min": int(bin_5min),
                    "time_slot": time_slot_str,
                    "hour": hour,
                    "minute": minute,
                    "day_of_week": s1["dt"].day_name(),
                    "day_index": s1["dt"].weekday(),
                    "is_weekend": 1 if s1["dt"].weekday() >= 5 else 0,
                    "is_peak_hour": is_peak,
                    "peak_period": peak_period,
                })

    df_features = pd.DataFrame(records)
    print(f"  ✓ Successfully extracted {len(df_features)} segment traversals!")

    # -------------------------------------------------------------------------
    # Step 4: Add Historical Context & Congestion Index
    # -------------------------------------------------------------------------
    print(f"\n[Step 4] Computing historical baselines & Congestion Index...")

    # Calculate historical average travel time per segment
    seg_hist_avg = df_features.groupby("segment_id")["travel_time_sec"].transform("mean")
    df_features["segment_hist_mean_sec"] = seg_hist_avg.round(1)

    # Congestion Index = Actual Travel Time / Historical Mean Travel Time
    # CI > 1.0 indicates slower than average (traffic congestion)
    # CI < 1.0 indicates free-flowing conditions
    df_features["congestion_index"] = (
        df_features["travel_time_sec"] / df_features["segment_hist_mean_sec"]
    ).round(2)

    # -------------------------------------------------------------------------
    # Step 5: Save Dataset
    # -------------------------------------------------------------------------
    parquet_path = os.path.join(output_dir, "segment_features_5min.parquet")
    csv_path = os.path.join(output_dir, "segment_features_sample.csv")

    df_features.to_parquet(parquet_path, index=False)
    df_features.head(100).to_csv(csv_path, index=False)

    print(f"  ✓ Saved Parquet dataset: {parquet_path} ({os.path.getsize(parquet_path)/1024:.1f} KB)")
    print(f"  ✓ Saved CSV preview (100 rows): {csv_path}")

    # -------------------------------------------------------------------------
    # Step 6: Summary Analytics Report
    # -------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print("📊 SEGMENT FEATURE SUMMARY ANALYTICS")
    print("=" * 75)
    print(f"Total Traversal Samples:       {len(df_features)}")
    print(f"Distinct Road Segments:        {df_features['segment_id'].nunique()}")
    print(f"Time Bins Covered (5-min):     {df_features['time_bin_5min'].nunique()} / 288 bins")
    print(f"Average Segment Distance:      {df_features['distance_m'].mean():.1f} meters")
    print(f"Average Segment Travel Time:   {df_features['travel_time_sec'].mean():.1f} seconds")
    print(f"Overall Average Speed:         {df_features['speed_kmh'].mean():.1f} km/h")

    print("\n🚦 Performance by Traffic Period:")
    summary_peak = df_features.groupby("peak_period").agg(
        traversals=("travel_time_sec", "count"),
        avg_speed_kmh=("speed_kmh", "mean"),
        avg_travel_time_sec=("travel_time_sec", "mean"),
        avg_congestion_index=("congestion_index", "mean"),
    ).round(2)
    print(summary_peak.to_string())

    print("\n⚠️  Top 3 Slowest Segments (Highest Congestion Index):")
    top_congested = df_features.sort_values("congestion_index", ascending=False).head(3)
    for _, row in top_congested.iterrows():
        print(f"  • {row['segment_id']} ({row['from_stop_name'][:20]} -> {row['to_stop_name'][:20]}): "
              f"{row['travel_time_sec']}s (Speed: {row['speed_kmh']} km/h | Congestion Index: {row['congestion_index']:.2f})")

    print("\n" + "=" * 75)
    print("✅ MILESTONE 2: FEATURE DATASET READY FOR MODEL TRAINING!")
    print("=" * 75)
    return df_features


if __name__ == "__main__":
    build_segment_features()

