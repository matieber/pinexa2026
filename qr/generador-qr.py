import os
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
import qrcode

# Cargar variables de entorno (puedes tener un archivo .env local con tu FLASK_SECRET_KEY)
load_dotenv()

# Clave secreta (debe ser la misma que uses en tu app.py de Flask)
secret_key = os.getenv("FLASK_SECRET_KEY")
print(f"secret_key {secret_key}")
serializer = URLSafeTimedSerializer(secret_key)

# Arreglo con las ubicaciones de tus buzones físicos
ubicaciones = [
    "exactas-unicen"
]

# Dominio de tu aplicación en producción (reemplaza con tu URL real de Render)
DOMINIO_BASE = "https://pinexa2026.onrender.com"

print("--- GENERANDO CÓDIGOS QR ---")

for ubicacion in ubicaciones:
    # 1. Generar el token firmado con la ubicación
    token = serializer.dumps(ubicacion, salt='ubicacion-qr-salt')

    # 2. Construir la URL final que irá dentro del QR
    url_final = f"{DOMINIO_BASE}/?token={token}"

    # 3. Crear la imagen del código QR
    img = qrcode.make(url_final)

    # 4. Definir el nombre del archivo usando la ubicación del arreglo
    nombre_archivo = f"{ubicacion}.png"

    # 5. Guardar la imagen en el directorio actual donde corre el script
    img.save(nombre_archivo)

    print(f"[✔] Archivo guardado: {nombre_archivo}")
    print(f"    URL asociada: {url_final}\n")

print("¡Proceso finalizado! Ya puedes usar las imágenes PNG generadas para imprimirlas.")
