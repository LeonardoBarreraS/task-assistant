# Imagen base con Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar solo requirements primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto (Railway establece PORT como variable de entorno)
EXPOSE 8080

# Comando para ejecutar la app
CMD ["python", "gradio_app.py"]