from flask import Flask, jsonify, request
import requests
import concurrent.futures
import os

app = Flask(__name__)

# 🔑 API Key desde variables de entorno (Render)
API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "http://api.weatherapi.com/v1/current.json"

# 🗺 Provincias de República Dominicana
PROVINCIAS_RD = [
    "Santo Domingo", "Distrito Nacional", "Santiago", "La Vega", "San Cristobal",
    "San Pedro de Macoris", "La Romana", "San Juan", "Puerto Plata", "Duarte",
    "Espaillat", "Peravia", "Azua", "Barahona", "Monte Plata", "Monseñor Nouel",
    "Hermanas Mirabal", "María Trinidad Sánchez", "Sánchez Ramírez", "La Altagracia",
    "El Seibo", "Hato Mayor", "San José de Ocoa", "Samaná", "Bahoruco", "Elías Piña",
    "Dajabón", "Monte Cristi", "Independencia", "Pedernales", "Valverde", "Santiago Rodríguez"
]

# 🌡️ Función para obtener el clima de una provincia
def obtener_clima(ciudad):
    params = {
        'key': API_KEY,
        'q': f"{ciudad},DO",
        'lang': 'es'
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {
                "provincia": ciudad,
                "temperatura": data["current"]["temp_c"],
                "descripcion": data["current"]["condition"]["text"],
                "humedad": data["current"]["humidity"],
                "viento": data["current"]["wind_kph"]
            }
        else:
            return {"provincia": ciudad, "error": f"No disponible ({r.status_code})"}
    except Exception as e:
        return {"provincia": ciudad, "error": str(e)}

# 🧠 Ruta raíz: mostrará TODAS las provincias
@app.route('/', methods=['GET'])
def clima_principal():
    resultados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(obtener_clima, p) for p in PROVINCIAS_RD]
        for future in concurrent.futures.as_completed(futures):
            resultados.append(future.result())

    return jsonify({
        "pais": "República Dominicana",
        "total_provincias": len(PROVINCIAS_RD),
        "data": resultados
    })

# 🌤 Endpoint individual (por ciudad)
@app.route('/clima', methods=['GET'])
def clima_individual():
    ciudad = request.args.get("ciudad")
    if not ciudad:
        return jsonify({"error": "Debes especificar una ciudad (?ciudad=)"}), 400
    return jsonify(obtener_clima(ciudad))

# 🏁 Run
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
