import streamlit as st
import geopandas as gpd
import folium
from shapely.geometry import Point
from streamlit_folium import st_folium
import os

st.set_page_config(layout="wide")
st.title("📍 Localizar Propriedade por Coordenadas")

BASE_DIR = "por_municipio"

# Inicializa estado
if "lat" not in st.session_state:
    st.session_state.lat = ""
if "lon" not in st.session_state:
    st.session_state.lon = ""
if "resultados" not in st.session_state:
    st.session_state.resultados = None
if "municipio_encontrado" not in st.session_state:
    st.session_state.municipio_encontrado = None

# Entradas do usuário
lat_str = st.text_input("Latitude (ex: -10.123456)", value=st.session_state.lat)
lon_str = st.text_input("Longitude (ex: -50.654321)", value=st.session_state.lon)

# Botão de pesquisa
if st.button("🔎 Buscar Propriedade"):
    try:
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
        ponto = Point(lon, lat)

        # Busca em todos os municípios
        for municipio in os.listdir(BASE_DIR):
            pasta = os.path.join(BASE_DIR, municipio)
            if not os.path.isdir(pasta):
                continue
            shp_file = next((f for f in os.listdir(pasta) if f.endswith(".shp")), None)
            if not shp_file:
                continue
            gdf = gpd.read_file(os.path.join(pasta, shp_file)).to_crs(epsg=4326)
            resultados = gdf[gdf.geometry.contains(ponto)]
            if not resultados.empty:
                st.session_state.lat = lat_str
                st.session_state.lon = lon_str
                st.session_state.resultados = resultados
                st.session_state.municipio_encontrado = municipio
                break
        else:
            st.session_state.resultados = None
            st.session_state.municipio_encontrado = None

    except ValueError:
        st.error("⚠️ Latitude e longitude inválidas. Insira números válidos.")

# Exibe resultado se houver
if st.session_state.resultados is not None:
    centro_lat = float(st.session_state.lat)
    centro_lon = float(st.session_state.lon)
    mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=13)
    folium.Marker([centro_lat, centro_lon], tooltip="📍 Local pesquisado").add_to(mapa)

    st.success(f"✅ Propriedade encontrada em **{st.session_state.municipio_encontrado.title()}**")

    for _, row in st.session_state.resultados.iterrows():
        centro_geom = row.geometry.centroid
        popup_info = ""
        for col in st.session_state.resultados.columns:
            if col != "geometry":
                popup_info += f"<b>{col}:</b> {row[col]}<br>"
        google_link = f"https://www.google.com/maps?q={centro_lat},{centro_lon}"
        popup_info += f"<br><a href='{google_link}' target='_blank'>🌐 Ver no Google Maps</a>"

        folium.GeoJson(
            row["geometry"],
            tooltip="Propriedade CAR",
            popup=folium.Popup(popup_info, max_width=450)
        ).add_to(mapa)

    st_folium(mapa, width=1200, height=600)
elif st.session_state.lat and st.session_state.lon:
    st.warning("❌ Nenhuma propriedade encontrada neste ponto.")
else:
    st.info("Informe latitude e longitude, depois clique em **Buscar Propriedade**.")
