import requests
import folium

# URL de votre backend OSRM
OSRM_URL = "http://localhost:5000"

# Liste des points en France en format (latitude, longitude)
points = [
    (48.8566, 2.3522),    # Paris
    (50.6292, 3.0573),    # Lille
    (49.2583, 4.0317),    # Reims
    (45.764, 4.8357),     # Lyon
    (43.6045, 1.444),     # Toulouse
    (43.7102, 7.262),     # Nice
]

# Fonction pour récupérer l'itinéraire multi-points depuis OSRM
def get_route(osrm_url, points):
    # Formatage des coordonnées pour OSRM
    coordinates = ";".join([f"{point[1]},{point[0]}" for point in points])
    url = f"{osrm_url}/route/v1/driving/{coordinates}"
    params = {
        "overview": "full",
        "geometries": "geojson"
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["routes"][0]["geometry"]["coordinates"]
    else:
        print(f"Erreur: {response.status_code}")
        return None

# Récupérer l'itinéraire
route = get_route(OSRM_URL, points)

# Créer une carte avec folium et tracer l'itinéraire
if route:
    # Centrer la carte sur la France
    map_ = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
    
    # Convertir le format des coordonnées de (lon, lat) à (lat, lon)
    route_lat_lon = [(coord[1], coord[0]) for coord in route]
    
    # Ajouter l'itinéraire à la carte
    folium.PolyLine(route_lat_lon, color="blue", weight=5, opacity=0.7).add_to(map_)
    
    # Ajouter des marqueurs pour chaque point
    for i, point in enumerate(points):
        folium.Marker(location=point, tooltip=f"Point {i + 1}").add_to(map_)
    
    # Sauvegarder la carte dans un fichier HTML
    map_.save("multi_point_route_map.html")
    print("La carte a été sauvegardée sous le nom 'multi_point_route_map.html'")
else:
    print("Impossible de récupérer l'itinéraire.")
