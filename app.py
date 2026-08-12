import os
from flask import Flask, request, render_template_string
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

app = Flask(__name__)

# 1. Configurar las credenciales de Cloudinary
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)

# 2. RUTA PARA CRON-JOB (Evita que el servidor se duerma)
# Configura cron-job.org para que apunte exactamente a: https://onrender.com
@app.route('/ping', methods=['GET'])
def keep_alive():
    return "Server OK", 200



# 3. Ruta para mostrar la página web principal (index.html)
@app.route('/')
def index():
    # Buscamos el archivo index.html en la misma carpeta
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: Archivo index.html no encontrado en el servidor.", 404

# 4. Ruta que recibe la foto desde el formulario HTML
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'photo' not in request.files:
        return "No seleccionó ninguna foto.", 400

    file = request.files['photo']

    if file.filename == '':
        return "Archivo sin nombre.", 400

    try:
        # Enviar el archivo directamente a Cloudinary sin guardarlo en el disco duro
        upload_result = cloudinary.uploader.upload(
            file,
            folder="phones",
            transformation=[{"width": 1024, "crop": "limit"}] # Redimensiona para ahorrar espacio
        )

        # Cloudinary nos devuelve la URL pública en 'secure_url'
        image_url = upload_result.get("secure_url")

        # Devolvemos una respuesta simple con la foto subida
        return render_template_string(f'''
            <h1>¡Sólo resta un paso!</h1>
            <p>Por favor, introducelo en la ranura del buzón</p>
            <br>
            <img src="{image_url}" alt="Foto subida" style="max-width: 300px; border-radius: 8px;">
            <br><br>
            <a href="/">Subir otra foto</a>
        ''')

    except Exception as e:
        print(e)
        return "Hubo un error al procesar la imagen.", 500

if __name__ == '__main__':
    # El puerto 10000 es el que usa Render por defecto para Python
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
