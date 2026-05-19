import requests

FUELECONOMY_BASE = "https://www.fueleconomy.gov/ws/rest"

def get_years():
    url = f"{FUELECONOMY_BASE}/vehicle/menu/year"
    response = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
    response.raise_for_status()
    data = response.json()
    return [item["value"] for item in data["menuItem"]]

def get_makes(year):
    url = f"{FUELECONOMY_BASE}/vehicle/menu/make?year={year}"
    response = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
    response.raise_for_status()
    data = response.json()
    items = data.get("menuItem", [])
    if isinstance(items, dict):
        items = [items]
    return [item["value"] for item in items]

def get_models(year, make):
    url = f"{FUELECONOMY_BASE}/vehicle/menu/model?year={year}&make={make}"
    response = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
    response.raise_for_status()
    data = response.json()
    items = data.get("menuItem", [])
    if isinstance(items, dict):
        items = [items]
    return [item["value"] for item in items]

def get_options(year, make, model):
    url = f"{FUELECONOMY_BASE}/vehicle/menu/options?year={year}&make={make}&model={model}"
    response = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
    response.raise_for_status()
    data = response.json()
    items = data.get("menuItem", [])
    if isinstance(items, dict):
        items = [items]
    return [{"text": item["text"], "value": item["value"]} for item in items]

def get_vehicle_data(vehicle_id):
    url = f"{FUELECONOMY_BASE}/vehicle/{vehicle_id}"
    response = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
    response.raise_for_status()
    data = response.json()

    comb_mpg = data.get("comb08", 0)
    if comb_mpg and comb_mpg > 0:
        l_per_100km = round(235.215 / comb_mpg, 1)
    else:
        l_per_100km = None

    return {
        "year": data.get("year", ""),
        "make": data.get("make", ""),
        "model": data.get("model", ""),
        "fuel_type": data.get("fuelType", ""),
        "cylinders": data.get("cylinders", ""),
        "displacement": data.get("displ", ""),
        "transmission": data.get("trany", ""),
        "mpg_city": data.get("city08", 0),
        "mpg_highway": data.get("highway08", 0),
        "mpg_combined": comb_mpg,
        "l_per_100km": l_per_100km
    }