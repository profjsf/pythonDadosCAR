import geopandas as gpd
import os

# Caminho do shapefile original
shp_path = "AREA_IMOVEL/AREA_IMOVEL_1.shp"

# Pasta de saída
output_dir = "por_municipio"
os.makedirs(output_dir, exist_ok=True)

# Carrega o shapefile
gdf = gpd.read_file(shp_path)

# Garante consistência no nome dos municípios
gdf["municipio"] = gdf["municipio"].astype(str).str.strip()

# Divide por município e salva individualmente
for municipio, grupo in gdf.groupby("municipio"):
    nome_limpo = municipio.replace(" ", "_").replace("/", "_")
    pasta_mun = os.path.join(output_dir, nome_limpo)
    os.makedirs(pasta_mun, exist_ok=True)

    caminho_saida = os.path.join(pasta_mun, f"{nome_limpo}.shp")
    grupo.to_file(caminho_saida)

print("✅ Shapefiles salvos por município na pasta 'por_municipio'")
