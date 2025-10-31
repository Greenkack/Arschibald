#!/usr/bin/env python3
"""
Docker-Hilfstool für die App
"""
import subprocess


def create_dockerfile():
    """Erstellt optimales Dockerfile für Streamlit-App"""

    dockerfile_content = '''FROM python:3.9-slim

WORKDIR /app

# System-Dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    software-properties-common \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Python-Dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# App-Code kopieren
COPY . .

# Streamlit-Port
EXPOSE 8501

# Health-Check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Streamlit-App starten
ENTRYPOINT ["streamlit", "run", "gui.py", "--server.port=8501", "--server.address=0.0.0.0"]
'''

    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)

    print("🐳 Dockerfile erstellt!")


def create_docker_compose():
    """Erstellt docker-compose.yml"""

    compose_content = '''version: '3.8'

services:
  solar-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped

  # Optional: Datenbank
  # db:
  #   image: postgres:13
  #   environment:
  #     POSTGRES_DB: solar_app
  #     POSTGRES_USER: user
  #     POSTGRES_PASSWORD: password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

# volumes:
#   postgres_data:
'''

    with open('docker-compose.yml', 'w') as f:
        f.write(compose_content)

    print("🐳 docker-compose.yml erstellt!")


def build_and_run():
    """Baut und startet Docker-Container"""

    print("🔨 Baue Docker-Image...")
    build_result = subprocess.run(['docker', 'build', '-t', 'solar-app', '.'],
                                  capture_output=True, text=True)

    if build_result.returncode == 0:
        print("✅ Docker-Image erfolgreich gebaut!")

        print("🚀 Starte Container...")
        subprocess.run(['docker', 'run', '-p', '8501:8501', 'solar-app'])
    else:
        print(f"❌ Build-Fehler: {build_result.stderr}")


if __name__ == "__main__":
    create_dockerfile()
    create_docker_compose()

    build = input("🐳 Docker-Image bauen und starten? (y/n): ")
    if build.lower() == 'y':
        build_and_run()
