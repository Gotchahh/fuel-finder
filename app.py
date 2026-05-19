import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from data.downloader import get_distributori_con_prezzi
from data.processor import filtra_per_range, filtra_per_carburante, calcola_costo_reale, get_top_distributori
from maps.visualizer import crea_mappa
from models.cars import get_years, get_makes, get_models, get_options, get_vehicle_data

st.set_page_config(
    page_title="Fuel Finder",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Outfit', sans-serif;
    }

    .main-header {
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(233, 69, 96, 0.3);
    }

    .main-header h1 {
        color: #e94560;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.3rem;
    }

    .stat-card {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(233, 69, 96, 0.2);
        margin-bottom: 0.8rem;
        text-align: center;
    }

    .stat-card h3 {
        color: #e94560;
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
    }

    .stat-card p {
        font-size: 1.4rem;
        font-weight: 600;
        margin: 0;
    }

    .winner-card {
        padding: 1.2rem;
        border-radius: 12px;
        border: 2px solid #10b981;
        margin-bottom: 1rem;
    }

    .winner-card h3 {
        color: #10b981;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .result-card {
        padding: 0.8rem;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 0.5rem;
    }

    .price-tag {
        color: #e94560;
        font-weight: 700;
        font-size: 1.1rem;
    }

    .distance-tag {
        font-size: 0.9rem;
        opacity: 0.7;
    }

    .legend {
        padding: 0.8rem;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-top: 0.5rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>⛽ Fuel Finder</h1>
    <p>Trova il distributore più conveniente vicino a te — dati aggiornati dal MISE e OpenStreetMap</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 📍 Posizione")
usa_gps = st.sidebar.checkbox("Usa la mia posizione attuale")

if usa_gps:
    st.sidebar.info("Inserisci le tue coordinate manualmente (il GPS del browser non è supportato da Streamlit)")
    lat = st.sidebar.number_input("Latitudine", value=45.9563, format="%.4f")
    lon = st.sidebar.number_input("Longitudine", value=12.6597, format="%.4f")
    st.sidebar.success(f"📌 {lat:.4f}, {lon:.4f}")
else:
    indirizzo = st.sidebar.text_input("Indirizzo o città", value="Pordenone")
    if indirizzo:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="fuel-finder")
        location = geolocator.geocode(indirizzo)
        if location:
            lat = location.latitude
            lon = location.longitude
            st.sidebar.success(f"📌 {lat:.4f}, {lon:.4f}")
        else:
            st.sidebar.error("Indirizzo non trovato")
            st.stop()
    else:
        st.stop()

st.sidebar.markdown("## ⚙️ Impostazioni")
range_km = st.sidebar.slider("Range di ricerca (km)", 5, 50, 25)
tipo_carburante = st.sidebar.selectbox("Tipo carburante", ["Benzina", "Gasolio", "GPL", "Metano"])
modalita_prezzo = st.sidebar.selectbox("Modalità prezzo", ["Tutti", "Self-service", "Servito"])
litri_pieno = st.sidebar.number_input("Litri pieno", min_value=10, max_value=100, value=40)

st.sidebar.markdown("## 🚗 La tua auto")
usa_auto = st.sidebar.checkbox("Seleziona il modello di macchina")

consumo = None
if usa_auto:
    try:
        years = get_years()
        anno = st.sidebar.selectbox("Anno", years)

        if anno:
            makes = get_makes(anno)
            marca = st.sidebar.selectbox("Marca", makes)

            if marca:
                modelli = get_models(anno, marca)
                modello = st.sidebar.selectbox("Modello", modelli)

                if modello:
                    options = get_options(anno, marca, modello)
                    if options:
                        versione = st.sidebar.selectbox(
                            "Versione",
                            options,
                            format_func=lambda x: x["text"]
                        )
                        if versione:
                            vehicle = get_vehicle_data(versione["value"])
                            consumo = vehicle["l_per_100km"]
                            if consumo:
                                st.sidebar.success(f"⛽ Consumo: {consumo} L/100km")
                            else:
                                st.sidebar.warning("Consumo non disponibile")
    except Exception as e:
        st.sidebar.error(f"Errore API auto: {str(e)}")
        consumo_manuale = st.sidebar.number_input(
            "Inserisci consumo manuale (L/100km)",
            min_value=3.0, max_value=30.0, value=7.0
        )
        consumo = consumo_manuale

if not usa_auto:
    consumo_manuale = st.sidebar.number_input(
        "Consumo manuale (L/100km)",
        min_value=0.0, max_value=30.0, value=0.0
    )
    if consumo_manuale > 0:
        consumo = consumo_manuale

if st.sidebar.button("🔍 Cerca distributori", use_container_width=True):
    with st.spinner("Scarico dati dal MISE e OpenStreetMap..."):
        try:
            df = get_distributori_con_prezzi(lat, lon, range_km)
        except Exception as e:
            st.error(f"Errore scaricamento dati: {str(e)}")
            st.stop()

    with st.spinner("Filtro distributori..."):
        df = filtra_per_range(df, lat, lon, range_km)
        df = filtra_per_carburante(df, tipo_carburante)

        if modalita_prezzo == "Self-service" and "isSelf" in df.columns:
            df = df[df["isSelf"] == 1]
        elif modalita_prezzo == "Servito" and "isSelf" in df.columns:
            df = df[df["isSelf"] == 0]

        if df.empty:
            st.warning("Nessun distributore trovato nel range selezionato")
            st.stop()

        df = calcola_costo_reale(df, consumo, litri_pieno)

    st.session_state["risultati"] = df
    st.session_state["lat"] = lat
    st.session_state["lon"] = lon
    st.session_state["range_km"] = range_km
    st.session_state["selezionato"] = None

if "risultati" in st.session_state:
    df = st.session_state["risultati"]
    lat = st.session_state["lat"]
    lon = st.session_state["lon"]
    range_km_saved = st.session_state["range_km"]

    df_con_prezzo = df[df["prezzo"].notna()]
    total = len(df)
    con_prezzo = len(df_con_prezzo)

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"""
        <div class="stat-card">
            <h3>Distributori trovati</h3>
            <p>{total}</p>
        </div>""", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
        <div class="stat-card">
            <h3>Con prezzo</h3>
            <p>{con_prezzo}</p>
        </div>""", unsafe_allow_html=True)
    with col_s3:
        if not df_con_prezzo.empty:
            st.markdown(f"""
            <div class="stat-card">
                <h3>Prezzo più basso</h3>
                <p>{df_con_prezzo['prezzo'].min():.3f} €/l</p>
            </div>""", unsafe_allow_html=True)
    with col_s4:
        if not df_con_prezzo.empty:
            st.markdown(f"""
            <div class="stat-card">
                <h3>Prezzo più alto</h3>
                <p>{df_con_prezzo['prezzo'].max():.3f} €/l</p>
            </div>""", unsafe_allow_html=True)

    ordinamento = st.selectbox(
        "Ordina classifica per:",
        ["Più conveniente (prezzo + distanza)", "Costo reale (pieno + tragitto)", "Prezzo al litro", "Distanza più vicina"]
    )

    if ordinamento == "Prezzo al litro":
        df = df.sort_values("prezzo", na_position="last")
    elif ordinamento == "Distanza più vicina":
        df = df.sort_values("distanza_km")
    elif ordinamento == "Costo reale (pieno + tragitto)":
        df = df.sort_values("costo_reale", na_position="last")
    else:
        df = df.sort_values("score_convenienza", na_position="last")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🗺️ Mappa")
        top = get_top_distributori(df, 20)

        selezionato = st.session_state.get("selezionato", None)
        dist_sel = None
        if selezionato is not None and selezionato < len(top):
            dist_sel = top.iloc[selezionato]

        mappa = crea_mappa(top, lat, lon, range_km_saved, dist_sel)
        st_folium(mappa, width=700, height=500)

        st.markdown("""
        <div class="legend">
            <span style="margin-right:1rem">🟢 Più economico</span>
            <span style="margin-right:1rem">🟠 Intermedio</span>
            <span style="margin-right:1rem">🔴 Più caro</span>
            <span style="margin-right:1rem">⚪ Prezzo N/D</span>
            <span>🔴 ⭕ Range di ricerca</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🏆 Classifica")
        best = get_top_distributori(df, 10)

        for i, (_, row) in enumerate(best.iterrows()):
            prezzo = row.get('prezzo')
            distanza = row.get('distanza_km', 0)
            gestore = row.get('Gestore', 'N/A')
            indirizzo_dist = row.get('Indirizzo', '')
            comune = row.get('Comune', '')
            costo_reale = row.get('costo_reale')
            costo_pieno = row.get('costo_pieno')
            costo_tragitto = row.get('costo_tragitto')

            if i == 0 and prezzo and not pd.isna(prezzo):
                st.markdown(f"""
                <div class="winner-card">
                    <h3>🏆 {gestore}</h3>
                    <p>📍 {indirizzo_dist}, {comune}</p>
                    <p><span class="price-tag">{prezzo:.3f} €/l</span> — {distanza:.1f} km — ⏱️ {row.get('tempo_stimato_min', 0):.0f} min</p>
                """, unsafe_allow_html=True)

                if costo_reale and not pd.isna(costo_reale):
                    html = f"<p>💰 Pieno: {costo_pieno:.2f} €</p>"
                    if costo_tragitto and not pd.isna(costo_tragitto):
                        html += f"<p>🚗 Tragitto A/R: {costo_tragitto:.2f} €</p>"
                    html += f"<p><strong>💶 Costo reale: {costo_reale:.2f} €</strong></p>"
                    st.markdown(html, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-card">
                    <strong>{i+1}. {gestore}</strong><br>
                    <span class="distance-tag">📍 {indirizzo_dist}, {comune}</span><br>
                """, unsafe_allow_html=True)

                if prezzo and not pd.isna(prezzo):
                    html = f'<span class="price-tag">{prezzo:.3f} €/l</span> — {distanza:.1f} km — ⏱️ {row.get("tempo_stimato_min", 0):.0f} min'
                else:
                    html = f'Prezzo N/D — {distanza:.1f} km'

                if costo_reale and not pd.isna(costo_reale):
                    html += f"<br>💶 <strong>{costo_reale:.2f} €</strong>"

                st.markdown(html + "</div>", unsafe_allow_html=True)

            if st.button(f"📍 Mostra percorso", key=f"route_{i}"):
                st.session_state["selezionato"] = i
                st.rerun()