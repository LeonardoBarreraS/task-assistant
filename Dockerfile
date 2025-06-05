FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias con versiones específicas compatibles
RUN pip install --no-cache-dir \
    gradio==4.19.2 \
    langgraph_sdk==0.1.34 \
    langchain_core==0.3.15 \
    httpx==0.25.2 
    #pydantic==1.10.13

# Copiar archivo de la aplicación
COPY gradio_app.py .

# Exponer puerto
EXPOSE 8080

# Comando de inicio
CMD ["python", "gradio_app.py"]