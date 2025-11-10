# -----------------------------------------------------------
# Imagen base ligera de Python (3.11-slim para soportar contourpy==1.3.3)
# -----------------------------------------------------------
FROM python:3.11-slim
# Si quisieras mantener Python 3.10 (más estable y ligera), usarías:
# FROM python:3.10-slim
# NOTA: En Python 3.10 contourpy==1.3.3 no está disponible, solo hasta 1.3.2

# -----------------------------------------------------------
# Desactiva el buffering del output de Python
# (para que los logs se muestren inmediatamente en consola)
# -----------------------------------------------------------
ENV PYTHONUNBUFFERED=1

# -----------------------------------------------------------
# Crea y establece el directorio de trabajo dentro del contenedor
# /app será donde vivirá el código fuente de mi aplicación
# -----------------------------------------------------------
WORKDIR /app

# -----------------------------------------------------------
# Copia el archivo de dependencias al contenedor
# -----------------------------------------------------------
COPY requirements.txt .

# -----------------------------------------------------------
# Actualiza pip y luego instala las dependencias
# --no-cache-dir evita almacenar archivos temporales (más ligero)
# -----------------------------------------------------------
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# En requirements.txt puedes usar contourpy==1.3.3
# Con Python 3.10 habría que bajarlo a 1.3.2

# -----------------------------------------------------------
# Copia todo el contenido del proyecto (código, templates, etc.)
# al directorio de trabajo del contenedor
# -----------------------------------------------------------
COPY . .

# -----------------------------------------------------------
# Expone el puerto 80, que es el que Flask usará dentro del contenedor
# -----------------------------------------------------------
EXPOSE 80

# -----------------------------------------------------------
# Comando por defecto: inicia la aplicación Flask
# Se ejecuta con Python directamente (sin necesidad de gunicorn en este caso)
# -----------------------------------------------------------
CMD ["python", "app.py"]



