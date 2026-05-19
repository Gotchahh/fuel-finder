import folium
import pandas as pd

def crea_mappa(df, lat_utente, lon_utente, range_km=25, distributore_selezionato=None):
    mappa = folium.Map(
        location=[lat_utente, lon_utente],
        zoom_start=12
    )

    folium.Marker(
        location=[lat_utente, lon_utente],
        popup="La tua posizione",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(mappa)

    folium.Circle(
        location=[lat_utente, lon_utente],
        radius=range_km * 1000,
        color="#e94560",
        weight=2,
        fill=True,
        fill_opacity=0.05,
        popup=f"Range: {range_km} km"
    ).add_to(mappa)

    if df.empty:
        return mappa

    df_con_prezzo = df[df["prezzo"].notna()]
    if not df_con_prezzo.empty:
        prezzo_min = df_con_prezzo["prezzo"].min()
        prezzo_max = df_con_prezzo["prezzo"].max()
    else:
        prezzo_min = 0
        prezzo_max = 0

    for _, row in df.iterrows():
        prezzo = row.get("prezzo", 0)
        distanza = row.get("distanza_km", 0)
        gestore = row.get("Gestore", "Sconosciuto")
        indirizzo = row.get("Indirizzo", "")
        comune = row.get("Comune", "")
        carburante = row.get("descCarburante", "")
        costo_pieno = row.get("costo_pieno", None)
        costo_tragitto = row.get("costo_tragitto", None)
        costo_reale = row.get("costo_reale", None)

        if pd.isna(prezzo):
            colore = "gray"
        elif prezzo == prezzo_min:
            colore = "green"
        elif prezzo == prezzo_max:
            colore = "red"
        else:
            colore = "orange"

        popup_html = f"""
        <div style="width:200px">
            <b>{gestore}</b><br>
            {indirizzo}, {comune}<br>
            <hr style="margin:5px 0">
        """

        if pd.notna(prezzo):
            popup_html += f"<b>{carburante}</b>: {prezzo:.3f} €/l<br>"
        else:
            popup_html += "<i>Prezzo non disponibile</i><br>"

        popup_html += f"Distanza: {distanza:.1f} km<br>"

        if costo_pieno is not None and pd.notna(costo_pieno):
            popup_html += f"Costo pieno: {costo_pieno:.2f} €<br>"

        if costo_tragitto is not None and pd.notna(costo_tragitto):
            popup_html += f"Costo tragitto A/R: {costo_tragitto:.2f} €<br>"

        if costo_reale is not None and pd.notna(costo_reale):
            popup_html += f"<b>Costo reale: {costo_reale:.2f} €</b><br>"

        popup_html += "</div>"

        folium.Marker(
            location=[row["Latitudine"], row["Longitudine"]],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=colore, icon="gas-pump", prefix="fa")
        ).add_to(mappa)

    if distributore_selezionato is not None:
        dest_lat = distributore_selezionato["Latitudine"]
        dest_lon = distributore_selezionato["Longitudine"]

        folium.PolyLine(
            locations=[
                [lat_utente, lon_utente],
                [dest_lat, dest_lon]
            ],
            color="#e94560",
            weight=3,
            opacity=0.8,
            dash_array="10"
        ).add_to(mappa)

    return mappa