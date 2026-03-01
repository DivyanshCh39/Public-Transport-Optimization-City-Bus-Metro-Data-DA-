"""
Transit Analytics Engine
Core analysis functions for Public Transport Optimization
"""

import pandas as pd
import numpy as np
import json
import os

# data folder is inside the same directory as analytics.py
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_data():
    gps = pd.read_csv(os.path.join(DATA_DIR, 'gps_data.csv'),
                      parse_dates=['timestamp', 'date'])
    tickets = pd.read_csv(os.path.join(DATA_DIR, 'ticketing_data.csv'),
                          parse_dates=['date'])
    routes = pd.read_csv(os.path.join(DATA_DIR, 'route_metadata.csv'))
    return gps, tickets, routes

def peak_hours_analysis(tickets):
    """Identify peak hours by total passenger journeys"""
    hourly = tickets.groupby(['hour', 'day_of_week']).size().reset_index(name='journeys')
    overall_peak = tickets.groupby('hour').size().reset_index(name='total_journeys')
    overall_peak['pct_of_day'] = (overall_peak['total_journeys'] / overall_peak['total_journeys'].sum() * 100).round(2)
    overall_peak['is_peak'] = overall_peak['total_journeys'] > overall_peak['total_journeys'].quantile(0.75)
    return overall_peak


def route_efficiency(gps, tickets):
    """Calculate efficiency metrics per route"""
    # Load factor per route
    gps['load_factor'] = (gps['passengers_onboard'] / gps['capacity']).clip(0, 1)
    avg_load = gps.groupby('route_id').agg(
        avg_load_factor=('load_factor', 'mean'),
        avg_delay=('delay_minutes', 'mean'),
        avg_speed=('speed_kmh', 'mean'),
        total_trips=('trip_id', 'nunique'),
    ).reset_index()

    # Revenue per route
    revenue = tickets.groupby('route_id').agg(
        total_revenue=('fare_amount', 'sum'),
        total_passengers=('ticket_id', 'count'),
        avg_fare=('fare_amount', 'mean'),
    ).reset_index()

    merged = avg_load.merge(revenue, on='route_id')
    merged['revenue_per_trip'] = (merged['total_revenue'] / merged['total_trips']).round(2)
    merged['efficiency_score'] = (
        (merged['avg_load_factor'] * 0.4) +
        ((1 - merged['avg_delay'].clip(0, 10) / 10) * 0.3) +
        ((merged['avg_speed'] / 50).clip(0, 1) * 0.3)
    ).round(3) * 100

    route_meta = pd.read_csv(os.path.join(DATA_DIR, 'route_metadata.csv'))
    route_info = route_meta.groupby('route_id').first()[['route_name', 'route_type', 'route_distance_km']].reset_index()
    merged = merged.merge(route_info, on='route_id')
    return merged


def underutilized_routes(efficiency_df, threshold=0.40):
    """Flag routes with average load factor below threshold"""
    under = efficiency_df[efficiency_df['avg_load_factor'] < threshold].copy()
    under['recommendation'] = under['avg_load_factor'].apply(
        lambda x: "Consider reducing frequency" if x < 0.25 else "Review schedule / merge trips"
    )
    return under[['route_id', 'route_name', 'route_type', 'avg_load_factor', 'avg_delay',
                   'total_passengers', 'total_revenue', 'recommendation']]


def passenger_load_trends(gps):
    """Hourly average load factor per route type"""
    gps['load_factor'] = (gps['passengers_onboard'] / gps['capacity']).clip(0, 1)
    trend = gps.groupby(['hour', 'route_type'])['load_factor'].mean().reset_index()
    trend['load_factor'] = trend['load_factor'].round(4)
    return trend


def schedule_optimization_suggestions(gps, tickets):
    """Generate actionable schedule optimization suggestions"""
    gps['load_factor'] = (gps['passengers_onboard'] / gps['capacity']).clip(0, 1)
    hourly_route = gps.groupby(['route_id', 'hour'])['load_factor'].mean().reset_index()

    suggestions = []
    for route_id in hourly_route['route_id'].unique():
        route_data = hourly_route[hourly_route['route_id'] == route_id]
        peak_hours = route_data[route_data['load_factor'] > 0.75]['hour'].tolist()
        low_hours = route_data[route_data['load_factor'] < 0.25]['hour'].tolist()

        if peak_hours:
            suggestions.append({
                "route_id": route_id,
                "type": "Increase Frequency",
                "affected_hours": peak_hours,
                "reason": f"Load factor exceeds 75% during hours: {peak_hours}",
                "priority": "High"
            })
        if low_hours:
            suggestions.append({
                "route_id": route_id,
                "type": "Reduce Frequency",
                "affected_hours": low_hours,
                "reason": f"Load factor below 25% during hours: {low_hours}",
                "priority": "Medium"
            })

    return pd.DataFrame(suggestions)


def daily_revenue_trend(tickets):
    daily = tickets.groupby(['date', 'route_type']).agg(
        revenue=('fare_amount', 'sum'),
        passengers=('ticket_id', 'count')
    ).reset_index()
    daily['date'] = daily['date'].astype(str)
    return daily


def payment_method_breakdown(tickets):
    return tickets.groupby(['route_type', 'payment_method']).size().reset_index(name='count')


def generate_summary_stats(gps, tickets, routes):
    gps['load_factor'] = (gps['passengers_onboard'] / gps['capacity']).clip(0, 1)
    return {
        "total_routes": routes['route_id'].nunique(),
        "total_trips": gps['trip_id'].nunique(),
        "total_passengers": len(tickets),
        "total_revenue": int(tickets['fare_amount'].sum()),
        "avg_load_factor": round(float(gps['load_factor'].mean()), 3),
        "avg_delay_min": round(float(gps['delay_minutes'].mean()), 2),
        "metro_share_pct": round(len(tickets[tickets['route_type'] == 'Metro']) / len(tickets) * 100, 1),
        "bus_share_pct": round(len(tickets[tickets['route_type'] == 'Bus']) / len(tickets) * 100, 1),
    }


if __name__ == "__main__":
    print("Loading data...")
    gps, tickets, routes = load_data()

    print("\n=== Peak Hours ===")
    peak = peak_hours_analysis(tickets)
    print(peak[peak['is_peak']].to_string(index=False))

    print("\n=== Route Efficiency ===")
    eff = route_efficiency(gps, tickets)
    print(eff[['route_id', 'route_name', 'avg_load_factor', 'efficiency_score', 'total_revenue']].to_string(index=False))

    print("\n=== Underutilized Routes ===")
    under = underutilized_routes(eff)
    print(under.to_string(index=False))

    print("\n=== Schedule Optimization Suggestions ===")
    suggestions = schedule_optimization_suggestions(gps, tickets)
    print(suggestions.head(10).to_string(index=False))

    print("\n=== Summary Stats ===")
    stats = generate_summary_stats(gps, tickets, routes)
    for k, v in stats.items():
        print(f"  {k}: {v}")
