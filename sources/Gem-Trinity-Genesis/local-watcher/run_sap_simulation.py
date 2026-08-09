import os
import sys
import asyncio
import json
import time

# Ensure we can import from local directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from architect_service import ArchitectService
    from builder_service import BuilderService, BuildStatus
    from llm_provider import LLMProvider
except ImportError:
    # Handle running from root
    from local_watcher.architect_service import ArchitectService
    from local_watcher.builder_service import BuilderService, BuildStatus
    from local_watcher.llm_provider import LLMProvider

# --- USER PROMPT (SAP DEV TUTOR) ---
USER_PROMPT = """
Actúa como: arquitecto de software + ML engineer (RAG) + DevOps (Docker) + experto certificado SAP Development.

CONTEXTO:
Estoy cursando la Weiterbildung "SAP-Entwicklung" de DCI. Quiero construir una app "SAP Dev Tutor (DCI Edition)" que:
- Durante el curso: me ayude en tiempo real.
- Después del curso: herramienta profesional.

REQUISITOS:
1) PRIVACIDAD: Modo CURSO (cloud ok) vs TRABAJO (100% local/Docker).
2) ANTI-ALUCINACIONES: Grounding agresivo. Citar fuentes internas.
3) IDIOMA: Input DE, Output ES (con términos DE).

COMPONENTES:
A) INGESTA: Material DCI (PDF/PPTX), Transcripciones.
B) RAG: Qdrant, Chunking con metadata.
C) TUTOR UI: Chat con modos (Profesor, Resumen).

ESTRATEGIA DE INGESTA (DEFINIDA):
- No usar browser automation para grabar clases.
- Usar grabaciones oficiales o locales (OBS) -> Transcribir con Whisper.
- El Tutor debe saber los 8 modulos del DCI (Basics, S/4HANA, Procesos, ABAP, RAP, Fiori).
"""

def run_simulation():
    print("--- SIMULATION START: SAP DEV TUTOR GENESIS ---")
    
    # 0. Setup Env
    if not os.getenv("LLM_PROVIDER"):
        os.environ["LLM_PROVIDER"] = "gemini"
    
    # 1. ARCHITECT PHASE
    print("\n--- [PHASE 1] ARCHITECT: ANALYZING REQUEST ---")
    architect = ArchitectService()
    
    # Generate Payload (Using Real LLM now!)
    print(">> Sending prompt to Architect Agent...")
    payload = architect.generate_payload(
        use_case=USER_PROMPT,
        domain="sap",
        complexity="high",
        model="gemini-pro"
    )
    
    print("\n[Architect Output (Blueprint)]:")
    print(json.dumps(payload["context_payload"], indent=2))
    
    # 2. BUILDER PHASE
    print("\n--- [PHASE 2] BUILDER: ASSEMBLING AGENTS ---")
    builder = BuilderService()
    
    # Compile Agent from Payload
    print(">> Submitting Blueprint to Builder Queue...")
    build_info = builder.compile_agent(
        payload_id=payload["payload_id"],
        agent_name="SAP_Dev_Tutor_Agent",
        model_config={"model": "gemini-2.0-flash"},
        tools=["rag-pipeline", "sap-knowledge-base"] # Simulating discovered tools
    )
    
    build_id = build_info["build_id"]
    print(f">> Build Started: {build_id} (ETA: {build_info['eta_seconds']}s)")
    
    # 3. MONITOR BUILD
    print("\n--- [PHASE 3] MONITORING CONSTRUCTION ---")
    while True:
        queue = builder.get_queue()
        # Find our build
        build_item = next((item for item in queue if item["build_id"] == build_id), None)
        
        if not build_item:
            print("[x] Build item lost!")
            break
            
        status = build_item["status"]
        progress = build_item.get("progress", 0)
        print(f"[{status}] Progress: {progress}%")
        
        if status == "READY":
            print("\n[BUILD COMPLETE!]")
            print(f"Completed at: {build_item.get('completed_at')}")
            break
        elif status == "FAILED":
            print(f"\n[BUILD FAILED]: {build_item.get('error')}")
            break
            
        time.sleep(2)
        
    # 4. REVIEW RESULTS
    print("\n--- [PHASE 4] FINAL AUDIT ---")
    agent_artifact = builder.get_agent(build_id)
    if agent_artifact:
        print("Agent Artifact Created Successfully:")
        print(f"- ID: {agent_artifact['id']}")
        print(f"- Script Path: {agent_artifact.get('script_path')}")
        
        # Verify Script Exists
        script_path = agent_artifact.get('script_path')
        if os.path.exists(script_path):
             print(f"[Verified]: Python Script generated at {script_path}")
             with open(script_path, "r", encoding="utf-8") as f:
                 print("\n--- PREVIEW OF GENERATED CODE ---")
                 content = f.read()
                 print(content[:500] + "\n...(truncated)...")
        else:
             print("[Error]: Script file not found on disk.")
    else:
        print("[Error]: Agent artifact could not be retrieved.")

    print("\n[SIMULATION COMPLETE.]")

if __name__ == "__main__":
    run_simulation()
