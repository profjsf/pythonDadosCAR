import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import os

def main():
    st.set_page_config(layout="wide")
    st.title("🌱 Visualizador Interativo do CAR")

    BASE_DIR = "por_municipio"

    # Lista os municípios disponíveis
    municipios_disponiveis = sorted([
        nome for nome in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, nome))
    ])

    # Estado inicial
    if "municipio" not in st.session_state:
        st.session_state.municipio = municipios_disponiveis[0]
    if "tipos" not in st.session_state:
        st.session_state.tipos = []
    if "pesquisar" not in st.session_state:
        st.session_state.pesquisar = False

    # Sidebar
    st.sidebar.header("🔍 Filtros")
    st.session_state.municipio = st.sidebar.selectbox(
        "🏘️ Município",
        municipios_disponiveis,
        index=municipios_disponiveis.index(st.session_state.municipio)
    )

    @st.cache_data(show_spinner="Carregando dados...")
    def carregar_gdf(municipio):
        pasta = os.path.join(BASE_DIR, municipio)
        shp_file = next((f for f in os.listdir(pasta) if f.endswith(".shp")), None)
        if not shp_file:
            return None
        gdf = gpd.read_file(os.path.join(pasta, shp_file))
        if "area_ha" not in gdf.columns:
            gdf_metric = gdf.to_crs(epsg=3857)
            gdf["area_ha"] = gdf_metric.geometry.area / 10000
            gdf = gdf.to_crs(epsg=4326)
        gdf["ind_tipo"] = gdf["ind_tipo"].astype(str).str.strip()
        return gdf

    gdf = carregar_gdf(st.session_state.municipio)

    if gdf is not None:
        tipos_disponiveis = sorted(gdf["ind_tipo"].dropna().unique())
        st.session_state.tipos = st.sidebar.multiselect("🏷️ Tipo de imóvel", tipos_disponiveis, default=tipos_disponiveis)

        if st.sidebar.button("🔎 Pesquisar"):
            st.session_state.pesquisar = True
    else:
        st.warning("Nenhum shapefile encontrado para esse município.")
        st.stop()

    if st.session_state.pesquisar:
        gdf_filtrado = gdf[gdf["ind_tipo"].isin(st.session_state.tipos)]

        st.sidebar.markdown(f"🧾 {len(gdf_filtrado)} imóveis encontrados")

        if not gdf_filtrado.empty:
            centro = gdf_filtrado.geometry.centroid.iloc[0]
            mapa = folium.Map(location=[centro.y, centro.x], zoom_start=11)

            for _, row in gdf_filtrado.iterrows():
                centro_geom = row.geometry.centroid
                lat, lon = centro_geom.y, centro_geom.x
                google_maps_link = f"https://www.google.com/maps?q={lat},{lon}"

                popup_info = ""
                for col in gdf_filtrado.columns:
                    if col != "geometry":
                        popup_info += f"<b>{col}:</b> {row[col]}<br>"
                popup_info += f"<b>Coordenadas:</b> {lat:.6f}, {lon:.6f}<br>"
                popup_info += f"<a href='{google_maps_link}' target='_blank'>🔗 Ver no Google Maps</a>"

                folium.GeoJson(
                    row["geometry"],
                    tooltip=f"{row['ind_tipo']} - {row['area_ha']:.2f} ha",
                    popup=folium.Popup(popup_info, max_width=450)
                ).add_to(mapa)

            st_folium(mapa, width=1200, height=600)
        else:
            st.warning("Nenhum imóvel encontrado com o filtro selecionado.")
    else:
        st.info("Selecione um município e clique em **Pesquisar** para visualizar os imóveis.")
