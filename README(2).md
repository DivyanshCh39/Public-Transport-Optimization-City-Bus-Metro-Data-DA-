# 🚌 TransitIQ — Public Transport Optimization Analytics

> Analyze GPS + ticketing data to find peak hours, underutilized routes, and optimize schedules.

---

## 📁 Project Structure

```
transit_analytics/
├── dashboard.html           ← Interactive analytics dashboard (open in browser)
├── generate_dataset.py      ← Dummy dataset generator (runs standalone)
├── src/
│   └── analytics.py         ← Core analytics engine (Python)
├── data/
│   ├── gps_data.csv         ← 748,350 GPS stop records (90 days)
│   ├── ticketing_data.csv   ← 518,050 passenger journey records
│   ├── route_metadata.csv   ← 170 stop/route records with GPS coords
│   └── dashboard_data.json  ← Pre-computed dashboard aggregations
└── README.md
```

---

## 🗄️ Datasets

### 1. `gps_data.csv` — 748K records
| Column | Description |
|--------|-------------|
| timestamp | Datetime of GPS ping at each stop |
| trip_id | Unique trip identifier |
| vehicle_id | Bus/train vehicle ID |
| route_id | Route identifier (R01–R10) |
| route_name | Human-readable route name |
| route_type | Bus or Metro |
| stop_sequence | Stop number in route |
| stop_name | Name of the stop |
| latitude / longitude | GPS coordinates |
| speed_kmh | Vehicle speed |
| passengers_onboard | Count of passengers at stop |
| capacity | Vehicle max capacity |
| delay_minutes | Delay at this stop |
| day_of_week, date, hour | Time dimensions |

### 2. `ticketing_data.csv` — 518K records
| Column | Description |
|--------|-------------|
| ticket_id | Unique ticket ID |
| date, hour, day_of_week | Journey time |
| route_id / route_name / route_type | Route info |
| boarding_stop / alighting_stop | Journey endpoints |
| stops_travelled | Distance proxy |
| passenger_type | Adult/Student/Senior/Child/Employee Pass |
| payment_method | Smart Card/Cash/Mobile App/QR Code |
| fare_amount | Fare paid (₹) |
| journey_duration_min | Trip duration |

### 3. `route_metadata.csv` — 170 records
| Column | Description |
|--------|-------------|
| route_id | Route ID |
| route_name | Route name |
| route_type | Bus or Metro |
| stop_sequence | Stop order |
| stop_name | Stop name |
| latitude / longitude | Stop GPS location |
| total_stops | Stops in route |
| route_distance_km | Total route length |
| vehicle_capacity | Seats per vehicle |

---

## 🚌 Routes Modeled

| ID | Name | Type | Stops | Capacity |
|----|------|------|-------|----------|
| R01 | Central – Airport Express | Bus | 12 | 60 |
| R02 | City Loop (North) | Bus | 18 | 60 |
| R03 | City Loop (South) | Bus | 16 | 60 |
| R04 | Metro Line 1 (Red) | Metro | 24 | 300 |
| R05 | Metro Line 2 (Blue) | Metro | 20 | 300 |
| R06 | University Shuttle | Bus | 8 | 45 |
| R07 | Industrial Zone Link | Bus | 10 | 60 |
| R08 | Suburban Express East | Bus | 14 | 60 |
| R09 | Metro Line 3 (Green) | Metro | 28 | 300 |
| R10 | Night Owl Service | Bus | 20 | 45 |

---

## 📊 Key Findings (from the data)

### Peak Hours
- **Morning Peak**: 08:00 (42,194 journeys) — highest of the day
- **Midday Surge**: 13:00 (41,772 journeys)
- **Evening Peak**: 20:00–21:00 (37K+ journeys)
- Off-peak hours (05:00, 23:00) see 80% lower volumes

### Route Efficiency
- **Metro routes** (R04/R05/R09) lead with efficiency scores 74.7–74.9
- **R07 Industrial Zone Link** is the most underutilized: 23.9% avg load factor
- All metro routes show 39–40% average load factor vs bus average of ~32%

### Revenue
- Total 90-day revenue: **₹15.57 million**
- Metro generates **57.3%** of revenue on just 3 routes
- R09 Metro Line 3 is highest earner: ₹3.63M

### Optimization Opportunities
1. **Increase** frequency on R06/R09 during morning peak (HIGH)
2. **Reduce** R07 midday services (save ₹8K/month fuel)
3. **Merge** R02+R03 evening loops (save ₹15K/month)
4. **Replace** R10 Night Owl 2–4 AM with demand-responsive minibus

---

## 🚀 How to Use

### Generate fresh dataset
```bash
python3 generate_dataset.py
```

### Run analytics in Python
```bash
python3 src/analytics.py
```

### View Dashboard
Open `dashboard.html` in any modern browser. No server required.
The dashboard has 5 tabs:
- **Overview** — KPIs, daily trends, peak hours, payment breakdown
- **Route Efficiency** — Efficiency scores, load factors, revenue comparison
- **Passenger Trends** — Load curves by time, passenger types, weekday vs weekend
- **Schedule Optimization** — AI-driven recommendations with estimated savings
- **GPS Heatmap** — Network map with animated route visualization

---

## 🛠️ Tech Stack
- **Data Generation**: Python (pandas, numpy)
- **Analytics Engine**: Python (analytics.py)
- **Dashboard**: HTML5 + Chart.js 4 (no framework, single file)
- **Data Format**: CSV (raw), JSON (pre-aggregated for dashboard)

---

*Dataset spans 90 days (Jan–Mar 2024), simulating a mid-sized metro city.*
