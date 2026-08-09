import json
import subprocess
import shlex
from typing import Dict, List
from pathlib import Path
from config_manager import config

class MCPGrid:
    def __init__(self):
        # Usamos la copia INTERNA del config de MCP para portabilidad
        self.mcp_config_path = config.get_path("mcp_config")
        self.definitions_dir = Path("resources/mcp_definitions")
        
    def get_definitions(self) -> List[Dict]:
        """Scan markdown definitions to populate the catalog"""
        definitions = []
        if not self.definitions_dir.exists():
            return definitions
            
        for md_file in self.definitions_dir.glob("*.md"):
            if md_file.name == "README.md": continue
            
            try:
                content = md_file.read_text(encoding="utf-8")
                # Simple extraction
                lines = content.splitlines()
                title = md_file.stem
                description = "No description"
                
                # Extract Title (H1)
                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                        
                definitions.append({
                    "id": md_file.stem,
                    "name": title,
                    "path": str(md_file),
                    "file_name": md_file.name
                })
            except Exception:
                continue
                
        return definitions
        
    def scan_grid(self) -> Dict:
        """
        Reads mcp_config.json and checks REAL status of servers.
        """
        grid_status = {
            "node_status": "active",
            "definitions": self.get_definitions(),
            "servers": []
        }
        
        if not self.mcp_config_path.exists():
            return {"error": f"MCP Config not found at {self.mcp_config_path}"}
            
        try:
            raw_config = self.mcp_config_path.read_text(encoding='utf-8')
            # Dynamic path expansion
            raw_config = raw_config.replace("${USER_HOME}", str(Path.home()).replace("\\", "\\\\"))
            mcp_conf = json.loads(raw_config)
            
            for server_name, server_conf in mcp_conf.get("mcpServers", {}).items():
                status = self._check_health(server_name, server_conf)
                grid_status["servers"].append({
                    "name": server_name,
                    "type": "stdio" if "command" in server_conf else "sse",
                    "status": status,
                    "config": server_conf # Sanitized config ideally
                })
                
        except Exception as e:
            grid_status["error"] = str(e)
            
        return grid_status

    def _check_health(self, name: str, conf: Dict) -> str:
        """
        Verifica si el servidor responde o si el comando base es ejecutable.
        Status: healthy, degraded (timeout), offline (error), unknown
        """
        if "command" not in conf:
            return "unknown" # SSE servers need HTTP ping (TODO)

        cmd_base = conf["command"]
        
        # Heurística 1: Si es 'npx' o 'python', verificamos que el runtime exista
        # Heurística 2: Si es un ejecutable directo, intentamos invocarlo con --version o --help
        
        test_args = ["--version"]
        if cmd_base == "npx":
            # npx es lento para checkear --version del paquete, checkeamos npx mismo
            test_cmd = ["npx", "--version"]
        elif cmd_base == "docker":
            test_cmd = ["docker", "info"] # Verifica demonio activo
        elif "python" in cmd_base:
            test_cmd = [cmd_base, "--version"]
        else:
            test_cmd = [cmd_base, "--version"]

        try:
            # Ejecutamos con timeout muy corto para no bloquear
            result = subprocess.run(
                test_cmd, 
                capture_output=True, 
                timeout=3, # 3s max ping
                text=True
            )
            
            if result.returncode == 0:
                return "healthy"
            else:
                return "degraded" # Corre pero retorna error
                
        except subprocess.TimeoutExpired:
            return "degraded" # Timeout
        except FileNotFoundError:
            return "offline" # Comando no encontrado
        except Exception:
            return "offline"

if __name__ == "__main__":
    grid = MCPGrid()
    print(json.dumps(grid.scan_grid(), indent=2))
