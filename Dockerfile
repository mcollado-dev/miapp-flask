# Imagen base ligera de Python
FROM python:3.10-slim

# Evitar prompts de instalación y limpiar cache
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos del proyecto
COPY . .

# Exponer el puerto interno
EXPOSE 80

# Usar Gunicorn para producción (4 workers)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app:app"]



