"""
Risk Engine - Fase 2 del Pipeline Gem Builder

Calcula el Risk Score (0-100) basado en:
- Sensibilidad de datos (PII, financial, etc.)
- Side-effects de acciones
- Complejidad del caso de uso
- Acceso a herramientas con permisos elevados

El Risk Score determina políticas automáticas:
- 0-30 (LOW): Model Armor OFF, HITL opcional
- 31-60 (MEDIUM): Model Armor ON, HITL sugerido
- 61-100 (HIGH): Model Armor ON, HITL obligatorio, Read-only tools
"""
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class RiskAssessment:
    """Resultado del análisis de riesgo"""
    score: int
    level: str  # LOW, MEDIUM, HIGH
    factors: Dict[str, int]  # Breakdown del score
    recommendations: list  # Recomendaciones de seguridad
    
    @property
    def model_armor_enabled(self) -> bool:
        return self.score > 30
    
    @property
    def hitl_required(self) -> bool:
        return self.score > 60
    
    @property
    def read_only_recommended(self) -> bool:
        return self.score > 70


class RiskEngine:
    """Motor de cálculo de riesgo para Use Case Specs"""
    
    # Puntos base según sensibilidad de datos
    DATA_SENSITIVITY_SCORES = {
        'public': 0,
        'internal': 15,
        'confidential': 35,
        'financial': 55
    }
    
    # Puntos según tipo de acción
    ACTION_SCORES = {
        'read': 0,
        'analyze': 5,
        'summarize': 5,
        'transform': 15,
        'execute': 25,
        'write': 20
    }
    
    # Puntos adicionales por side-effects
    SIDE_EFFECTS_PENALTY = 15
    
    # Puntos por complejidad (número de data sources)
    COMPLEXITY_THRESHOLDS = [
        (2, 0),    # 1-2 sources: +0
        (5, 10),   # 3-5 sources: +10
        (10, 20),  # 6-10 sources: +20
        (999, 30)  # 11+: +30
    ]
    
    def calculate(self, spec: Dict) -> RiskAssessment:
        """
        Calcula el Risk Score de un Use Case Spec normalizado.
        
        Args:
            spec: Use Case Spec normalizado (output de IntakeValidator)
        
        Returns:
            RiskAssessment con score, nivel y recomendaciones
        """
        factors = {}
        recommendations = []
        
        # 1. Sensibilidad de datos
        data_score = self._calculate_data_sensitivity(spec)
        factors['data_sensitivity'] = data_score
        
        # 2. Riesgo de acciones
        action_score = self._calculate_action_risk(spec)
        factors['actions_risk'] = action_score
        
        # 3. Side-effects
        side_effects_score = self._calculate_side_effects(spec)
        factors['side_effects'] = side_effects_score
        
        # 4. Complejidad
        complexity_score = self._calculate_complexity(spec)
        factors['complexity'] = complexity_score
        
        # 5. Acceso a herramientas sensibles
        tools_score = self._calculate_tools_risk(spec)
        factors['tools_risk'] = tools_score
        
        # Calcular score total (capped at 100)
        total_score = min(100, sum(factors.values()))
        
        # Determinar nivel
        if total_score <= 30:
            level = 'LOW'
        elif total_score <= 60:
            level = 'MEDIUM'
        else:
            level = 'HIGH'
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(spec, total_score, factors)
        
        return RiskAssessment(
            score=total_score,
            level=level,
            factors=factors,
            recommendations=recommendations
        )
    
    def _calculate_data_sensitivity(self, spec: Dict) -> int:
        """Calcula score basado en sensibilidad de datos"""
        max_sensitivity = 0
        
        for ds in spec.get('data_sources', []):
            sensitivity = ds.get('sensitivity', 'internal')
            score = self.DATA_SENSITIVITY_SCORES.get(sensitivity, 15)
            max_sensitivity = max(max_sensitivity, score)
        
        return max_sensitivity
    
    def _calculate_action_risk(self, spec: Dict) -> int:
        """Calcula score basado en tipos de acciones"""
        max_action_risk = 0
        
        for action in spec.get('actions', []):
            action_type = action.get('type', 'read')
            score = self.ACTION_SCORES.get(action_type, 0)
            max_action_risk = max(max_action_risk, score)
        
        return max_action_risk
    
    def _calculate_side_effects(self, spec: Dict) -> int:
        """Calcula penalización por side-effects"""
        has_side_effects = any(
            action.get('side_effects', False)
            for action in spec.get('actions', [])
        )
        
        return self.SIDE_EFFECTS_PENALTY if has_side_effects else 0
    
    def _calculate_complexity(self, spec: Dict) -> int:
        """Calcula score basado en complejidad"""
        num_sources = len(spec.get('data_sources', []))
        num_actions = len(spec.get('actions', []))
        
        total_items = num_sources + num_actions
        
        for threshold, score in self.COMPLEXITY_THRESHOLDS:
            if total_items <= threshold:
                return score
        
        return 30  # Max complexity score
    
    def _calculate_tools_risk(self, spec: Dict) -> int:
        """Calcula score basado en herramientas requeridas"""
        high_risk_tools = {'execute', 'code_sandbox', 'database_write', 'deploy'}
        
        allowed_tools = spec.get('security', {}).get('allowed_tools', [])
        
        # Si no hay whitelist, asumir riesgo medio
        if not allowed_tools:
            return 5
        
        # Verificar si hay herramientas de alto riesgo
        for tool in allowed_tools:
            if tool.lower() in high_risk_tools:
                return 15
        
        return 0
    
    def _generate_recommendations(
        self, 
        spec: Dict, 
        score: int, 
        factors: Dict
    ) -> list:
        """Genera recomendaciones de seguridad basadas en el análisis"""
        recommendations = []
        
        # Recomendaciones según score
        if score > 60:
            recommendations.append("🔒 HITL obligatorio recomendado para este Risk Score")
            recommendations.append("🛡️ Model Armor debe estar habilitado")
        
        if score > 70:
            recommendations.append("📖 Considerar modo read-only para herramientas")
            recommendations.append("🔍 Añadir grounding obligatorio para facts")
        
        # Recomendaciones según factores específicos
        if factors.get('data_sensitivity', 0) >= 35:
            recommendations.append("💾 Datos sensibles detectados - considerar encryption at rest")
        
        if factors.get('side_effects', 0) > 0:
            recommendations.append("⚠️ Acciones con side-effects - implementar rollback strategy")
        
        if factors.get('actions_risk', 0) >= 20:
            recommendations.append("🔐 Acciones de alto riesgo - requiere dry-run antes de ejecución real")
        
        return recommendations


# CLI para testing standalone
if __name__ == "__main__":
    import json
    import sys
    
    # Ejemplo de spec para testing
    test_spec = {
        "use_case_id": "financial_analyzer",
        "goal": "Analizar transacciones financieras y generar reportes",
        "data_sources": [
            {"type": "db", "sensitivity": "financial", "access": "read"},
            {"type": "api", "sensitivity": "confidential", "access": "read"}
        ],
        "actions": [
            {"type": "analyze", "side_effects": False},
            {"type": "transform", "side_effects": False},
            {"type": "write", "side_effects": True}
        ],
        "security": {
            "allowed_tools": ["database", "filesystem"]
        }
    }
    
    engine = RiskEngine()
    assessment = engine.calculate(test_spec)
    
    print("\n" + "="*60)
    print("  RISK ASSESSMENT")
    print("="*60 + "\n")
    
    print(f"Risk Score: {assessment.score} ({assessment.level})")
    print(f"\nFactors:")
    for factor, score in assessment.factors.items():
        print(f"  - {factor}: +{score}")
    
    print(f"\nPolicies:")
    print(f"  - Model Armor: {'ON' if assessment.model_armor_enabled else 'OFF'}")
    print(f"  - HITL Required: {'YES' if assessment.hitl_required else 'NO'}")
    print(f"  - Read-Only Recommended: {'YES' if assessment.read_only_recommended else 'NO'}")
    
    print(f"\nRecommendations:")
    for rec in assessment.recommendations:
        print(f"  {rec}")
