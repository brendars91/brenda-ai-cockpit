"""
Gem Builder CLI - Compilador Determinista de Agentes

Punto de entrada principal del compilador. Orquesta el pipeline de 6 fases.

Uso:
    python cli.py compile --spec specs/my_use_case.json
    python cli.py validate --spec specs/my_use_case.json
    python cli.py validate --bundle bundles/my_gem_v1.0.0.json
    python cli.py version
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Importar componentes del pipeline
from intake_validator import IntakeValidator
from risk_engine import RiskEngine
from model_router import ModelRouter
from tool_planner import ToolPlanner
from prompt_compiler import PromptCompiler
from verifier_gate import VerifierGate


import subprocess

class Colors:
    """ANSI color codes para terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def log_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")


def log_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")


def log_warn(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")


def log_info(msg):
    print(f"{Colors.CYAN}ℹ{Colors.RESET} {msg}")


def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")


def cmd_update(args):
    """
    Auto-actualiza Gem Builder desde el repositorio remoto.
    """
    print_header("GEM BUILDER AUTO-UPDATE")
    log_info("Checking for updates...")
    
    try:
        # Check remote
        subprocess.check_call(["git", "fetch"], cwd=Path(__file__).parent.parent)
        status = subprocess.check_output(
            ["git", "rev-list", "HEAD...origin/main", "--count"], 
            cwd=Path(__file__).parent.parent
        ).decode().strip()
        
        if int(status) == 0:
            log_success("Gem Builder is already up to date.")
            return

        log_warn(f"Found {status} new commits. Updating...")
        
        # Pull
        subprocess.check_call(["git", "pull"], cwd=Path(__file__).parent.parent)
        log_success("Successfully updated source code.")
        
        # Validar dependencias (simplificado)
        # subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        log_success("Update complete! Please restart any running instances.")
        
    except Exception as e:
        log_error(f"Failed to update: {e}")
        sys.exit(1)


def cmd_compile(args):
    """
    Compila un Use Case Spec en un Gem Bundle.
    
    Pipeline:
    1. Intake & Validation
    2. Risk Engine
    3. Model Router
    4. Tool Planner
    5. Prompt Compiler
    6. Verifier Gate
    """
    print_header("GEM BUILDER COMPILER")
    
    spec_path = args.spec
    output_path = args.output
    dry_run = args.dry_run
    verbose = args.verbose
    
    log_info(f"Input: {spec_path}")
    
    # FASE 1: Intake & Validation
    print(f"\n{Colors.BOLD}[1/6] Intake & Validation{Colors.RESET}")
    
    validator = IntakeValidator()
    is_valid, normalized_spec, errors = validator.validate(spec_path)
    
    if not is_valid:
        log_error("Spec validation failed")
        for error in errors:
            print(f"  - {error}")
        
        # Preguntas FALTAN_DATOS
        if normalized_spec:
            questions = validator.get_missing_data_questions(normalized_spec)
            if questions:
                print(f"\n{Colors.YELLOW}FALTAN_DATOS - Completar:{Colors.RESET}")
                for q in questions:
                    print(f"  ? {q}")
        
        sys.exit(1)
    
    log_success("Spec válido y normalizado")
    
    if verbose:
        print(f"\n{Colors.BLUE}Spec normalizado:{Colors.RESET}")
        print(json.dumps(normalized_spec, indent=2, ensure_ascii=False))
    
    # FASE 2: Risk Engine
    print(f"\n{Colors.BOLD}[2/6] Risk Engine{Colors.RESET}")
    
    risk_engine = RiskEngine()
    risk_assessment = risk_engine.calculate(normalized_spec)
    risk_score = risk_assessment.score
    
    log_success(f"Risk Score: {risk_score} ({risk_assessment.level})")
    
    if verbose:
        print(f"\n{Colors.BLUE}Risk Factors:{Colors.RESET}")
        for factor, score in risk_assessment.factors.items():
            print(f"  - {factor}: +{score}")
        if risk_assessment.recommendations:
            print(f"\n{Colors.BLUE}Recommendations:{Colors.RESET}")
            for rec in risk_assessment.recommendations:
                print(f"  {rec}")
    
    # FASE 3: Model Router
    print(f"\n{Colors.BOLD}[3/6] Model Router{Colors.RESET}")
    
    model_router = ModelRouter()
    routing_decision = model_router.select(normalized_spec, risk_score)
    model = routing_decision.model
    model_config = model_router.get_model_config(routing_decision)
    
    log_success(f"Model: {model} (confidence: {routing_decision.confidence:.0%})")
    log_info(f"Reason: {routing_decision.reason}")
    
    # FASE 4: Tool Planner
    print(f"\n{Colors.BOLD}[4/6] Tool Planner{Colors.RESET}")
    
    tool_planner = ToolPlanner()
    tool_contracts = tool_planner.plan(normalized_spec, risk_score)
    tools = tool_planner.to_bundle_format(tool_contracts)
    
    log_success(f"Tools seleccionados: {len(tools)}")
    for tool in tool_contracts:
        side_effect_icon = "⚠️" if tool.side_effects else "✓"
        print(f"  {side_effect_icon} {tool.name}: {tool.description[:50]}...")
    
    # FASE 5: Prompt Compiler
    print(f"\n{Colors.BOLD}[5/6] Prompt Compiler{Colors.RESET}")
    
    prompt_compiler = PromptCompiler()
    compiled_prompt = prompt_compiler.compile(
        spec=normalized_spec,
        risk_score=risk_score,
        model=model,
        tools=tools
    )
    system_prompt = prompt_compiler.to_bundle_format(compiled_prompt)
    
    log_success(f"Prompt compilado: {compiled_prompt.tokens_approx} tokens aprox")
    log_info(f"SHA-256: {compiled_prompt.sha256_hash}")
    
    # Construir Gem Bundle (antes de verificar)
    gem_bundle = {
        "bundle_meta": {
            "use_case_id": normalized_spec['use_case_id'],
            "version": "1.0.0",
            "compiled_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "compiler_version": "1.0.0",
            "risk_score": risk_score
        },
        "model_routing": {
            "default_model": model,
            "reasoning_mode": "auto"
        },
        "policies": {
            "knowledge_states": ["HECHO_VERIFICADO", "INFERENCIA", "ASUNCION", "FALTAN_DATOS"],
            "model_armor_enabled": risk_score > 60,
            "hitl_required": (
                normalized_spec.get('security', {}).get('hitl_required', 'auto') == 'always'
                or risk_score > 80  # HITL automático para Risk alto
            )
        },
        "system_prompt": system_prompt,
        "tools": {
            "contracts": tools
        },
        "verifier": {
            "checks": ["schema", "grounding", "security", "ghost_entities"]
        }
    }
    
    # FASE 6: Verifier Gate
    print(f"\n{Colors.BOLD}[6/6] Verifier Gate{Colors.RESET}")
    
    verifier = VerifierGate()
    verification = verifier.verify(gem_bundle, risk_score)
    
    if verification.passed:
        log_success(f"Verificación pasada ({len(verification.checks_passed)}/4 checks)")
        gem_bundle = verifier.add_verification_metadata(gem_bundle, verification)
        gem_bundle['verifier']['verified_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    else:
        log_error("Verificación FALLIDA")
        for error in verification.errors:
            print(f"  {Colors.RED}✗{Colors.RESET} {error}")
    
    if verification.warnings:
        for warning in verification.warnings:
            print(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning}")
    
    # Guardar o mostrar
    if dry_run:
        log_info("Dry-run mode: No se guardará el bundle")
        print(f"\n{Colors.BLUE}Gem Bundle (preview):{Colors.RESET}")
        print(json.dumps(gem_bundle, indent=2, ensure_ascii=False))
    else:
        # Determinar output path
        if not output_path:
            use_case_id = normalized_spec['use_case_id']
            output_path = f"bundles/{use_case_id}_v1.0.0.json"
        
        # Crear directorio si no existe
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(gem_bundle, f, indent=2, ensure_ascii=False)
        
        log_success(f"Gem Bundle compilado: {output_path}")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Compilación completada{Colors.RESET}")
    print(f"  Risk Score: {risk_score}")
    print(f"  Model: {model}")
    print(f"  HITL: {gem_bundle['policies']['hitl_required']}")


def cmd_validate_spec(args):
    """Valida un Use Case Spec"""
    print_header("VALIDATE USE CASE SPEC")
    
    spec_path = args.spec
    
    validator = IntakeValidator()
    is_valid, normalized_spec, errors = validator.validate(spec_path)
    
    if is_valid:
        log_success("Spec válido")
        print(f"\nUse Case ID: {normalized_spec['use_case_id']}")
        print(f"Goal: {normalized_spec['goal']}")
        print(f"Data Sources: {len(normalized_spec.get('data_sources', []))}")
        print(f"Actions: {len(normalized_spec.get('actions', []))}")
    else:
        log_error("Spec inválido")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


def cmd_validate_bundle(args):
    """Valida un Gem Bundle existente"""
    print_header("VALIDATE GEM BUNDLE")
    
    bundle_path = args.bundle
    
    # Cargar bundle
    try:
        with open(bundle_path, 'r', encoding='utf-8') as f:
            bundle = json.load(f)
    except FileNotFoundError:
        log_error(f"Bundle no encontrado: {bundle_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        log_error(f"JSON inválido: {e}")
        sys.exit(1)
    
    log_info(f"Bundle: {bundle_path}")
    log_info(f"Use Case: {bundle.get('bundle_meta', {}).get('use_case_id', 'unknown')}")
    
    # Verificar
    verifier = VerifierGate()
    risk_score = bundle.get('bundle_meta', {}).get('risk_score', 0)
    result = verifier.verify(bundle, risk_score)
    
    if result.passed:
        log_success(f"Bundle VÁLIDO ({len(result.checks_passed)}/4 checks)")
    else:
        log_error("Bundle INVÁLIDO")
        for error in result.errors:
            print(f"  {Colors.RED}✗{Colors.RESET} {error}")
        sys.exit(1)
    
    if result.warnings:
        print(f"\n{Colors.YELLOW}Warnings:{Colors.RESET}")
        for warning in result.warnings:
            print(f"  ⚠ {warning}")


def cmd_version(args):
    """Muestra versión del compilador"""
    print_header("GEM BUILDER COMPILER")
    
    version_info = {
        "version": "1.0.0",
        "pipeline_stages": 6,
        "implemented_stages": 6,
        "status": "✅ Release - Pipeline completo (6/6 fases)"
    }
    
    print(json.dumps(version_info, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Gem Builder Compiler - Compilador Determinista de Agentes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Compilar Use Case Spec
  python cli.py compile --spec specs/my_use_case.json
  
  # Dry-run (sin guardar)
  python cli.py compile --spec specs/my_use_case.json --dry-run
  
  # Validar Spec
  python cli.py validate --spec specs/my_use_case.json
  
  # Versión
  python cli.py version
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando: compile
    compile_parser = subparsers.add_parser('compile', help='Compila Use Case Spec → Gem Bundle')
    compile_parser.add_argument('--spec', required=True, help='Path al Use Case Spec JSON')
    compile_parser.add_argument('--output', '-o', help='Path de salida del Gem Bundle')
    compile_parser.add_argument('--dry-run', action='store_true', help='Mostrar sin guardar')
    compile_parser.add_argument('--verbose', '-v', action='store_true', help='Output detallado')
    compile_parser.set_defaults(func=cmd_compile)
    
    # Comando: validate
    validate_parser = subparsers.add_parser('validate', help='Valida Spec o Bundle')
    validate_group = validate_parser.add_mutually_exclusive_group(required=True)
    validate_group.add_argument('--spec', help='Path al Use Case Spec JSON')
    validate_group.add_argument('--bundle', help='Path al Gem Bundle JSON')
    validate_parser.set_defaults(func=lambda args: 
        cmd_validate_spec(args) if args.spec else cmd_validate_bundle(args)
    )
    
    # Comando: version
    version_parser = subparsers.add_parser('version', help='Muestra versión del compilador')
    version_parser.set_defaults(func=cmd_version)
    
    # Comando: update
    update_parser = subparsers.add_parser('update', help='Actualiza Gem Builder desde GitHub')
    update_parser.set_defaults(func=cmd_update)
    
    # Parse args
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Ejecutar comando
    args.func(args)


if __name__ == "__main__":
    main()
