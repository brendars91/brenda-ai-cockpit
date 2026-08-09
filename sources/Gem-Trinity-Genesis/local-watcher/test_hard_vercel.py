# -*- coding: utf-8 -*-
"""
PRUEBA DIFICIL - VERCEL DEPLOYMENT
Gem Trinity Genesis - Test Suite para Producción (GitHub URL)

Esta prueba evalúa el despliegue en producción:
1. Conectividad API a través de Vercel -> Oracle Cloud
2. Health checks y respuestas del backend
3. Configuración CORS
4. Endpoints públicos disponibles
5. Performance y tiempos de respuesta
6. Manejo de errores en producción
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

# Configuración - URL de Producción
PROD_URL = "https://app-eta-fawn-42.vercel.app"
BACKEND_IP = "https://100.69.240.73"

# Colores para terminal
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

# Resultados de pruebas
test_results = {
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "tests": [],
    "response_times": []
}

def log_test(category: str, name: str, status: str, details: str = "", response_time: float = 0):
    """Registra el resultado de una prueba"""
    test_results["tests"].append({
        "category": category,
        "name": name,
        "status": status,
        "details": details,
        "response_time": response_time
    })

    if response_time > 0:
        test_results["response_times"].append(response_time)

    time_str = f" ({response_time*1000:.0f}ms)" if response_time > 0 else ""

    if status == "PASS":
        test_results["passed"] += 1
        print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {name}{time_str}")
    elif status == "FAIL":
        test_results["failed"] += 1
        print(f"  {Colors.RED}[FAIL]{Colors.RESET} {name}: {details}{time_str}")
    else:
        test_results["warnings"] += 1
        print(f"  {Colors.YELLOW}[WARN]{Colors.RESET} {name}: {details}{time_str}")

def print_header(title: str):
    """Imprime un encabezado de sección"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{title}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

# ============================================
# FASE 1: FRONTEND VERCEL ACCESS
# ============================================
def test_frontend_access():
    print_header("FASE 1: FRONTEND VERCEL ACCESS")

    # Test 1.1: Acceso al frontend
    print("1.1. Accediendo al frontend de Vercel...")
    try:
        start = time.time()
        response = requests.get(PROD_URL, timeout=30)
        elapsed = time.time() - start

        if response.status_code == 200:
            log_test("frontend", "Vercel Frontend Access", "PASS", f"Status: {response.status_code}", elapsed)
            content_length = len(response.content)
            print(f"     Content length: {content_length} bytes")
            print(f"     Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        else:
            log_test("frontend", "Vercel Frontend Access", "FAIL", f"Status: {response.status_code}", elapsed)
    except Exception as e:
        log_test("frontend", "Vercel Frontend Access", "FAIL", str(e))

    # Test 1.2: Headers de seguridad
    print("\n1.2. Verificando headers de seguridad...")
    try:
        response = requests.get(PROD_URL, timeout=30)
        headers = dict(response.headers)

        security_checks = {
            "X-Frame-Options": "Clickjacking protection",
            "X-Content-Type-Options": "MIME sniffing protection",
            "Strict-Transport-Security": "HSTS",
            "X-XSS-Protection": "XSS protection"
        }

        found = 0
        for header, description in security_checks.items():
            if header in headers:
                found += 1
                print(f"     {Colors.GREEN}[+]{Colors.RESET} {header}: {description}")

        log_test("frontend", "Security Headers", "PASS" if found >= 2 else "WARN", f"Found {found}/4 security headers")
    except Exception as e:
        log_test("frontend", "Security Headers", "WARN", str(e))

# ============================================
# FASE 2: API PROXY & BACKEND CONNECTIVITY
# ============================================
def test_api_connectivity():
    print_header("FASE 2: API PROXY & BACKEND CONNECTIVITY")

    # Test 2.1: Status endpoint through Vercel proxy
    print("2.1. API Status a través de proxy Vercel...")
    try:
        start = time.time()
        response = requests.get(f"{PROD_URL}/api/status", timeout=30)
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            log_test("api", "API Status via Proxy", "PASS", f"Status: {data.get('status', 'unknown')}", elapsed)
            print(f"     Response: {json.dumps(data, indent=2)}")
        else:
            log_test("api", "API Status via Proxy", "FAIL", f"Status: {response.status_code}", elapsed)
    except Exception as e:
        log_test("api", "API Status via Proxy", "FAIL", str(e))

    # Test 2.2: Direct backend IP access
    print("\n2.2. Acceso directo al backend Oracle Cloud...")
    try:
        start = time.time()
        response = requests.get(f"{BACKEND_IP}/api/status", timeout=30, verify=False)
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            log_test("api", "Direct Backend Access", "PASS", f"Status: {data.get('status', 'unknown')}", elapsed)
        else:
            log_test("api", "Direct Backend Access", "WARN", f"Status: {response.status_code}", elapsed)
    except Exception as e:
        log_test("api", "Direct Backend Access", "WARN", str(e))

    # Test 2.3: System Info
    print("\n2.3. System Info del backend...")
    try:
        start = time.time()
        response = requests.get(f"{PROD_URL}/api/system/info", timeout=30)
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            log_test("api", "System Info", "PASS", "", elapsed)
            print(f"     Python: {data.get('python_version', 'N/A')}")
            print(f"     Platform: {data.get('platform', 'N/A')}")
            print(f"     Uptime: {data.get('uptime', 'N/A')}")
        else:
            log_test("api", "System Info", "WARN", f"Status: {response.status_code}", elapsed)
    except Exception as e:
        log_test("api", "System Info", "WARN", str(e))

# ============================================
# FASE 3: CORS CONFIGURATION
# ============================================
def test_cors_configuration():
    print_header("FASE 3: CORS CONFIGURATION")

    # Test 3.1: Preflight OPTIONS request
    print("3.1. Verificando CORS Preflight...")
    try:
        headers = {
            "Origin": "https://app-eta-fawn-42.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }

        response = requests.options(f"{PROD_URL}/api/architect/generate", headers=headers, timeout=30)

        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }

        if cors_headers["Access-Control-Allow-Origin"]:
            log_test("cors", "CORS Preflight", "PASS", f"Origin: {cors_headers['Access-Control-Allow-Origin']}")
            print(f"     Methods: {cors_headers['Access-Control-Allow-Methods']}")
            print(f"     Headers: {cors_headers['Access-Control-Allow-Headers']}")
        else:
            log_test("cors", "CORS Preflight", "WARN", "No CORS headers found")
    except Exception as e:
        log_test("cors", "CORS Preflight", "WARN", str(e))

    # Test 3.2: Cross-origin request
    print("\n3.2. Verificando petición cross-origin...")
    try:
        headers = {"Origin": "https://app-eta-fawn-42.vercel.app"}
        response = requests.get(f"{PROD_URL}/api/status", headers=headers, timeout=30)

        acao = response.headers.get("Access-Control-Allow-Origin")
        if acao:
            log_test("cors", "Cross-Origin GET", "PASS", f"Allow-Origin: {acao}")
        else:
            log_test("cors", "Cross-Origin GET", "WARN", "No Allow-Origin header")
    except Exception as e:
        log_test("cors", "Cross-Origin GET", "WARN", str(e))

# ============================================
# FASE 4: API ENDPOINTS AVAILABILITY
# ============================================
def test_endpoints_availability():
    print_header("FASE 4: API ENDPOINTS AVAILABILITY")

    endpoints = [
        ("/api/status", "Status Endpoint"),
        ("/api/system/info", "System Info"),
        ("/api/architect/history", "Architect History"),
        ("/api/metrics", "Metrics"),
        ("/api/documentation", "Documentation"),
        ("/api/transparency/history", "Transparency History")
    ]

    for endpoint, description in endpoints:
        try:
            start = time.time()
            response = requests.get(f"{PROD_URL}{endpoint}", timeout=30)
            elapsed = time.time() - start

            if response.status_code == 200:
                log_test("endpoints", description, "PASS", "", elapsed)
            elif response.status_code == 404:
                log_test("endpoints", description, "WARN", "Not found (404)", elapsed)
            else:
                log_test("endpoints", description, "WARN", f"Status: {response.status_code}", elapsed)
        except Exception as e:
            log_test("endpoints", description, "WARN", str(e))

# ============================================
# FASE 5: ARCHITECT API TEST
# ============================================
def test_architect_api():
    print_header("FASE 5: ARCHITECT API PRODUCTION TEST")

    # Test 5.1: Generación de arquitectura simple
    print("5.1. Generando arquitectura en producción...")

    architect_payload = {
        "use_case": "Create a simple REST API for managing todo items with CRUD operations",
        "domain": "web",
        "complexity": "simple",
        "model": "gemini-2.0-flash-exp"
    }

    try:
        start = time.time()
        response = requests.post(f"{PROD_URL}/api/architect/generate", json=architect_payload, timeout=120)
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            payload_id = data.get("payload_id")

            if payload_id:
                log_test("architect", "Architect Generation", "PASS", f"Payload ID: {payload_id}", elapsed)

                # Test 5.2: Recuperar payload
                print("\n5.2. Recuperando payload generado...")
                get_start = time.time()
                get_response = requests.get(f"{PROD_URL}/api/architect/payload/{payload_id}", timeout=30)
                get_elapsed = time.time() - get_start

                if get_response.status_code == 200:
                    payload_data = get_response.json()
                    log_test("architect", "Payload Retrieval", "PASS", "", get_elapsed)

                    prd = payload_data.get("prd", {})
                    if prd:
                        print(f"     PRD components: {len(prd.get('components', []))}")
                else:
                    log_test("architect", "Payload Retrieval", "FAIL", f"Status: {get_response.status_code}", get_elapsed)
            else:
                log_test("architect", "Architect Generation", "WARN", "No payload_id returned", elapsed)
        else:
            log_test("architect", "Architect Generation", "FAIL", f"Status: {response.status_code}", elapsed)
    except Exception as e:
        log_test("architect", "Architect Generation", "FAIL", str(e))

# ============================================
# FASE 6: PERFORMANCE & LOAD
# ============================================
def test_performance():
    print_header("FASE 6: PERFORMANCE & RESPONSE TIMES")

    # Test 6.1: Tiempo de respuesta múltiple
    print("6.1. Midiendo tiempos de respuesta (5 iteraciones)...")

    response_times = []
    for i in range(5):
        try:
            start = time.time()
            response = requests.get(f"{PROD_URL}/api/status", timeout=30)
            elapsed = time.time() - start
            response_times.append(elapsed)
            print(f"     Iteration {i+1}: {elapsed*1000:.0f}ms")
        except:
            pass

    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)

        print(f"\n     Average: {avg_time*1000:.0f}ms")
        print(f"     Min: {min_time*1000:.0f}ms")
        print(f"     Max: {max_time*1000:.0f}ms")

        if avg_time < 2:
            log_test("performance", "Response Time", "PASS", f"Average: {avg_time*1000:.0f}ms (excellent)")
        elif avg_time < 5:
            log_test("performance", "Response Time", "PASS", f"Average: {avg_time*1000:.0f}ms (good)")
        else:
            log_test("performance", "Response Time", "WARN", f"Average: {avg_time*1000:.0f}ms (slow)")
    else:
        log_test("performance", "Response Time", "FAIL", "No successful requests")

    # Test 6.2: Concurrent requests simulation
    print("\n6.2. Simulando peticiones concurrentes...")
    try:
        import concurrent.futures

        def make_request():
            try:
                start = time.time()
                r = requests.get(f"{PROD_URL}/api/status", timeout=30)
                return time.time() - start, r.status_code
            except:
                return None, None

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        successful = sum(1 for r, s in results if s == 200)
        log_test("performance", "Concurrent Requests", "PASS" if successful >= 8 else "WARN", f"{successful}/10 successful")
    except Exception as e:
        log_test("performance", "Concurrent Requests", "WARN", str(e))

# ============================================
# FASE 7: ERROR HANDLING IN PRODUCTION
# ============================================
def test_error_handling():
    print_header("FASE 7: ERROR HANDLING IN PRODUCTION")

    # Test 7.1: 404 Handling
    print("7.1. Verificando manejo de 404...")
    try:
        response = requests.get(f"{PROD_URL}/api/nonexistent", timeout=30)
        if response.status_code == 404:
            log_test("errors", "404 Error Handling", "PASS", "Correctly returns 404")
        elif response.status_code == 500:
            log_test("errors", "404 Error Handling", "WARN", "Returns 500 instead of 404")
        else:
            log_test("errors", "404 Error Handling", "WARN", f"Unexpected status: {response.status_code}")
    except Exception as e:
        log_test("errors", "404 Error Handling", "WARN", str(e))

    # Test 7.2: Invalid JSON handling
    print("\n7.2. Verificando manejo de JSON inválido...")
    try:
        response = requests.post(
            f"{PROD_URL}/api/architect/generate",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code in [400, 422]:
            log_test("errors", "Invalid JSON Handling", "PASS", "Correctly rejected invalid JSON")
        else:
            log_test("errors", "Invalid JSON Handling", "WARN", f"Status: {response.status_code}")
    except Exception as e:
        log_test("errors", "Invalid JSON Handling", "WARN", str(e))

    # Test 7.3: Rate limiting check
    print("\n7.3. Verificando rate limiting...")
    try:
        # Hacer múltiples peticiones rápidas
        statuses = []
        for _ in range(15):
            r = requests.get(f"{PROD_URL}/api/status", timeout=30)
            statuses.append(r.status_code)

        if 429 in statuses:  # Too Many Requests
            log_test("errors", "Rate Limiting", "PASS", "Rate limiting active")
        else:
            log_test("errors", "Rate Limiting", "WARN", "No rate limiting detected (or not triggered)")
    except Exception as e:
        log_test("errors", "Rate Limiting", "WARN", str(e))

# ============================================
# MAIN
# ============================================
def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("=" * 70)
    print("    GEM TRINITY GENESIS - PRUEBA DIFICIL PRODUCCION")
    print("         URL: https://app-eta-fawn-42.vercel.app")
    print("         Backend: Oracle Cloud (100.69.240.73)")
    print("=" * 70)
    print(f"{Colors.RESET}")

    start_time = time.time()

    # Ejecutar todas las fases
    test_frontend_access()
    test_api_connectivity()
    test_cors_configuration()
    test_endpoints_availability()
    test_architect_api()
    test_performance()
    test_error_handling()

    # Resumen final
    elapsed = time.time() - start_time

    print_header("RESUMEN DE RESULTADOS - PRODUCCION")

    total = test_results["passed"] + test_results["failed"] + test_results["warnings"]

    print(f"{Colors.BOLD}Total Pruebas:{Colors.RESET} {total}")
    print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {test_results['passed']}")
    print(f"  {Colors.RED}[FAIL]{Colors.RESET} {test_results['failed']}")
    print(f"  {Colors.YELLOW}[WARN]{Colors.RESET} {test_results['warnings']}")
    print(f"\nTiempo total: {elapsed:.2f} segundos")

    # Análisis de performance
    if test_results["response_times"]:
        avg_response = sum(test_results["response_times"]) / len(test_results["response_times"])
        print(f"\n{Colors.BOLD}Performance:{Colors.RESET}")
        print(f"  Tiempo promedio de respuesta: {avg_response*1000:.0f}ms")

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
    print_header("VEREDICTO FINAL - PRODUCCION")

    critical_failures = sum(1 for t in test_results["tests"] if t["status"] == "FAIL" and t["category"] in ["api", "frontend"])

    if critical_failures == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}[PRODUCCION OPERATIVA]{Colors.RESET}")
        print(f"{Colors.GREEN}El despliegue en producción funciona correctamente.{Colors.RESET}")
        print(f"{Colors.GREEN}Frontend Vercel -> Backend Oracle Cloud: OK{Colors.RESET}\n")
        return 0
    elif test_results["failed"] <= 3:
        print(f"{Colors.YELLOW}{Colors.BOLD}[PRODUCCION PARCIAL]{Colors.RESET}")
        print(f"{Colors.YELLOW}Algunas pruebas fallaron pero el servicio es funcional.{Colors.RESET}")
        print(f"{Colors.YELLOW}Revisar endpoints críticos.{Colors.RESET}\n")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}[PRODUCCION CRITICA]{Colors.RESET}")
        print(f"{Colors.RED}Múltiples pruebas fallaron en producción.{Colors.RESET}")
        print(f"{Colors.RED}Se requiere intervención urgente.{Colors.RESET}\n")
        return 2

if __name__ == "__main__":
    sys.exit(main())
