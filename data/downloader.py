import requests
import pandas as pd
import os
import streamlit as st

DATA_DIR = "data/cache"

ANAGRAFICA_URL = "https://www.mimit.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"
PREZZI_URL = "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"

def setup_cache():
    os.makedirs(DATA_DIR, exist_ok=True)

@st.cache_data(ttl=3600)
def download_anagrafica():
    setup_cache()
    filepath = os.path.join(DATA_DIR, "anagrafica.csv")

    response = requests.get(ANAGRAFICA_URL, timeout=30)
    response.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(response.content)

    df = pd.read_csv(filepath, sep="|", encoding="utf-8", skiprows=1, on_bad_lines="skip")
    return df

@st.cache_data(ttl=3600)
def download_prezzi():
    setup_cache()
    filepath = os.path.join(DATA_DIR, "prezzi.csv")

    response = requests.get(PREZZI_URL, timeout=30)
    response.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(response.content)

    df = pd.read_csv(filepath, sep="|", encoding="utf-8", skiprows=1, on_bad_lines="skip")
    return df

@st.cache_data(ttl=3600)
def download_osm_distributori(lat, lon, range_km=25):
    overpass_url = "https://overpass-api.de/api/interpreter"

    delta = range_km / 111
    south = lat - delta
    north = lat + delta
    west = lon - delta
    east = lon + delta

    query = f"""[out:json][timeout:30];
(node["amenity"="fuel"]({south},{west},{north},{east}););
out body;"""

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "FuelFinder/1.0"
    }

    response = requests.post(
        overpass_url,
        data=f"data={query}",
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()

    distributori = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        distributori.append({
            "idImpianto": f"osm_{element['id']}",
            "Gestore": tags.get("brand", tags.get("operator", tags.get("name", "Sconosciuto"))),
            "Indirizzo": tags.get("addr:street", ""),
            "Comune": tags.get("addr:city", ""),
            "Provincia": tags.get("addr:province", ""),
            "Latitudine": element.get("lat"),
            "Longitudine": element.get("lon"),
            "fonte": "OpenStreetMap"
        })

    return pd.DataFrame(distributori)

def get_distributori_con_prezzi(lat=None, lon=None, range_km=25):
    anagrafica = download_anagrafica()
    prezzi = download_prezzi()

    merged = pd.merge(
        anagrafica,
        prezzi,
        left_on="idImpianto",
        right_on="idImpianto",
        how="inner"
    )
    merged["fonte"] = "MISE"

    if lat and lon:
        osm = download_osm_distributori(lat, lon, range_km)

        if not osm.empty:
            osm["descCarburante"] = "N/D"
            osm["prezzo"] = None
            osm["isSelf"] = None
            osm["dtComu"] = None

            combined = pd.concat([merged, osm], ignore_index=True)
            combined = combined.drop_duplicates(
                subset=["Latitudine", "Longitudine"],
                keep="first"
            )
            return combined

    return merged