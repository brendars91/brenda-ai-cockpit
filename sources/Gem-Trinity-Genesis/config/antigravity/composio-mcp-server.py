#!/usr/bin/env python3
"""
Composio MCP Server - Wrapper que expone herramientas de Composio via MCP stdio
Usa la API REST de Composio para ejecutar acciones
"""

import os
import sys
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional
import httpx

# Configurar logging a stderr para no contaminar stdout (MCP usa stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
COMPOSIO_BASE_URL = "https://backend.composio.dev/api/v3"


class ComposioMCPServer:
    """Servidor MCP que expone herramientas de Composio"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={
                "X-API-Key": COMPOSIO_API_KEY,
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        self.tools_cache: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Inicializa el servidor y carga las herramientas disponibles"""
        try:
            # Obtener lista de apps/tools disponibles (v3 usa /tools en lugar de /actions)
            response = await self.client.get(f"{COMPOSIO_BASE_URL}/tools")
            if response.status_code == 200:
                tools_data = response.json()
                # Convertir tools de Composio a formato MCP tools
                self.tools_cache = self._convert_actions_to_tools(tools_data.get("items", [])[:50])  # Limitar a 50 para performance
                logger.info(f"Loaded {len(self.tools_cache)} Composio tools")
            else:
                logger.error(f"Failed to load Composio tools: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error initializing Composio: {e}")
    
    def _convert_actions_to_tools(self, actions: List[Dict]) -> List[Dict]:
        """Convierte acciones de Composio a formato MCP tools"""
        tools = []
        for action in actions:
            tool = {
                "name": action.get("name", "unknown"),
                "description": action.get("description", "No description"),
                "inputSchema": {
                    "type": "object",
                    "properties": action.get("parameters", {}).get("properties", {}),
                    "required": action.get("parameters", {}).get("required", [])
                }
            }
            tools.append(tool)
        return tools
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta de Composio"""
        try:
            # Ejecutar tool via API de Composio v3
            response = await self.client.post(
                f"{COMPOSIO_BASE_URL}/tools/{tool_name}/execute",
                json={"input": arguments}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result.get("data", result), indent=2)
                        }
                    ]
                }
            else:
                error_msg = f"Composio API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "content": [{"type": "text", "text": error_msg}],
                    "isError": True
                }
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            return {
                "content": [{"type": "text", "text": error_msg}],
                "isError": True
            }
    
    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Maneja requests MCP"""
        method = request.get("method")
        request_id = request.get("id")
        
        # Las notifications no tienen ID y no requieren respuesta
        is_notification = request_id is None
        
        try:
            if method == "initialize":
                await self.initialize()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True}
                        },
                        "serverInfo": {
                            "name": "composio-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools_cache
                    }
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                if not params:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: params object is required"
                        }
                    }
                
                tool_name = params.get("name")
                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: 'name' is required"
                        }
                    }
                
                arguments = params.get("arguments", {})
                
                result = await self.execute_tool(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            elif method == "notifications/initialized":
                # Esta es una notification, no requiere respuesta
                logger.info("Client initialized")
                return None
            
            else:
                if is_notification:
                    logger.warning(f"Unknown notification: {method}")
                    return None
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            if is_notification:
                return None
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run(self):
        """Loop principal del servidor MCP (stdio)"""
        logger.info("Composio MCP Server starting on stdio")
        
        while True:
            try:
                # Leer línea de stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parsear request JSON-RPC
                request = json.loads(line)
                
                # Procesar request
                response = await self.handle_request(request)
                
                # Solo enviar response si no es None (las notifications no requieren respuesta)
                if response is not None:
                    print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                break
        
        await self.client.aclose()
        logger.info("Composio MCP Server stopped")


async def main():
    """Entry point"""
    if not COMPOSIO_API_KEY:
        logger.error("COMPOSIO_API_KEY environment variable not set")
        sys.exit(1)
    
    server = ComposioMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
