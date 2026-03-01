"""
Public Transport Dataset Generator
Generates realistic dummy data for city bus/metro analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os

np.random.seed(42)
random.seed(42)

# ─── Configuration ────────────────────────────────────────────────────────────
ROUTES = {
    "R01": {"name": "Central – Airport Express", "type": "Bus", "stops": 12, "distance_km": 28.5, "capacity": 60},
    "R02": {"name": "City Loop (North)", "type": "Bus", "stops": 18, "distance_km": 22.1, "capacity": 60},
    "R03": {"name": "City Loop (South)", "type": "Bus", "stops": 16, "distance_km": 19.8, "capacity": 60},
    "R04": {"name": "Metro Line 1 (Red)", "type": "Metro", "stops": 24, "distance_km": 35.2, "capacity": 300},
    "R05": {"name": "Metro Line 2 (Blue)", "type": "Metro", "stops": 20, "distance_km": 30.6, "capacity": 300},
    "R06": {"name": "University Shuttle", "type": "Bus", "stops": 8, "distance_km": 11.3, "capacity": 45},
    "R07": {"name": "Industrial Zone Link", "type": "Bus", "stops": 10, "distance_km": 15.7, "capacity": 60},
    "R08": {"name": "Suburban Express East", "type": "Bus", "stops": 14, "distance_km": 24.4, "capacity": 60},
    "R09": {"name": "Metro Line 3 (Green)", "type": "Metro", "stops": 28, "distance_km": 42.0, "capacity": 300},
    "R10": {"name": "Night Owl Service", "type": "Bus", "stops": 20, "distance_km": 30.0, "capacity": 45},
}

STOPS_MAP = {
    "R01": ["Central Station", "Business District", "Tech Park", "Mall Junction", "Riverside", "West Gate",
            "Hospital Cross", "Exhibition Center", "Airport Cargo", "Airport Domestic", "Airport Int'l T1", "Airport Int'l T2"],
    "R04": ["Central", "Museum", "Market Square", "University", "Stadium", "Hospital", "Tech Hub",
            "Residential North", "Shopping Mall", "Park East", "Suburb Gate", "Industrial A",
            "Industrial B", "East Terminal", "River Cross", "Park West", "Sports Complex",
            "Convention Center", "Business Bay", "Finance District", "Government Hub",
            "Heritage Quarter", "Night Market", "South Terminal"],
}

# Fill remaining stops generically
for rid, rdata in ROUTES.items():
    if rid not in STOPS_MAP:
        STOPS_MAP[rid] = [f"{rdata['name'].split('(')[0].strip()} Stop {i+1}" for i in range(rdata["stops"])]

# GPS coordinates (city center ~lat 28.6, lon 77.2 — Delhi-like)
CENTER_LAT, CENTER_LON = 28.6139, 77.2090

def generate_stop_coords(route_id, n_stops):
    angle_start = random.uniform(0, 2 * np.pi)
    coords = []
    for i in range(n_stops):
        angle = angle_start + (i / n_stops) * np.pi * 1.5
        radius = 0.05 + 0.15 * (i / n_stops)
        lat = CENTER_LAT + radius * np.sin(angle) + np.random.normal(0, 0.002)
        lon = CENTER_LON + radius * np.cos(angle) + np.random.normal(0, 0.002)
        coords.append((round(lat, 5), round(lon, 5)))
    return coords

STOP_COORDS = {rid: generate_stop_coords(rid, ROUTES[rid]["stops"]) for rid in ROUTES}

# ─── Passenger Load Model ──────────────────────────────────────────────────────
def passenger_load_factor(hour, route_id, day_of_week):
    """Realistic passenger load based on time/route/day"""
    is_weekday = day_of_week < 5
    base = 0.15

    if route_id == "R06":  # University — heavy mid-morning, early afternoon
        peaks = {8: 0.85, 9: 0.90, 12: 0.70, 13: 0.65, 17: 0.80, 18: 0.75}
        if not is_weekday:
            return base + 0.05
    elif route_id == "R07":  # Industrial — early morning and evening
        peaks = {6: 0.80, 7: 0.85, 16: 0.70, 17: 0.80}
        if not is_weekday:
            return base
    elif route_id == "R10":  # Night Owl — late night
        peaks = {22: 0.50, 23: 0.55, 0: 0.40, 1: 0.30}
        if not is_weekday:
            peaks = {22: 0.65, 23: 0.70, 0: 0.55}
    elif route_id in ["R04", "R05", "R09"]:  # Metro — rush hours
        peaks = {7: 0.75, 8: 0.95, 9: 0.85, 12: 0.55, 17: 0.80, 18: 0.90, 19: 0.70}
        if not is_weekday:
            peaks = {10: 0.60, 11: 0.65, 14: 0.70, 15: 0.65, 19: 0.55}
    else:
        peaks = {7: 0.65, 8: 0.80, 9: 0.70, 12: 0.50, 17: 0.75, 18: 0.80}
        if not is_weekday:
            peaks = {10: 0.50, 11: 0.55, 14: 0.60, 15: 0.55}

    load = peaks.get(hour, base)
    return min(1.0, load + np.random.normal(0, 0.05))


# ─── Generate GPS Data ─────────────────────────────────────────────────────────
def generate_gps_data(days=90):
    records = []
    start_date = datetime(2024, 1, 1)

    for day_offset in range(days):
        date = start_date + timedelta(days=day_offset)
        dow = date.weekday()

        for route_id, rdata in ROUTES.items():
            # Frequency of trips per day
            if rdata["type"] == "Metro":
                trips_per_day = 80 if dow < 5 else 60
            elif route_id == "R10":
                trips_per_day = 8  # Night owl
            else:
                trips_per_day = 40 if dow < 5 else 25

            for trip_num in range(trips_per_day):
                # Distribute trips across operating hours
                if route_id == "R10":
                    hour = random.choice([21, 22, 23, 0, 1, 2, 3])
                else:
                    hour = random.choices(
                        range(5, 23),
                        weights=[3, 5, 8, 10, 8, 6, 7, 8, 10, 7, 5, 4, 4, 5, 8, 9, 6, 4],
                        k=1
                    )[0]

                minute = random.randint(0, 59)
                trip_start = date.replace(hour=hour, minute=minute)

                vehicle_id = f"VH-{route_id}-{(trip_num % 15) + 1:02d}"
                trip_id = f"TRIP-{route_id}-{date.strftime('%Y%m%d')}-{trip_num:03d}"

                coords = STOP_COORDS[route_id]
                stops = STOPS_MAP[route_id]
                cap = rdata["capacity"]
                load_factor = passenger_load_factor(hour, route_id, dow)

                stop_time = trip_start
                for stop_idx, (stop_name, (lat, lon)) in enumerate(zip(stops, coords)):
                    # Delay simulation
                    scheduled_gap = 3  # minutes between stops
                    delay = max(0, int(np.random.exponential(1.5)) if random.random() < 0.3 else 0)
                    stop_time += timedelta(minutes=scheduled_gap + delay)

                    records.append({
                        "timestamp": stop_time,
                        "trip_id": trip_id,
                        "vehicle_id": vehicle_id,
                        "route_id": route_id,
                        "route_name": rdata["name"],
                        "route_type": rdata["type"],
                        "stop_sequence": stop_idx + 1,
                        "stop_name": stop_name,
                        "latitude": lat + np.random.normal(0, 0.0001),
                        "longitude": lon + np.random.normal(0, 0.0001),
                        "speed_kmh": round(np.random.normal(28 if rdata["type"] == "Metro" else 22, 5), 1),
                        "passengers_onboard": max(0, int(cap * load_factor * np.random.uniform(0.8, 1.2))),
                        "capacity": cap,
                        "delay_minutes": delay,
                        "day_of_week": date.strftime("%A"),
                        "date": date.date(),
                        "hour": hour,
                    })

    return pd.DataFrame(records)


# ─── Generate Ticketing Data ───────────────────────────────────────────────────
def generate_ticketing_data(days=90):
    records = []
    start_date = datetime(2024, 1, 1)
    ticket_id = 1

    FARE_TABLE = {
        "Bus": {"base": 15, "per_stop": 3},
        "Metro": {"base": 20, "per_stop": 5},
    }
    PAYMENT_METHODS = ["Smart Card", "Cash", "Mobile App", "QR Code"]
    PASSENGER_TYPES = ["Adult", "Student", "Senior", "Child", "Employee Pass"]

    for day_offset in range(days):
        date = start_date + timedelta(days=day_offset)
        dow = date.weekday()

        for route_id, rdata in ROUTES.items():
            cap = rdata["capacity"]
            fare = FARE_TABLE[rdata["type"]]
            stops = STOPS_MAP[route_id]
            n_stops = len(stops)

            base_daily = 1200 if rdata["type"] == "Metro" else 400
            daily_passengers = int(base_daily * (0.85 if route_id in ["R07", "R10"] else 1.0))
            if dow >= 5:
                daily_passengers = int(daily_passengers * 0.7)

            for _ in range(daily_passengers):
                hour = random.choices(
                    range(5, 23) if route_id != "R10" else range(21, 24),
                    weights=[3, 5, 8, 10, 8, 6, 7, 8, 10, 7, 5, 4, 4, 5, 8, 9, 6, 4] if route_id != "R10" else [4, 4, 2],
                    k=1
                )[0]
                boarding_stop_idx = random.randint(0, n_stops - 3)
                alighting_stop_idx = random.randint(boarding_stop_idx + 1, min(boarding_stop_idx + 10, n_stops - 1))
                stops_travelled = alighting_stop_idx - boarding_stop_idx
                fare_amount = fare["base"] + fare["per_stop"] * stops_travelled

                p_type = random.choices(
                    PASSENGER_TYPES,
                    weights=[60, 20, 10, 5, 5]
                )[0]
                discount = {"Adult": 0, "Student": 0.25, "Senior": 0.40, "Child": 0.50, "Employee Pass": 1.0}
                final_fare = int(fare_amount * (1 - discount[p_type]))

                records.append({
                    "ticket_id": f"TKT-{ticket_id:07d}",
                    "date": date.date(),
                    "hour": hour,
                    "day_of_week": date.strftime("%A"),
                    "route_id": route_id,
                    "route_name": rdata["name"],
                    "route_type": rdata["type"],
                    "boarding_stop": stops[boarding_stop_idx],
                    "alighting_stop": stops[alighting_stop_idx],
                    "stops_travelled": stops_travelled,
                    "passenger_type": p_type,
                    "payment_method": random.choices(PAYMENT_METHODS, weights=[45, 25, 20, 10])[0],
                    "fare_amount": final_fare,
                    "journey_duration_min": stops_travelled * 3 + random.randint(-2, 8),
                })
                ticket_id += 1

    return pd.DataFrame(records)


# ─── Generate Route Metadata ────────────────────────────────────────────────────
def generate_route_metadata():
    rows = []
    for rid, rdata in ROUTES.items():
        coords = STOP_COORDS[rid]
        stops = STOPS_MAP[rid]
        for i, (stop_name, (lat, lon)) in enumerate(zip(stops, coords)):
            rows.append({
                "route_id": rid,
                "route_name": rdata["name"],
                "route_type": rdata["type"],
                "stop_sequence": i + 1,
                "stop_name": stop_name,
                "latitude": lat,
                "longitude": lon,
                "total_stops": rdata["stops"],
                "route_distance_km": rdata["distance_km"],
                "vehicle_capacity": rdata["capacity"],
            })
    return pd.DataFrame(rows)


# ─── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print("Generating GPS data (90 days)...")
    gps_df = generate_gps_data(days=90)
    gps_df.to_csv("data/gps_data.csv", index=False)
    print(f"  → {len(gps_df):,} GPS records saved")

    print("Generating Ticketing data (90 days)...")
    ticket_df = generate_ticketing_data(days=90)
    ticket_df.to_csv("data/ticketing_data.csv", index=False)
    print(f"  → {len(ticket_df):,} ticket records saved")

    print("Generating Route metadata...")
    route_df = generate_route_metadata()
    route_df.to_csv("data/route_metadata.csv", index=False)
    print(f"  → {len(route_df)} stop records saved")

    print("\nAll datasets saved to /data/")
    print("Summary:")
    print(f"  GPS records:     {len(gps_df):,}")
    print(f"  Ticket records:  {len(ticket_df):,}")
    print(f"  Route stops:     {len(route_df)}")
