# Imagen base ligera de Python
FROM python:3.10-slim

# Evitar buffering de logs
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY . .

# Exponer el puerto que usa Flask
EXPOSE 80

# Comando de inicio
CMD ["python", "app.py"]






