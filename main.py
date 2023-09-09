import os
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
from fiona.crs import from_epsg
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox

shapefile_path = r'C:\Users\Sanja\Desktop\GIS programiranje\Opstina Novi Beograd.shp'
opstina = gpd.read_file(shapefile_path)
print(opstina)
type(opstina)

opstina.crs
print(opstina.crs)
opstina.crs=from_epsg(6316)
opstina.crs
print(opstina.crs)

opstina.plot(color='lightblue', edgecolor='black')
plt.title("Opština Novi Beograd")
plt.show()

place_name="Opstina Novi Beograd, Srbija"
graph=ox.graph_from_place(place_name, network_type="bike")

