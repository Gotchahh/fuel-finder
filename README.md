# ⛽ Fuel Finder — Smart Fuel Price Analyzer

A smart fuel price analyzer that finds the most convenient gas station near you, considering not just the price per liter but also the real cost of getting there. Data is sourced from the Italian Ministry of Economic Development (MISE) and OpenStreetMap.

## How It Works

```
Your position
        ↓
Download fuel prices (MISE) + stations (OpenStreetMap)
        ↓
Filter by range, fuel type, self/attended
        ↓
For each station calculate:
├── Distance from you (km)
├── Estimated travel time (min)
├── Full tank cost
├── Round-trip fuel cost (optional, based on your car)
└── Convenience score (price 40% + distance 60%)
        ↓
Display on interactive map + ranked list
```

## Key Feature: Real Cost Calculation

A cheaper station far away might actually cost you more when you factor in the fuel needed to get there:

```
Station A: 1.75 €/l — 5 km away
Station B: 1.65 €/l — 35 km away

Your car: 6.0 L/100km — Full tank: 40 liters

Real cost A: (40 × 1.75) + round-trip fuel = 71.17 €
Real cost B: (40 × 1.65) + round-trip fuel = 73.70 €

→ Station A is cheaper despite the higher price per liter!
```

## Features

- **Dual data source** — MISE (official prices) + OpenStreetMap (additional stations)
- **Interactive map** — color-coded pins (green = cheapest, red = most expensive, gray = no price)
- **Visual range** — circle on map showing your search radius
- **Route display** — click to show the path to any station
- **Smart ranking** — convenience score balancing price (40%) and distance (60%)
- **Multiple sort options** — by convenience, real cost, price per liter, or distance
- **Self-service / attended filter** — toggle between pricing modes
- **Car consumption lookup** — automatic via FuelEconomy.gov API or manual input
- **Travel time estimate** — estimated minutes to reach each station
- **Data caching** — results cached for 1 hour to avoid repeated downloads
- **Flexible positioning** — enter an address or input coordinates manually

## Tech Stack

- **Python** — main language
- **Streamlit** — web interface
- **Pandas** — data processing and filtering
- **Folium** — interactive map rendering
- **Geopy** — geocoding and distance calculation
- **MISE Open Data** — official daily fuel prices for all Italian stations
- **OpenStreetMap Overpass API** — additional station locations
- **FuelEconomy.gov API** — vehicle fuel consumption data

## Prerequisites

- Python 3.9+
- Internet connection (for data download)

## Installation

```bash
git clone https://github.com/Gotchahh/fuel-finder.git
cd fuel-finder
python3 -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

## Project Structure

```
fuel-finder/
├── app.py                    # Streamlit interface
├── data/
│   ├── downloader.py         # Downloads data from MISE and OpenStreetMap
│   └── processor.py          # Filters, calculates costs and convenience score
├── maps/
│   └── visualizer.py         # Generates interactive Folium map
├── models/
│   └── cars.py               # FuelEconomy.gov API for car consumption
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration
├── requirements.txt
├── .gitignore
└── README.md
```

## Data Sources

| Source | Data | Update Frequency |
|---|---|---|
| MISE | Fuel prices for all Italian stations | Daily at 8:00 AM |
| OpenStreetMap | Station locations without prices | Community-maintained |
| FuelEconomy.gov | Vehicle fuel consumption (US market) | Yearly |

## Configuration

The convenience score balances two factors:

| Factor | Weight | Reasoning |
|---|---|---|
| Price | 40% | Important but not the only factor |
| Distance | 60% | Driving far for a small saving is not worth it |

Travel time is estimated at an average speed of 40 km/h (urban driving).

## Possible Improvements

- Real route distance via OSRM instead of geodesic distance
- Price history tracking with daily data storage and trend charts
- Price drop notifications when a station goes below a threshold
- Multi-fuel comparison (gasoline vs diesel vs LPG) at the same station
- European car consumption database to replace the US-only FuelEconomy.gov API
- Export results to CSV or PDF
- Docker containerization for easy deployment

## Author

Built by Alberto D'Odorico as a learning project during the ITS AI Developing program.
