# Dockerfile dla Django
FROM python:3.10-slim

# Ustawienia środowiska
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Praca w katalogu aplikacji
WORKDIR /app

# Instalacja zależności
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie projektu
COPY ./ /app/

# Uruchomienie serwera
CMD ["python", "manage.py", "runserver"]
