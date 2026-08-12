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

    # EXTRACT ALL USER DATA FROM THE FRONTEND FORM
    device_brand = request.form.get('marca', 'desconocida').strip()
    device_model = request.form.get('modelo', '').strip()
    motivos_seleccionados = request.form.getlist('motivos')
    user_description = request.form.get('descripcion', '').strip()

    # Sanitize and format data strings for metadata storage
    brand_string = device_brand if device_brand else "desconocida"
    model_string = device_model if device_model else "no_especificado"
    tags_string = ", ".join(motivos_seleccionados) if motivos_seleccionados else "no_especificado"
    notes_string = user_description if user_description else "ninguna"

    try:
        # CONSTRUCT A PIPE-SEPARATED CONTEXT STRING FOR CLOUDINARY
        # Format example: "marca=samsung|modelo=Galaxy S20|motivos=pantalla_rota|descripcion=ninguna"
        metadata_payload = (
            f"marca={brand_string}|"
            f"modelo={model_string}|"
            f"motivos={tags_string}|"
            f"descripcion={notes_string}"
        )
        # Enviar el archivo directamente a Cloudinary sin guardarlo en el disco duro
        upload_result = cloudinary.uploader.upload(
            file,
            folder="phones",
            transformation=[{"width": 1024, "crop": "limit"}] # Redimensiona para ahorrar espacio
            context=metadata_payload
        )

        # Devolvemos una respuesta simple con la foto subida
         # Cloudinary nos devuelve la URL pública en 'secure_url'
        image_url = upload_result.get("secure_url")

        # RETORNA UNA PÁGINA DE ÉXITO ESTILIZADA
        return render_template_string(f'''
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>¡Registro Exitoso!</title>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-image: url('https://images.unsplash.com/vector-1786548471086-58641d62c5e3?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwcm9maWxlLXBhZ2V8MXx8fGVufDB8fHx8fA%3D%3D');
                        background-size: cover;
                        background-position: center;
                        background-attachment: fixed;
                        height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }}
                    .container {{
                        background-color: rgba(255, 255, 255, 0.95);
                        padding: 30px;
                        border-radius: 15px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        text-align: center;
                        max-width: 400px;
                        width: 90%;
                    }}
                    .icon {{
                        font-size: 50px;
                        color: #28a745;
                        margin-bottom: 10px;
                    }}
                    h1 {{
                        color: #155724;
                        margin-bottom: 10px;
                        font-size: 24px;
                    }}
                    p {{
                        color: #555;
                        margin-bottom: 20px;
                        font-size: 15px;
                    }}
                    .preview-img {{
                        max-width: 100%;
                        max-height: 250px;
                        border-radius: 10px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                        margin-bottom: 25px;
                        object-fit: cover;
                    }}
                    .btn-back {{
                        display: inline-block;
                        background-color: #007bff;
                        color: white;
                        text-decoration: none;
                        padding: 12px 20px;
                        font-size: 16px;
                        border-radius: 8px;
                        font-weight: bold;
                        width: calc(100% - 40px);
                        transition: background-color 0.3s;
                    }}
                    .btn-back:hover {{
                        background-color: #0056b3;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">✓</div>
                    <h1>Ultimo paso: introducilo en la ranura del buzón y listo</h1>
                    <p>Ya puedes cerrar esta página</p>

                    <img src="{image_url}" alt="Miniatura de foto subida" class="preview-img">

                    <a href="/" class="btn-back">Cerrar</a>
                </div>
            </body>
            </html>
        ''')

    except Exception as e:
        print(f"Error al subir imagen: {e}")

        # RETORNA UNA PÁGINA DE ERROR ESTILIZADA QUE INCENTIVA A REINTENTAR
        return render_template_string('''
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Hubo un problema</title>
                <style>
                    body {
                        margin: 0;
                        padding: 0;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-image: url('https://unsplash.com');
                        background-size: cover;
                        background-position: center;
                        background-attachment: fixed;
                        height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    .container {
                        background-color: rgba(255, 255, 255, 0.95);
                        padding: 30px;
                        border-radius: 15px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        text-align: center;
                        max-width: 400px;
                        width: 90%;
                    }
                    .icon {
                        font-size: 50px;
                        color: #ffc107;
                        margin-bottom: 10px;
                    }
                    h1 {
                        color: #856404;
                        margin-bottom: 10px;
                        font-size: 24px;
                    }
                    p {
                        color: #666;
                        margin-bottom: 25px;
                        font-size: 15px;
                        line-height: 1.5;
                    }
                    .btn-retry {
                        display: inline-block;
                        background-color: #ffc107;
                        color: #212529;
                        text-decoration: none;
                        padding: 12px 20px;
                        font-size: 16px;
                        border-radius: 8px;
                        font-weight: bold;
                        width: calc(100% - 40px);
                        transition: background-color 0.3s, transform 0.1s;
                    }
                    .btn-retry:hover {
                        background-color: #e0a800;
                    }
                    .btn-retry:active {
                        transform: scale(0.98);
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">⚠️</div>
                    <h1>¡Ups! Algo salió mal</h1>
                    <p>No pudimos procesar tu imagen en este momento. Si en un reintento el problema persiste, no te preocupes, puedes saltear este paso colocando directamente el teléfono que deseas descartar en el buzón y así tu acción sostenible se completa</p>

                    <a href="/" class="btn-retry">Intentar de nuevo</a>
                </div>
            </body>
            </html>
        ''')

if __name__ == '__main__':
    # El puerto 10000 es el que usa Render por defecto para Python
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
