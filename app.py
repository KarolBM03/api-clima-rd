from flask import Flask, jsonify
import requests
import concurrent.futures
import os

app = Flask(__name__)

# 🔑 Tu API key desde las variables de entorno de Render
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# 🗺️ Provincias de República Dominicana
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
        'q': f"{ciudad},DO",
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'es'
    }
    try:
        r = requests.get(BASE_URL, params=params)
        if r.status_code == 200:
            data = r.json()
            return {
                "provincia": ciudad,
                "temperatura": data["main"]["temp"],
                "descripcion": data["weather"][0]["description"],
                "humedad": data["main"]["humidity"],
                "viento": data["wind"]["speed"]
            }
        else:
            return {"provincia": ciudad, "error": f"No disponible ({r.status_code})"}
    except Exception as e:
        return {"provincia": ciudad, "error": str(e)}

# 🧠 Ruta raíz: mostrará TODAS las provincias directamente
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
    from flask import request
    ciudad = request.args.get("ciudad")
    if not ciudad:
        return jsonify({"error": "Debes especificar una ciudad (?ciudad=)"})
    return jsonify(obtener_clima(ciudad))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
