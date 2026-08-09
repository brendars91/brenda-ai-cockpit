#!/usr/bin/env python3
"""
AGCCE Dashboard Server
Genera datos para el dashboard y sirve archivos estaticos.

Uso: python dashboard_server.py [--port 8080] [--generate-only]
"""

import json
import sys
import os
import http.server
import socketserver
from pathlib import Path

# Importar collector de metricas
try:
    from metrics_collector import TelemetryReader
except ImportError:
    # Fallback si se ejecuta desde otro directorio
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
    from metrics_collector import TelemetryReader


def generate_dashboard_data(days: int = 7) -> dict:
    """Genera datos para el dashboard."""
    
    # Obtener resumen
    summary = TelemetryReader.get_summary(days)
    
    # Obtener timeline de seguridad
    timeline = TelemetryReader.get_security_timeline(days)
    
    # Obtener proyectos
    projects = get_projects()
    
    # Estructurar para el dashboard
    data = {
        "generated_at": __import__('datetime').datetime.now().isoformat(),
        "period_days": days,
        "reliability": summary.get("reliability", {}),
        "performance": summary.get("performance", {}),
        "security": summary.get("security", {}),
        "timeline": timeline[:20],  # Ultimos 20 eventos
        "projects": projects
    }
    
    return data


def get_projects() -> list:
    """Lee proyectos del registro y solo incluye proyectos explícitamente creados."""
    projects = []
    root = Path(__file__).parent.parent
    
    # 1. Solo proyectos creados con project_creator.py (tienen .agcce_project marker)
    try:
        for item in root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Verificar si tiene el marcador de proyecto AGCCE
                if (item / ".agcce_project").exists():
                    projects.append(item.name)
    except Exception as e:
        print(f"Error scanning projects: {e}")

    # 2. Proyectos registrados externamente
    config_file = root / "config" / "projects.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                registered = json.load(f)
                for proj in registered:
                    projects.append(proj['name'])
        except Exception as e:
            print(f"Error reading project registry: {e}")

    # 3. Agregar el propio Engine
    projects.append("Agente Copilot Engine")
    
    return sorted(list(set(projects)))


def save_dashboard_data():
    """Genera y guarda datos para el dashboard."""
    data = generate_dashboard_data()
    
    # Crear directorio logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    output_path = "logs/dashboard_data.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Dashboard data saved to: {output_path}")
    return output_path


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Handler personalizado para servir el dashboard."""
    
    def __init__(self, *args, **kwargs):
        # Cambiar al directorio del dashboard
        super().__init__(*args, directory=str(Path(__file__).parent.parent), **kwargs)
    
    def do_POST(self):
        # Manejar eliminación de proyectos
        if self.path == '/api/unregister':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                project_name = data.get('project')
                
                # Importar función de unregister
                import sys
                sys.path.insert(0, str(Path(__file__).parent))
                from unregister_project import unregister_project
                
                if unregister_project(project_name):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                print(f"Error unregistering project: {e}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        # Si piden datos, regenerar
        if self.path == '/logs/dashboard_data.json':
            save_dashboard_data()
        
        # Si piden / redirigir a dashboard
        if self.path == '/':
            self.path = '/dashboard/index.html'
        
        return super().do_GET()
    
    def log_message(self, format, *args):
        # Log silencioso
        pass


def run_server(port: int = 8080):
    """Inicia servidor HTTP para el dashboard."""
    os.chdir(Path(__file__).parent.parent)
    
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        print(f"\n=== AGCCE Dashboard Server ===")
        print(f"URL: http://localhost:{port}")
        print(f"Dashboard: http://localhost:{port}/dashboard/index.html")
        print(f"\nPresiona Ctrl+C para detener\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido")


def main():
    if "--generate-only" in sys.argv:
        save_dashboard_data()
        return
    
    if "--help" in sys.argv:
        print("Uso: python dashboard_server.py [--port 8080] [--generate-only]")
        print("\nOpciones:")
        print("  --port N         Puerto del servidor (default: 8080)")
        print("  --generate-only  Solo generar datos, no iniciar servidor")
        return
    
    port = 8080
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])
    
    # Generar datos iniciales
    save_dashboard_data()
    
    # Iniciar servidor
    run_server(port)


if __name__ == '__main__':
    main()
