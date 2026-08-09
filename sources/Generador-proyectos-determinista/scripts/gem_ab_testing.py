"""
Gem A/B Testing - Comparación de rendimiento entre versiones de Gems

Features:
- Ejecutar mismo prompt con diferentes versiones
- Medir métricas (latencia, tokens, calidad)
- Comparación estadística
- Selección automática de winner
- Reportes de A/B test
"""
import json
import time
import hashlib
import statistics
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field


@dataclass
class ABTestConfig:
    """Configuración de un A/B test"""
    name: str
    gem_a: str  # Path o nombre del gem A
    gem_b: str  # Path o nombre del gem B
    test_prompts: List[str]  # Prompts de prueba
    metrics: List[str] = field(default_factory=lambda: ["latency", "tokens", "quality"])
    iterations: int = 3  # Iteraciones por prompt
    quality_evaluator: Optional[str] = None  # Función de evaluación


@dataclass
class ABTestResult:
    """Resultado individual de una ejecución"""
    gem_id: str
    prompt: str
    iteration: int
    latency_ms: float
    tokens_input: int
    tokens_output: int
    response: str
    quality_score: float = 0.0
    error: Optional[str] = None


@dataclass
class ABTestSummary:
    """Resumen comparativo del A/B test"""
    test_name: str
    gem_a_name: str
    gem_b_name: str
    winner: str
    
    # Métricas A
    a_avg_latency: float
    a_avg_tokens: float
    a_avg_quality: float
    
    # Métricas B
    b_avg_latency: float
    b_avg_tokens: float
    b_avg_quality: float
    
    # Diferencias
    latency_diff_pct: float
    tokens_diff_pct: float
    quality_diff_pct: float
    
    total_iterations: int
    completed_at: str


class GemABTesting:
    """Sistema de A/B Testing para Gems"""
    
    def __init__(self, gems_dir: str = None, results_dir: str = None):
        """
        Args:
            gems_dir: Directorio de Gems
            results_dir: Directorio para guardar resultados
        """
        if gems_dir is None:
            gems_dir = Path(__file__).parent.parent / "gems"
        
        self.gems_dir = Path(gems_dir)
        
        if results_dir is None:
            results_dir = self.gems_dir / ".ab_tests"
        
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def create_test(
        self,
        name: str,
        gem_a: str,
        gem_b: str,
        test_prompts: List[str],
        iterations: int = 3
    ) -> ABTestConfig:
        """
        Crea configuración de A/B test.
        
        Args:
            name: Nombre del test
            gem_a: Gem versión A
            gem_b: Gem versión B
            test_prompts: Prompts de prueba
            iterations: Iteraciones por prompt
        
        Returns:
            ABTestConfig
        """
        config = ABTestConfig(
            name=name,
            gem_a=gem_a,
            gem_b=gem_b,
            test_prompts=test_prompts,
            iterations=iterations
        )
        
        # Guardar configuración
        config_file = self.results_dir / f"{name}_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump({
                "name": config.name,
                "gem_a": config.gem_a,
                "gem_b": config.gem_b,
                "test_prompts": config.test_prompts,
                "iterations": config.iterations,
                "metrics": config.metrics,
                "created_at": datetime.now(timezone.utc).isoformat()
            }, f, indent=2)
        
        return config
    
    def _load_gem(self, gem_id: str) -> Optional[Dict]:
        """Carga un Gem Bundle"""
        # Intentar como path absoluto
        gem_path = Path(gem_id)
        if not gem_path.exists():
            # Intentar en gems_dir
            gem_path = self.gems_dir / f"{gem_id}.json"
            if not gem_path.exists():
                # Buscar con patrón
                matches = list(self.gems_dir.glob(f"{gem_id}*.json"))
                if matches:
                    gem_path = matches[0]
                else:
                    return None
        
        with open(gem_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _simulate_execution(
        self,
        gem: Dict,
        prompt: str
    ) -> Tuple[float, int, int, str]:
        """
        Simula ejecución de un prompt con un Gem.
        En producción, esto llamaría al LLM real.
        
        Returns:
            Tuple (latency_ms, tokens_input, tokens_output, response)
        """
        # Simulación para testing
        # En producción, aquí iría la llamada real al modelo
        
        start_time = time.time()
        
        # Simular procesamiento basado en risk_score
        risk_score = gem.get("bundle_meta", {}).get("risk_score", 50)
        model = gem.get("model_routing", {}).get("default_model", "gemini-flash")
        
        # Simular latencia basada en modelo
        base_latency = 500 if model == "gemini-flash" else 1500
        # Añadir variabilidad
        import random
        latency_ms = base_latency + random.randint(-100, 200)
        
        # Simular tokens
        tokens_input = len(prompt.split()) * 2  # Aproximación
        tokens_output = 50 + random.randint(10, 100)
        
        # Simular respuesta
        response = f"[Simulated response for: {prompt[:50]}...]"
        
        # Simular tiempo real
        time.sleep(0.1)  # 100ms mínimo
        
        return latency_ms, tokens_input, tokens_output, response
    
    def _evaluate_quality(
        self,
        prompt: str,
        response: str,
        gem: Dict
    ) -> float:
        """
        Evalúa calidad de respuesta.
        En producción, esto podría usar otro LLM como juez.
        
        Returns:
            Score de 0 a 1
        """
        # Simulación simple basada en longitud y risk_score
        # En producción, usar LLM-as-judge o métricas reales
        
        response_quality = min(1.0, len(response) / 200)
        risk_penalty = gem.get("bundle_meta", {}).get("risk_score", 50) / 200
        
        return max(0, min(1, response_quality - risk_penalty + 0.5))
    
    def run_test(
        self,
        config: ABTestConfig,
        progress_callback: Callable[[int, int], None] = None
    ) -> ABTestSummary:
        """
        Ejecuta un A/B test.
        
        Args:
            config: Configuración del test
            progress_callback: Función para reportar progreso
        
        Returns:
            ABTestSummary con resultados
        """
        # Cargar gems
        gem_a = self._load_gem(config.gem_a)
        gem_b = self._load_gem(config.gem_b)
        
        if not gem_a or not gem_b:
            raise ValueError("No se pudieron cargar los gems")
        
        results_a: List[ABTestResult] = []
        results_b: List[ABTestResult] = []
        
        total_runs = len(config.test_prompts) * config.iterations * 2
        current_run = 0
        
        # Ejecutar tests
        for prompt in config.test_prompts:
            for iteration in range(config.iterations):
                # Test A
                latency, tok_in, tok_out, response = self._simulate_execution(gem_a, prompt)
                quality = self._evaluate_quality(prompt, response, gem_a)
                
                results_a.append(ABTestResult(
                    gem_id=config.gem_a,
                    prompt=prompt,
                    iteration=iteration,
                    latency_ms=latency,
                    tokens_input=tok_in,
                    tokens_output=tok_out,
                    response=response,
                    quality_score=quality
                ))
                
                current_run += 1
                if progress_callback:
                    progress_callback(current_run, total_runs)
                
                # Test B
                latency, tok_in, tok_out, response = self._simulate_execution(gem_b, prompt)
                quality = self._evaluate_quality(prompt, response, gem_b)
                
                results_b.append(ABTestResult(
                    gem_id=config.gem_b,
                    prompt=prompt,
                    iteration=iteration,
                    latency_ms=latency,
                    tokens_input=tok_in,
                    tokens_output=tok_out,
                    response=response,
                    quality_score=quality
                ))
                
                current_run += 1
                if progress_callback:
                    progress_callback(current_run, total_runs)
        
        # Calcular métricas
        a_latencies = [r.latency_ms for r in results_a]
        b_latencies = [r.latency_ms for r in results_b]
        
        a_tokens = [r.tokens_output for r in results_a]
        b_tokens = [r.tokens_output for r in results_b]
        
        a_quality = [r.quality_score for r in results_a]
        b_quality = [r.quality_score for r in results_b]
        
        a_avg_latency = statistics.mean(a_latencies)
        b_avg_latency = statistics.mean(b_latencies)
        
        a_avg_tokens = statistics.mean(a_tokens)
        b_avg_tokens = statistics.mean(b_tokens)
        
        a_avg_quality = statistics.mean(a_quality)
        b_avg_quality = statistics.mean(b_quality)
        
        # Calcular diferencias
        latency_diff = ((b_avg_latency - a_avg_latency) / a_avg_latency) * 100 if a_avg_latency else 0
        tokens_diff = ((b_avg_tokens - a_avg_tokens) / a_avg_tokens) * 100 if a_avg_tokens else 0
        quality_diff = ((b_avg_quality - a_avg_quality) / a_avg_quality) * 100 if a_avg_quality else 0
        
        # Determinar winner (menor latencia, menor tokens, mayor quality)
        score_a = (-a_avg_latency / 1000) + (-a_avg_tokens / 100) + (a_avg_quality * 10)
        score_b = (-b_avg_latency / 1000) + (-b_avg_tokens / 100) + (b_avg_quality * 10)
        
        winner = config.gem_a if score_a > score_b else config.gem_b
        
        summary = ABTestSummary(
            test_name=config.name,
            gem_a_name=config.gem_a,
            gem_b_name=config.gem_b,
            winner=winner,
            a_avg_latency=a_avg_latency,
            a_avg_tokens=a_avg_tokens,
            a_avg_quality=a_avg_quality,
            b_avg_latency=b_avg_latency,
            b_avg_tokens=b_avg_tokens,
            b_avg_quality=b_avg_quality,
            latency_diff_pct=latency_diff,
            tokens_diff_pct=tokens_diff,
            quality_diff_pct=quality_diff,
            total_iterations=len(results_a) + len(results_b),
            completed_at=datetime.now(timezone.utc).isoformat()
        )
        
        # Guardar resultados
        self._save_results(config.name, summary, results_a, results_b)
        
        return summary
    
    def _save_results(
        self,
        test_name: str,
        summary: ABTestSummary,
        results_a: List[ABTestResult],
        results_b: List[ABTestResult]
    ):
        """Guarda resultados del test"""
        result_file = self.results_dir / f"{test_name}_results.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "test_name": summary.test_name,
                    "winner": summary.winner,
                    "gem_a": {
                        "name": summary.gem_a_name,
                        "avg_latency_ms": summary.a_avg_latency,
                        "avg_tokens": summary.a_avg_tokens,
                        "avg_quality": summary.a_avg_quality
                    },
                    "gem_b": {
                        "name": summary.gem_b_name,
                        "avg_latency_ms": summary.b_avg_latency,
                        "avg_tokens": summary.b_avg_tokens,
                        "avg_quality": summary.b_avg_quality
                    },
                    "differences_pct": {
                        "latency": summary.latency_diff_pct,
                        "tokens": summary.tokens_diff_pct,
                        "quality": summary.quality_diff_pct
                    },
                    "total_iterations": summary.total_iterations,
                    "completed_at": summary.completed_at
                },
                "raw_results_a": [
                    {
                        "prompt": r.prompt[:100],
                        "iteration": r.iteration,
                        "latency_ms": r.latency_ms,
                        "tokens_output": r.tokens_output,
                        "quality_score": r.quality_score
                    }
                    for r in results_a
                ],
                "raw_results_b": [
                    {
                        "prompt": r.prompt[:100],
                        "iteration": r.iteration,
                        "latency_ms": r.latency_ms,
                        "tokens_output": r.tokens_output,
                        "quality_score": r.quality_score
                    }
                    for r in results_b
                ]
            }, f, indent=2)
    
    def list_tests(self) -> List[Dict]:
        """Lista tests ejecutados"""
        tests = []
        
        for result_file in self.results_dir.glob("*_results.json"):
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            summary = data.get("summary", {})
            tests.append({
                "name": summary.get("test_name", result_file.stem),
                "winner": summary.get("winner", "unknown"),
                "completed_at": summary.get("completed_at", ""),
                "gem_a": summary.get("gem_a", {}).get("name", ""),
                "gem_b": summary.get("gem_b", {}).get("name", "")
            })
        
        return tests
    
    def get_test_result(self, test_name: str) -> Optional[Dict]:
        """Obtiene resultados de un test específico"""
        result_file = self.results_dir / f"{test_name}_results.json"
        
        if not result_file.exists():
            return None
        
        with open(result_file, 'r', encoding='utf-8') as f:
            return json.load(f)


# CLI para testing standalone
if __name__ == "__main__":
    import sys
    
    ab_tester = GemABTesting()
    
    print("\n" + "="*60)
    print("  GEM A/B TESTING")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nComandos:")
        print("  run <name> <gem_a> <gem_b>  - Ejecutar nuevo test")
        print("  list                         - Listar tests")
        print("  show <name>                  - Ver resultados de test")
    else:
        cmd = sys.argv[1]
        
        if cmd == "list":
            tests = ab_tester.list_tests()
            print(f"\nTests ejecutados ({len(tests)}):")
            for t in tests:
                print(f"  - {t['name']}: {t['gem_a']} vs {t['gem_b']}")
                print(f"    Winner: {t['winner']}")
        
        elif cmd == "show" and len(sys.argv) > 2:
            result = ab_tester.get_test_result(sys.argv[2])
            if result:
                summary = result.get("summary", {})
                print(f"\n📊 Resultados: {summary.get('test_name')}")
                print(f"\n🏆 Winner: {summary.get('winner')}")
                print(f"\nGem A ({summary.get('gem_a', {}).get('name')}):")
                print(f"  Latency: {summary.get('gem_a', {}).get('avg_latency_ms', 0):.1f}ms")
                print(f"  Tokens: {summary.get('gem_a', {}).get('avg_tokens', 0):.1f}")
                print(f"  Quality: {summary.get('gem_a', {}).get('avg_quality', 0):.2f}")
                print(f"\nGem B ({summary.get('gem_b', {}).get('name')}):")
                print(f"  Latency: {summary.get('gem_b', {}).get('avg_latency_ms', 0):.1f}ms")
                print(f"  Tokens: {summary.get('gem_b', {}).get('avg_tokens', 0):.1f}")
                print(f"  Quality: {summary.get('gem_b', {}).get('avg_quality', 0):.2f}")
            else:
                print(f"Test '{sys.argv[2]}' no encontrado")
        
        elif cmd == "run" and len(sys.argv) > 4:
            name = sys.argv[2]
            gem_a = sys.argv[3]
            gem_b = sys.argv[4]
            
            config = ab_tester.create_test(
                name=name,
                gem_a=gem_a,
                gem_b=gem_b,
                test_prompts=[
                    "Analiza este documento y genera un resumen",
                    "Lista los puntos clave del texto",
                    "Identifica las acciones pendientes"
                ]
            )
            
            print(f"\nEjecutando A/B test: {name}")
            print(f"  Gem A: {gem_a}")
            print(f"  Gem B: {gem_b}")
            
            def progress(current, total):
                pct = (current / total) * 100
                print(f"\r  Progreso: {current}/{total} ({pct:.0f}%)", end="")
            
            summary = ab_tester.run_test(config, progress)
            
            print(f"\n\n🏆 Winner: {summary.winner}")
            print(f"  Latency diff: {summary.latency_diff_pct:+.1f}%")
            print(f"  Quality diff: {summary.quality_diff_pct:+.1f}%")
