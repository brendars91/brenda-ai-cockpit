
"""
Skill Genetics Scanner
Scans the 'resources/skills' directory and generates a semantic index.
"""
import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict
from config_manager import config

class SkillScanner:
    def __init__(self):
        self.skills_root = config.get_path("skills")
        
    def scan(self) -> Dict:
        """
        Scans all SKILL.md files and builds a 'Genetic Map' of capabilities.
        Uses the internal 'resources/skills' directory.
        """
        dna_map = {
            "version": "2026.1",
            "skills": []
        }
        
        if not self.skills_root.exists():
            print(f"[WARN] Skills root not found at {self.skills_root}")
            return dna_map

        print(f"[SCAN] Scanning internal skills at: {self.skills_root}")

        try:
            # Recursive scan for SKILL.md (covers .agent, vendor, tools)
            for skill_file in self.skills_root.rglob("SKILL.md"):
                skill_data = self._extract_dna(skill_file)
                if skill_data:
                    dna_map["skills"].append(skill_data)
        except PermissionError as e:
            print(f"[ERROR] Permission denied scanning skills: {e}")
                        
        print(f"[SUCCESS] Scanned {len(dna_map['skills'])} skills from Local Genotype.")
        return dna_map

    def _extract_dna(self, file_path: Path) -> Dict:
        """
        Reads the SKILL.md and extracts metadata + adaptation prompts.
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Robust parsing fallback
            name = file_path.parent.name
            description = "No description"
            
            # Intento de parseo YAML básico si existe frontmatter
            lines = content.split('\n')
            in_frontmatter = False
            for line in lines:
                line = line.strip()
                if line == "---":
                    if in_frontmatter: break # Fin del frontmatter
                    in_frontmatter = True
                    continue
                
                if line.startswith("description:"):
                    description = line.replace("description:", "", 1).strip()
                    # Si no hay quote, estamos listos. Si hay quote, limpiar.
                    description = description.strip('"').strip("'")
            
            return {
                "id": name,
                "path": str(file_path.parent), # Internal path
                "description": description,
                "dna_hash": hashlib.md5(content.encode()).hexdigest()[:8],
                "adaptation_ready": True
            }
        except Exception as e:
            print(f"[WARN] Error extracting DNA from {file_path}: {e}")
            return None

if __name__ == "__main__":
    scanner = SkillScanner()
    print(json.dumps(scanner.scan(), indent=2))
