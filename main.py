# 1. Uvoz potrebnih biblioteka

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from fiona.crs import from_epsg
from shapely.geometry import Point

# 2. Učitavanje geoprostornih podataka

opstina = gpd.read_file(r'C:\Users\Sanja\Desktop\GIS programiranje\Opstine.shp')
mreza_puteva = gpd.read_file(r'C:\Users\Sanja\Desktop\GIS programiranje\Mreža puteva.shp')
biciklisticke_staze = gpd.read_file(r'C:\Users\Sanja\Desktop\GIS programiranje\Biciklisticke staze.shp')

# 3. Definisanje koordinatnog sistema

opstina.crs = from_epsg(32634)
mreza_puteva.crs = from_epsg(32634)
biciklisticke_staze.crs = from_epsg(32634)

# 4. Vizuelizacija učitanih podataka

opstina.plot(color='lightgray', edgecolor='black')
plt.title("Opštine Novi Beograd i Stari Grad")
plt.show()
biciklisticke_staze.plot(color='blue')
plt.title("Biciklističke staze na teritoriji opština Novi Beograd i Stari Grad")
plt.show()
mreza_puteva.plot(color='black', linewidth=0.5)
plt.title("Mreža puteva na teritoriji opština Novi Beograd i Stari Grad")
plt.show()

# 5. Računanje gustine biciklističkih staza

ukupna_duzina = biciklisticke_staze.length.sum() / 1000  # pretvaranje u km
ukupna_povrsina = opstina.geometry.area.sum() / 1000000  # pretvaranje u km2
odnos = (ukupna_duzina/ukupna_povrsina)

print("Ukupna dužina biciklističkih staza: ", ukupna_duzina, "km")
print("Ukupna površina opštine: ", ukupna_povrsina, "km²")
print("Odnos dužine biciklističkih staza i ukupne površine: ", odnos, "km/km²")

# 6. Definisanje koordinata i prikaz lokacija za iznajmljivanje

tacka1 = Point(7455440.1, 4962999.7)
tacka2 = Point(7457537.7, 4963570.0)
tacka3 = Point(7457308.8, 4965146.1)

tacke = {'ID': [1, 2, 3], 'geometry': [tacka1, tacka2, tacka3]}
lokacije_za_iznajmljivanje = gpd.GeoDataFrame(tacke, crs='EPSG:32634')

fig, ax = plt.subplots()
opstina.plot(ax=ax, color='lightgray', edgecolor='black')
lokacije_za_iznajmljivanje.plot(ax=ax, color='yellow', markersize=50)
plt.title("Lokacije za iznajmljivanje bicikala")
plt.show()

# 7. Definisanje brzine bicikla i vremenskih intervala za izračunavanje vremenskog obuhvata lokacija

brzina_bicikla = 15  # km/h
vremenski_intervali = [10, 20, 30]  # vremenski intervali u minutima

columns = ['tacke_ID', 'interval', 'geometry']
obuhvati_gdf = gpd.GeoDataFrame(columns=columns, crs='EPSG:32634')

# 8. Izračunavanje vremenskog obuhvata za odabrane lokacije

for point_ID, lokacija in enumerate(lokacije_za_iznajmljivanje.itertuples(), 1):
    for vremenski_interval in vremenski_intervali:
        poligoni_obuhvata = []
        centar = lokacija.geometry
        brzina_ms = (brzina_bicikla * 1000) / 3600  # Pretvaranje brzine iz km/h u m/s
        poluprecnik = (brzina_ms * 60 * vremenski_interval)  # Pretvaranje vremenskog intervala iz minuta u sekunde
        poligon_obuhvata = centar.buffer(poluprecnik)
        poligoni_obuhvata.append(poligon_obuhvata)
        gdf_interval = gpd.GeoDataFrame({'tacke_ID': point_ID, 'interval': vremenski_interval, 'geometry': poligoni_obuhvata}, crs='EPSG:32634')
        obuhvati_gdf = pd.concat([obuhvati_gdf, gdf_interval], ignore_index=True)

# 9. Vizuelizacija poligona

for point_id in range(1, len(lokacije_za_iznajmljivanje) + 1):
    fig, ax = plt.subplots(figsize=(10, 5))
    for vremenski_interval in vremenski_intervali:
        poligoni_obuhvata = obuhvati_gdf[(obuhvati_gdf['tacke_ID'] == point_id) & (obuhvati_gdf['interval'] == vremenski_interval)]

        if vremenski_interval == 10:
            color = 'indigo'
        elif vremenski_interval == 20:
            color = 'red'
        elif vremenski_interval == 30:
            color = 'darkred'

        poligoni_obuhvata = gpd.overlay(poligoni_obuhvata, opstina, how='intersection')
        poligoni_obuhvata.plot(ax=ax, color=color, alpha=0.3, label=f'{vremenski_interval} min')

    opstina.plot(ax=ax, color='lightgray', edgecolor='black', alpha=0.5)
    mreza_puteva.plot(ax=ax, color='black', linewidth=0.5, alpha=0.4)
    lokacije_za_iznajmljivanje.iloc[point_id - 1:point_id].plot(ax=ax, color='yellow', markersize=50, alpha=0.7, zorder=4)

    opstina_bounds = opstina.total_bounds
    mreza_puteva_bounds = mreza_puteva.total_bounds
    poligoni_obuhvata_bounds = obuhvati_gdf.total_bounds

    prostor = 0.1

    x_min = opstina_bounds[0] - (opstina_bounds[2] - opstina_bounds[0]) * prostor
    x_max = opstina_bounds[2] + (opstina_bounds[2] - opstina_bounds[0]) * prostor
    y_min = opstina_bounds[1] - (opstina_bounds[3] - opstina_bounds[1]) * prostor
    y_max = opstina_bounds[3] + (opstina_bounds[3] - opstina_bounds[1]) * prostor

    ax.set_xlim([x_min, x_max])
    ax.set_ylim([y_min, y_max])

plt.show()