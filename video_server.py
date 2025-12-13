"""
Simple HTTP Server für Video-Streaming
Läuft parallel zu Streamlit und serviert Videos aus static/intro_videos/
Verwendet http.server aus der Standardbibliothek (kein Flask notwendig)

Features:
- Singleton Pattern: verhindert doppelte Server-Starts
- Port-Verfügbarkeit-Check
- Retry-Logic mit exponential backoff
- Health-Check Endpoint
- Graceful Shutdown
- CORS-Header für Cross-Origin-Requests
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
import sys
import threading
import socket
import time
import atexit
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('VideoServer')

# Singleton: Server-Instanz
_server_instance = None
_server_lock = threading.Lock()

class VideoHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Setze Arbeitsverzeichnis auf static/intro_videos/
        video_dir = Path(__file__).parent / 'static' / 'intro_videos'
        video_dir.mkdir(parents=True, exist_ok=True)  # Erstelle Verzeichnis falls nicht vorhanden
        super().__init__(*args, directory=str(video_dir), **kwargs)
    
    def end_headers(self):
        # CORS-Header für Cross-Origin-Requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        # Cache-Control für bessere Performance
        self.send_header('Cache-Control', 'public, max-age=3600')
        super().end_headers()
    
    def do_GET(self):
        """Handle GET requests mit Health-Check"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "service": "video-server"}')
            return
        super().do_GET()
    
    def log_message(self, format, *args):
        """Custom Logging"""
        logger.debug(f"{self.address_string()} - {format % args}")

def is_port_available(port, host='localhost'):
    """Prüfe ob Port verfügbar ist"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.bind((host, port))
            return True
    except (socket.error, OSError):
        return False

def find_available_port(start_port=8503, max_attempts=10):
    """Finde verfügbaren Port ab start_port"""
    for i in range(max_attempts):
        port = start_port + i
        if is_port_available(port):
            return port
    return None

def start_video_server(port=8503, retry_attempts=3, retry_delay=2):
    """
    Starte Video-Server im Hintergrund mit Retry-Logic
    
    Args:
        port: Bevorzugter Port (default: 8503)
        retry_attempts: Anzahl Wiederholungsversuche
        retry_delay: Wartezeit zwischen Versuchen (Sekunden)
    
    Returns:
        tuple: (success: bool, port: int, message: str)
    """
    global _server_instance
    
    with _server_lock:
        # Singleton: Prüfe ob Server bereits läuft
        if _server_instance is not None:
            logger.info(f"Video-Server läuft bereits auf Port {_server_instance.server_port}")
            return True, _server_instance.server_port, "Already running"
        
        # Prüfe Port-Verfügbarkeit
        if not is_port_available(port):
            logger.warning(f"Port {port} ist belegt, suche alternativen Port...")
            alt_port = find_available_port(port)
            if alt_port:
                port = alt_port
                logger.info(f"Verwende alternativen Port: {port}")
            else:
                logger.error("Kein verfügbarer Port gefunden")
                return False, 0, "No available port"
        
        # Retry-Logic mit exponential backoff
        for attempt in range(retry_attempts):
            try:
                _server_instance = HTTPServer(('localhost', port), VideoHandler)
                logger.info(f"Video-Server gestartet auf http://localhost:{port}")
                
                # Graceful Shutdown bei App-Ende
                def shutdown_server():
                    global _server_instance
                    if _server_instance:
                        logger.info("Video-Server wird heruntergefahren...")
                        _server_instance.shutdown()
                        _server_instance = None
                
                atexit.register(shutdown_server)
                
                # Server-Loop (blockierend)
                _server_instance.serve_forever()
                return True, port, "Started"
                
            except OSError as e:
                logger.error(f"Versuch {attempt+1}/{retry_attempts} fehlgeschlagen: {e}")
                if attempt < retry_attempts - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Warte {wait_time}s vor erneutem Versuch...")
                    time.sleep(wait_time)
                else:
                    logger.error("Video-Server konnte nicht gestartet werden")
                    return False, 0, str(e)
            except Exception as e:
                logger.exception(f"Unerwarteter Fehler: {e}")
                return False, 0, str(e)
    
    return False, 0, "Unknown error"

def get_server_status():
    """Gib Server-Status zurück"""
    global _server_instance
    if _server_instance:
        return {
            'running': True,
            'port': _server_instance.server_port,
            'address': f"http://localhost:{_server_instance.server_port}"
        }
    return {'running': False}

if __name__ == '__main__':
    print("Starting Video Server on http://localhost:8503")
    success, port, msg = start_video_server()
    if success:
        print(f"Server running on port {port}")
    else:
        print(f"Failed to start server: {msg}")
        sys.exit(1)

