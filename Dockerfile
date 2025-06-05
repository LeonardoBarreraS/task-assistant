FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
RUN pip install --no-cache-dir \
    gradio==4.44.0 \
    langgraph_sdk==0.1.33 \
    langchain_core==0.3.15

# Copiar archivo de la aplicación
COPY gradio_app.py .

# Exponer puerto
EXPOSE 7860

# Comando de inicio
CMD ["python", "gradio_app.py"]