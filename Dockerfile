# -----------------------------------------------------------
# Imagen base ligera de Python (3.10-slim es pequeña y estable)
# -----------------------------------------------------------
FROM python:3.10-slim

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
# Instala las dependencias listadas en requirements.txt
# --no-cache-dir evita almacenar archivos temporales (más ligero)
# -----------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt

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


