import pandas as pd
from geopy.distance import geodesic

def filtra_per_range(df, lat_utente, lon_utente, range_km=25):
    df = df.copy()
    df["Latitudine"] = pd.to_numeric(df["Latitudine"], errors="coerce")
    df["Longitudine"] = pd.to_numeric(df["Longitudine"], errors="coerce")
    df = df.dropna(subset=["Latitudine", "Longitudine"])

    def calcola_distanza(row):
        try:
            return geodesic(
                (lat_utente, lon_utente),
                (row["Latitudine"], row["Longitudine"])
            ).km
        except:
            return None

    df["distanza_km"] = df.apply(calcola_distanza, axis=1)
    df = df.dropna(subset=["distanza_km"])
    df = df[df["distanza_km"] <= range_km]

    return df

def filtra_per_carburante(df, tipo_carburante="Benzina"):
    df = df.copy()
    df["descCarburante"] = df["descCarburante"].astype(str).str.strip()
    filtered = df[df["descCarburante"].str.contains(tipo_carburante, case=False, na=False)]
    return filtered

def calcola_costo_reale(df, consumo_l_per_100km=None, litri_pieno=40):
    df = df.copy()
    df["prezzo"] = pd.to_numeric(df["prezzo"], errors="coerce")
    df = df.dropna(subset=["prezzo"])

    df["costo_pieno"] = df["prezzo"] * litri_pieno

    if consumo_l_per_100km:
        df["litri_tragitto"] = (df["distanza_km"] * 2) / 100 * consumo_l_per_100km
        df["costo_tragitto"] = df["litri_tragitto"] * df["prezzo"]
        df["costo_reale"] = df["costo_pieno"] + df["costo_tragitto"]
    else:
        df["litri_tragitto"] = None
        df["costo_tragitto"] = None
        df["costo_reale"] = df["costo_pieno"]

    df["tempo_stimato_min"] = (df["distanza_km"] / 40 * 60).round(1)

    prezzo_norm = (df["prezzo"] - df["prezzo"].min()) / (df["prezzo"].max() - df["prezzo"].min() + 0.001)
    distanza_norm = (df["distanza_km"] - df["distanza_km"].min()) / (df["distanza_km"].max() - df["distanza_km"].min() + 0.001)

    df["score_convenienza"] = ((prezzo_norm * 0.4) + (distanza_norm * 0.6)).round(3)

    df = df.sort_values("score_convenienza")
    return df

def get_top_distributori(df, top_n=10):
    columns = [
        "Gestore", "Indirizzo", "Comune", "Provincia",
        "descCarburante", "prezzo", "distanza_km",
        "costo_pieno", "costo_tragitto", "costo_reale",
        "tempo_stimato_min", "score_convenienza",
        "Latitudine", "Longitudine"
    ]
    available = [c for c in columns if c in df.columns]
    return df[available].head(top_n)