# Imagen base ligera de Python
FROM python:3.10-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar el resto de los archivos del proyecto
COPY . .

# Exponer el puerto 80 (el mismo que usas en app.py)
EXPOSE 80

# Comando de inicio de la app Flask
CMD ["python", "app.py"]

