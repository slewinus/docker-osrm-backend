from flask import Flask, render_template, request, redirect, url_for
import os
import requests
import folium
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration pour les téléchargements de fichiers
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Créez le dossier de téléchargement si nécessaire
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# URL de votre backend OSRM
OSRM_URL = "http://localhost:5000"

# Fonction pour vérifier l'extension du fichier
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fonction pour récupérer l'itinéraire multi-points depuis OSRM
def get_route(osrm_url, points):
    coordinates = ";".join([f"{point[1]},{point[0]}" for point in points])
    url = f"{osrm_url}/route/v1/driving/{coordinates}"
    params = {"overview": "full", "geometries": "geojson"}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["routes"][0]["geometry"]["coordinates"]
    else:
        print(f"Erreur: {response.status_code}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Vérifier si le fichier est dans la requête
        if 'file' not in request.files:
            return "Pas de fichier sélectionné", 400

        file = request.files['file']
        
        # Vérifier si le fichier a un nom et est de type CSV
        if file.filename == '' or not allowed_file(file.filename):
            return "Fichier invalide, veuillez télécharger un fichier CSV.", 400

        # Enregistrer le fichier
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Charger les points depuis le fichier CSV
        try:
            data = pd.read_csv(file_path)
            points = list(zip(data["y"], data["x"]))  # Extraire les points (lat, lon)
            names = data["nom"].tolist()              # Extraire les noms pour les marqueurs
        except Exception as e:
            return f"Erreur lors de la lecture du CSV : {e}"

        # Obtenir l'itinéraire depuis OSRM
        route = get_route(OSRM_URL, points)
        
        # Générer la carte
        if route:
            map_ = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
            route_lat_lon = [(coord[1], coord[0]) for coord in route]
            
            folium.PolyLine(route_lat_lon, color="blue", weight=5, opacity=0.7).add_to(map_)
            for i, (point, name) in enumerate(zip(points, names)):
                folium.Marker(location=point, tooltip=name).add_to(map_)
            
            # Sauvegarder la carte dans un fichier HTML
            map_.save("templates/map.html")
            return render_template('map.html')
        else:
            return "Impossible de récupérer l'itinéraire.", 500
    
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=3000)
