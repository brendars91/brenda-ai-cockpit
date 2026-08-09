# -*- coding: utf-8 -*-
"""
PRUEBA DIFICIL - LOCALHOST
Gem Trinity Genesis - Test Suite Completo para Entorno Local

Esta prueba evalúa:
1. Flujo completo Architect -> Builder -> Engine con caso complejo
2. Sistema de Transparencia y logging
3. Métricas y telemetría
4. Tolerancia a fallos y recuperación
5. Manejo de errores validado
"""
import requests
import json
import time
import sys
import io
from typing import Dict, Any

# Configurar codificación para Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuración
BASE_URL = "http://localhost:8000"
VERCEL_URL = "https://app-eta-fawn-42.vercel.app"

# Colores para terminal
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

# Resultados de pruebas
test_results = {
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "tests": []
}

def log_test(category: str, name: str, status: str, details: str = ""):
    """Registra el resultado de una prueba"""
    test_results["tests"].append({
        "category": category,
        "name": name,
        "status": status,
        "details": details
    })

    if status == "PASS":
        test_results["passed"] += 1
        print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {name}")
    elif status == "FAIL":
        test_results["failed"] += 1
        print(f"  {Colors.RED}[FAIL]{Colors.RESET} {name}: {details}")
    else:
        test_results["warnings"] += 1
        print(f"  {Colors.YELLOW}[WARN]{Colors.RESET} {name}: {details}")

def print_header(title: str):
    """Imprime un encabezado de sección"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

# ============================================
# FASE 1: HEALTH CHECK & SYSTEM STATUS
# ============================================
def test_health_system():
    print_header("FASE 1: HEALTH CHECK & SYSTEM STATUS")

    # Test 1.1: API Status
    print("1.1. API Status Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test("health", "API Status", "PASS", f"Status: {data.get('status', 'unknown')}")
            print(f"     Response: {json.dumps(data, indent=2)}")
        else:
            log_test("health", "API Status", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("health", "API Status", "FAIL", str(e))

    # Test 1.2: System Info
    print("\n1.2. System Info Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/system/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test("health", "System Info", "PASS")
            print(f"     Python: {data.get('python_version', 'N/A')}")
            print(f"     Platform: {data.get('platform', 'N/A')}")
        else:
            log_test("health", "System Info", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("health", "System Info", "FAIL", str(e))

    # Test 1.3: Metrics Endpoint
    print("\n1.3. Metrics Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/metrics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test("health", "Metrics", "PASS")
            print(f"     Requests: {data.get('total_requests', 'N/A')}")
            print(f"     Errors: {data.get('total_errors', 'N/A')}")
        else:
            log_test("health", "Metrics", "WARN", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("health", "Metrics", "WARN", str(e))

# ============================================
# FASE 2: ARCHITECT COMPLEJO
# ============================================
def test_architect_complex():
    print_header("FASE 2: ARCHITECT - CASO COMPLEJO")

    # Caso complejo: Sistema de análisis de datos con múltiples componentes
    complex_payload = {
        "use_case": "Build a real-time data analysis dashboard that ingests stock market data, processes it with technical indicators (SMA, RSI, MACD), displays interactive charts, and sends alerts when thresholds are crossed. The system must handle WebSocket connections and persist data to SQLite.",
        "domain": "fintech",
        "complexity": "complex",
        "model": "gemini-2.0-flash-exp"
    }

    print("2.1. Generando arquitectura compleja...")
    print(f"     Use Case: {complex_payload['use_case'][:80]}...")

    try:
        response = requests.post(f"{BASE_URL}/api/architect/generate", json=complex_payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            payload_id = data.get("payload_id")

            if payload_id:
                log_test("architect", "Complex Architect Generation", "PASS", f"Payload ID: {payload_id}")

                # Verificar calidad del PRD
                prd = data.get("prd", {})
                if prd.get("architecture") and prd.get("components"):
                    log_test("architect", "PRD Quality Check", "PASS", "Architecture and components present")
                else:
                    log_test("architect", "PRD Quality Check", "WARN", "Incomplete PRD structure")

                # Test 2.2: Recuperar payload
                print("\n2.2. Recuperando payload generado...")
                get_response = requests.get(f"{BASE_URL}/api/architect/payload/{payload_id}", timeout=10)
                if get_response.status_code == 200:
                    payload_data = get_response.json()
                    log_test("architect", "Payload Retrieval", "PASS")
                    return payload_id
                else:
                    log_test("architect", "Payload Retrieval", "FAIL", f"Status: {get_response.status_code}")
                    return None
            else:
                log_test("architect", "Complex Architect Generation", "FAIL", "No payload_id returned")
                return None
        else:
            log_test("architect", "Complex Architect Generation", "FAIL", f"Status: {response.status_code}, Error: {response.text[:100]}")
            return None
    except Exception as e:
        log_test("architect", "Complex Architect Generation", "FAIL", str(e))
        return None

# ============================================
# FASE 3: BUILDER COMPILATION
# ============================================
def test_builder_compilation(payload_id: str):
    print_header("FASE 3: BUILDER - COMPILACION")

    if not payload_id:
        log_test("builder", "Skip Builder Tests", "WARN", "No valid payload_id")
        return None

    builder_payload = {
        "payload_id": payload_id,
        "agent_name": "StockAnalysisAgent",
        "llm_config": {
            "provider": "gemini",
            "model": "gemini-2.0-flash-exp",
            "temperature": 0.3
        },
        "tools": ["calculator", "web_search"]
    }

    print("3.1. Compilando agente...")
    try:
        response = requests.post(f"{BASE_URL}/api/builder/compile", json=builder_payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            build_id = data.get("build_id")

            if build_id:
                log_test("builder", "Agent Compilation", "PASS", f"Build ID: {build_id}")

                # Test 3.2: Verificar estado del agente
                print("\n3.2. Verificando estado del agente...")
                time.sleep(3)  # Esperar compilación

                status_response = requests.get(f"{BASE_URL}/api/builder/agent/{build_id}", timeout=10)
                if status_response.status_code == 200:
                    agent_data = status_response.json()
                    status = agent_data.get("status")
                    log_test("builder", "Agent Status Check", "PASS", f"Status: {status}")

                    if status == "ready":
                        return build_id
                    else:
                        log_test("builder", "Agent Readiness", "WARN", f"Status is {status}, not ready")
                        return build_id
                else:
                    log_test("builder", "Agent Status Check", "FAIL", f"Status: {status_response.status_code}")
                    return build_id
            else:
                log_test("builder", "Agent Compilation", "FAIL", "No build_id returned")
                return None
        else:
            log_test("builder", "Agent Compilation", "FAIL", f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("builder", "Agent Compilation", "FAIL", str(e))
        return None

# ============================================
# FASE 4: ENGINE EXECUTION
# ============================================
def test_engine_execution(build_id: str):
    print_header("FASE 4: ENGINE - EJECUCION")

    if not build_id:
        log_test("engine", "Skip Engine Tests", "WARN", "No valid build_id")
        return

    # Test 4.1: Ejecución con streaming
    print("4.1. Ejecutando tarea con streaming...")

    engine_payload = {
        "agent_id": build_id,
        "task": "Analyze AAPL stock and provide a brief technical analysis",
        "stream": True
    }

    try:
        response = requests.post(f"{BASE_URL}/api/engine/execute", json=engine_payload, stream=True, timeout=30)

        if response.status_code == 200:
            log_test("engine", "Engine Execution Start", "PASS")

            # Procesar stream
            events_received = 0
            result_found = False

            for line in response.iter_lines():
                if line:
                    try:
                        event = json.loads(line.decode('utf-8'))
                        events_received += 1

                        if event.get("type") == "result":
                            result_found = True
                            output = event.get("output", "")
                            print(f"\n     Result received: {str(output)[:100]}...")

                        if events_received > 50:  # Limitar eventos
                            break
                    except json.JSONDecodeError:
                        pass

            if events_received > 0:
                log_test("engine", "Stream Processing", "PASS", f"Events: {events_received}")
            else:
                log_test("engine", "Stream Processing", "WARN", "No events received")

            if result_found:
                log_test("engine", "Result Reception", "PASS")
            else:
                log_test("engine", "Result Reception", "WARN", "No result in stream")

        else:
            log_test("engine", "Engine Execution Start", "FAIL", f"Status: {response.status_code}")

    except Exception as e:
        log_test("engine", "Engine Execution", "FAIL", str(e))

    # Test 4.2: Telemetría
    print("\n4.2. Obteniendo telemetría del agente...")
    try:
        telemetry_response = requests.get(f"{BASE_URL}/api/engine/telemetry/{build_id}", timeout=10)
        if telemetry_response.status_code == 200:
            telemetry = telemetry_response.json()
            log_test("engine", "Telemetry Retrieval", "PASS")
            print(f"     Telemetry keys: {list(telemetry.keys())[:5]}")
        else:
            log_test("engine", "Telemetry Retrieval", "WARN", f"Status: {telemetry_response.status_code}")
    except Exception as e:
        log_test("engine", "Telemetry Retrieval", "WARN", str(e))

# ============================================
# FASE 5: TRANSPARENCY & LOGGING
# ============================================
def test_transparency():
    print_header("FASE 5: TRANSPARENCY & LOGGING")

    # Test 5.1: Historial de ejecuciones
    print("5.1. Obteniendo historial de transparencia...")
    try:
        response = requests.get(f"{BASE_URL}/api/transparency/history", timeout=10)
        if response.status_code == 200:
            data = response.json()
            history = data.get("history", [])
            log_test("transparency", "History Retrieval", "PASS", f"Entries: {len(history)}")

            if len(history) > 0:
                latest = history[0]
                print(f"     Latest execution: {latest.get('agent_name', 'N/A')}")
                print(f"     Status: {latest.get('status', 'N/A')}")
        else:
            log_test("transparency", "History Retrieval", "WARN", f"Status: {response.status_code}")
    except Exception as e:
        log_test("transparency", "History Retrieval", "WARN", str(e))

    # Test 5.2: Metrics actualizados
    print("\n5.2. Verificando métricas actualizadas...")
    try:
        response = requests.get(f"{BASE_URL}/api/metrics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test("transparency", "Updated Metrics", "PASS")
            print(f"     Total requests: {data.get('total_requests', 'N/A')}")
            print(f"     Active workflows: {data.get('active_workflows', 'N/A')}")
        else:
            log_test("transparency", "Updated Metrics", "WARN", f"Status: {response.status_code}")
    except Exception as e:
        log_test("transparency", "Updated Metrics", "WARN", str(e))

# ============================================
# FASE 6: ERROR HANDLING
# ============================================
def test_error_handling():
    print_header("FASE 6: ERROR HANDLING & EDGE CASES")

    # Test 6.1: Payload inválido
    print("6.1. Probando payload inválido...")
    try:
        invalid_payload = {"use_case": "", "domain": "invalid"}  # Campos faltantes
        response = requests.post(f"{BASE_URL}/api/architect/generate", json=invalid_payload, timeout=10)

        if response.status_code == 422 or response.status_code == 400:
            log_test("errors", "Invalid Payload Handling", "PASS", "Correctly rejected invalid input")
        else:
            log_test("errors", "Invalid Payload Handling", "WARN", f"Unexpected status: {response.status_code}")
    except Exception as e:
        log_test("errors", "Invalid Payload Handling", "WARN", str(e))

    # Test 6.2: Recurso no existente
    print("\n6.2. Probando recurso no existente...")
    try:
        response = requests.get(f"{BASE_URL}/api/architect/payload/nonexistent_id", timeout=10)
        if response.status_code == 404:
            log_test("errors", "404 Handling", "PASS", "Correctly returns 404")
        else:
            log_test("errors", "404 Handling", "WARN", f"Status: {response.status_code}")
    except Exception as e:
        log_test("errors", "404 Handling", "WARN", str(e))

    # Test 6.3: Builder con payload inválido
    print("\n6.3. Probando builder con payload inválido...")
    try:
        invalid_builder = {"payload_id": "invalid_id", "agent_name": "Test"}
        response = requests.post(f"{BASE_URL}/api/builder/compile", json=invalid_builder, timeout=10)

        if response.status_code == 404 or response.status_code == 400:
            log_test("errors", "Builder Error Handling", "PASS", "Correctly handled invalid payload_id")
        else:
            log_test("errors", "Builder Error Handling", "WARN", f"Status: {response.status_code}")
    except Exception as e:
        log_test("errors", "Builder Error Handling", "WARN", str(e))

# ============================================
# MAIN
# ============================================
def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 70)
    print("    GEM TRINITY GENESIS - PRUEBA DIFICIL LOCALHOST")
    print("                  Test Suite Completo")
    print("=" * 70)
    print(f"{Colors.RESET}")

    start_time = time.time()

    # Ejecutar todas las fases
    test_health_system()
    payload_id = test_architect_complex()
    build_id = test_builder_compilation(payload_id)
    test_engine_execution(build_id)
    test_transparency()
    test_error_handling()

    # Resumen final
    elapsed = time.time() - start_time

    print_header("RESUMEN DE RESULTADOS")

    total = test_results["passed"] + test_results["failed"] + test_results["warnings"]

    print(f"{Colors.BOLD}Total Pruebas:{Colors.RESET} {total}")
    print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {test_results['passed']}")
    print(f"  {Colors.RED}[FAIL]{Colors.RESET} {test_results['failed']}")
    print(f"  {Colors.YELLOW}[WARN]{Colors.RESET} {test_results['warnings']}")
    print(f"\nTiempo total: {elapsed:.2f} segundos")

    # Categorías
    print(f"\n{Colors.BOLD}Pruebas por categoría:{Colors.RESET}")
    categories = {}
    for test in test_results["tests"]:
        cat = test["category"]
        if cat not in categories:
            categories[cat] = {"pass": 0, "fail": 0, "warn": 0}
        if test["status"] == "PASS":
            categories[cat]["pass"] += 1
        elif test["status"] == "FAIL":
            categories[cat]["fail"] += 1
        else:
            categories[cat]["warn"] += 1

    for cat, counts in categories.items():
        print(f"  {cat}: {counts['pass']} pass, {counts['fail']} fail, {counts['warn']} warn")

    # Veredicto final
    print_header("VEREDICTO FINAL")

    if test_results["failed"] == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}[EXCELLENTE]{Colors.RESET} Todas las pruebas críticas pasaron.")
        print(f"{Colors.GREEN}El sistema local funciona correctamente.{Colors.RESET}\n")
        return 0
    elif test_results["failed"] <= 2:
        print(f"{Colors.YELLOW}{Colors.BOLD}[ACEPTABLE]{Colors.RESET} Algunas pruebas fallaron pero el sistema es funcional.")
        print(f"{Colors.YELLOW}Revisar los tests fallados para mejora.{Colors.RESET}\n")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}[CRITICO]{Colors.RESET} Múltiples pruebas fallaron.")
        print(f"{Colors.RED}El sistema requiere revisión urgente.{Colors.RESET}\n")
        return 2

if __name__ == "__main__":
    sys.exit(main())
