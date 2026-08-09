"""
Model Router - Fase 3 del Pipeline Gem Builder

Selecciona el modelo óptimo basado en:
- Risk Score del caso de uso
- Requisitos de razonamiento (simple vs complejo)
- Restricciones de latencia
- Tipo de tareas (clasificación, generación, análisis)

Modelos disponibles:
- gemini-3-pro: Razonamiento profundo, code generation compleja
- gemini-flash: Latencia baja, tareas deterministas
"""
from typing import Dict
from dataclasses import dataclass


@dataclass
class RoutingDecision:
    """Decisión de routing del modelo"""
    model: str
    reason: str
    confidence: float  # 0-1
    fallback_model: str
    reasoning_mode: str  # "auto", "extended", "minimal"


class ModelRouter:
    """Router de modelos para Gem Builder"""
    
    # Umbrales de configuración
    HIGH_LATENCY_THRESHOLD = 5000  # ms
    LOW_LATENCY_THRESHOLD = 2000   # ms
    HIGH_RISK_THRESHOLD = 60
    
    # Tipos de acciones que requieren razonamiento profundo
    DEEP_REASONING_ACTIONS = {'execute', 'transform', 'analyze'}
    
    # Tipos de acciones simples (Flash-compatible)
    SIMPLE_ACTIONS = {'read', 'summarize'}
    
    def select(self, spec: Dict, risk_score: int) -> RoutingDecision:
        """
        Selecciona el modelo óptimo para el Use Case Spec.
        
        Args:
            spec: Use Case Spec normalizado
            risk_score: Risk Score del caso de uso (0-100)
        
        Returns:
            RoutingDecision con modelo seleccionado y justificación
        """
        # Extraer restricciones
        constraints = spec.get('constraints', {})
        latency_ms = constraints.get('latency_ms', 5000)
        cost_tier = constraints.get('cost_tier', 'medium')
        
        # Analizar acciones
        actions = [a.get('type') for a in spec.get('actions', [])]
        
        # Analizar sensibilidad de datos
        has_financial = any(
            ds.get('sensitivity') == 'financial'
            for ds in spec.get('data_sources', [])
        )
        
        has_confidential = any(
            ds.get('sensitivity') == 'confidential'
            for ds in spec.get('data_sources', [])
        )
        
        # Decisión basada en reglas
        
        # Regla 1: Financial data → Pro obligatorio
        if has_financial:
            return RoutingDecision(
                model="gemini-3-pro",
                reason="Datos financieros requieren razonamiento profundo y precisión",
                confidence=0.95,
                fallback_model="gemini-3-pro",  # Sin fallback
                reasoning_mode="extended"
            )
        
        # Regla 2: Alto riesgo → Pro recomendado
        if risk_score > self.HIGH_RISK_THRESHOLD:
            return RoutingDecision(
                model="gemini-3-pro",
                reason=f"Risk Score alto ({risk_score}) requiere modelo con mejor razonamiento",
                confidence=0.90,
                fallback_model="gemini-flash",
                reasoning_mode="extended"
            )
        
        # Regla 3: Acciones de razonamiento profundo → Pro
        if any(action in self.DEEP_REASONING_ACTIONS for action in actions):
            return RoutingDecision(
                model="gemini-3-pro",
                reason="Acciones de transformación/ejecución requieren razonamiento multi-step",
                confidence=0.85,
                fallback_model="gemini-flash",
                reasoning_mode="auto"
            )
        
        # Regla 4: Latencia baja + acciones simples → Flash
        if latency_ms < self.LOW_LATENCY_THRESHOLD:
            if all(action in self.SIMPLE_ACTIONS for action in actions):
                return RoutingDecision(
                    model="gemini-flash",
                    reason=f"Latencia baja ({latency_ms}ms) con acciones simples",
                    confidence=0.90,
                    fallback_model="gemini-3-pro",
                    reasoning_mode="minimal"
                )
        
        # Regla 5: Cost tier bajo + sin datos sensibles → Flash
        if cost_tier == 'low' and not has_confidential:
            return RoutingDecision(
                model="gemini-flash",
                reason="Cost tier bajo sin datos sensibles permite Flash",
                confidence=0.80,
                fallback_model="gemini-3-pro",
                reasoning_mode="auto"
            )
        
        # Default: Pro para calidad
        return RoutingDecision(
            model="gemini-3-pro",
            reason="Default: Pro para máxima calidad y precisión",
            confidence=0.70,
            fallback_model="gemini-flash",
            reasoning_mode="auto"
        )
    
    def get_model_config(self, decision: RoutingDecision) -> Dict:
        """
        Genera configuración del modelo para el Gem Bundle.
        
        Args:
            decision: Decisión de routing
        
        Returns:
            Dict con configuración del modelo
        """
        return {
            "default_model": decision.model,
            "fallback_model": decision.fallback_model,
            "reasoning_mode": decision.reasoning_mode,
            "routing_reason": decision.reason,
            "routing_confidence": decision.confidence,
            "model_requirements": {
                "extended_thinking": decision.reasoning_mode == "extended",
                "streaming": True,
                "temperature": 0.1 if decision.model == "gemini-3-pro" else 0.3
            }
        }


# CLI para testing standalone
if __name__ == "__main__":
    import json
    
    # Ejemplo 1: Caso financiero (debe elegir Pro)
    financial_spec = {
        "use_case_id": "financial_analyzer",
        "data_sources": [{"type": "db", "sensitivity": "financial"}],
        "actions": [{"type": "analyze"}],
        "constraints": {"latency_ms": 5000, "cost_tier": "high"}
    }
    
    # Ejemplo 2: Caso simple (debe elegir Flash)
    simple_spec = {
        "use_case_id": "document_reader",
        "data_sources": [{"type": "file", "sensitivity": "public"}],
        "actions": [{"type": "read"}, {"type": "summarize"}],
        "constraints": {"latency_ms": 1500, "cost_tier": "low"}
    }
    
    router = ModelRouter()
    
    print("\n" + "="*60)
    print("  MODEL ROUTER TESTS")
    print("="*60)
    
    # Test 1
    print("\n[1] Financial Analyzer:")
    decision1 = router.select(financial_spec, risk_score=75)
    print(f"  Model: {decision1.model}")
    print(f"  Reason: {decision1.reason}")
    print(f"  Confidence: {decision1.confidence}")
    print(f"  Reasoning Mode: {decision1.reasoning_mode}")
    
    # Test 2
    print("\n[2] Document Reader:")
    decision2 = router.select(simple_spec, risk_score=15)
    print(f"  Model: {decision2.model}")
    print(f"  Reason: {decision2.reason}")
    print(f"  Confidence: {decision2.confidence}")
    print(f"  Reasoning Mode: {decision2.reasoning_mode}")
