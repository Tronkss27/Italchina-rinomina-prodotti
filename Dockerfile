# Dockerfile per Image Renamer MVP
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

# Crea directory per volumi
RUN mkdir -p /app/data/input /app/data/output

# Imposta l'entrypoint
ENTRYPOINT ["python", "app.py"]

# Comando di default (mostra help)
CMD ["--help"]

# Metadati
LABEL version="1.0.0"
LABEL description="Image Renamer MVP - Rinomina immagini basato su mapping Excel"
LABEL maintainer="Image Renamer Team"

# Volumi suggeriti per i dati
VOLUME ["/app/data"] 