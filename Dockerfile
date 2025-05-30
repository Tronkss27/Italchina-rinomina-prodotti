# Dockerfile per Image Renamer - Railway Compatible
FROM python:3.9-slim

# Imposta variabili d'ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Crea directory di lavoro
WORKDIR /app

# Copia e installa dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice sorgente
COPY . .

# Crea directory necessarie
RUN mkdir -p uploads output

# Espone la porta (Railway la detecta automaticamente)
EXPOSE 5000

# Comando per avviare la web app
CMD ["python", "web_app.py"]

# Metadati
LABEL version="1.0.0"
LABEL description="Image Renamer Web App - Railway Ready"
LABEL maintainer="Image Renamer Team" 