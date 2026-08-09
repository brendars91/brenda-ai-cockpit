
"""
Trinity Sync Engine (Context Aggregator)
Prepares the 'Neural Context' from internal modules.
"""
import time
import json
from pathlib import Path
from skill_scanner import SkillScanner
from config_manager import config

class SyncEngine:
    def __init__(self):
        self.scanner = SkillScanner()
        self.artifacts_dir = config.get_path("artifacts_root")
        self.artifacts_dir.mkdir(exist_ok=True)
        
    def pack_context(self) -> dict:
        """
        The 'Smart Context Packer'. 
        Aggregates all LOCAL INTERNAL intelligence into a single JSON payload.
        Returns the payload dict for API usage.
        """
        # 1. Scan Skills (Internal)
        skills_dna = self.scanner.scan()
        
        # 2. Get Project Status (TODO: Check internal modules health)
        project_status = {
            "architect": "online", # TODO: Real check via config.get_path('architect')
            "builder": "idle",
            "engine": "active"
        }
        
        # 3. Build Payload
        payload = {
            "timestamp": time.time(),
            "iso_timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "skills_index": skills_dna,
            "project_status": project_status,
            "mode": "autonomous_mirror" 
        }
        
        # 4. Save to Artifacts (Legacy support & Inspection)
        output_file = self.artifacts_dir / "context_payload.json"
        
        try:
            output_file.write_text(json.dumps(payload, indent=2))
        except Exception as e:
            print(f"[SYNC ERROR] Failed to write payload: {e}")

        return payload
        
    def run_once(self):
        """Manual trigger used by API"""
        print("[SYNC] Packing Neural Context...")
        self.pack_context()
        print("[SYNC] Complete.")

if __name__ == "__main__":
    engine = SyncEngine()
    engine.run_once()
