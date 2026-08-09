"""
Skill Genetics Service
Auto-generates missing skills following best practices and saves them for future use.
"""
import os
import json
from pathlib import Path
from typing import Dict, Optional

class SkillGeneticsService:
    """
    Implements the "Skill Genetics" pattern:
    1. When a skill is needed but doesn't exist, generate it using LLM
    2. Follow skill best practices (SKILL.md structure)
    3. Save to library for future reuse
    4. Adapt to current project context
    """
    
    SKILL_TEMPLATE = '''---
name: {skill_name}
description: {description}
version: 1.0.0
auto_generated: true
---

# {skill_name}

## Purpose
{purpose}

## Usage
{usage}

## Instructions
{instructions}

## Examples
{examples}

## Best Practices
{best_practices}
'''

    def __init__(self, skills_path: Path = None, llm_provider = None):
        self.skills_path = skills_path or Path("resources/skills")
        self.skills_path.mkdir(parents=True, exist_ok=True)
        self.llm = llm_provider
        
    def get_skill(self, skill_name: str, project_context: str = "") -> Optional[str]:
        """
        Get a skill, generating it if it doesn't exist.
        Returns the skill content adapted to the project context.
        """
        skill_dir = self.skills_path / skill_name
        skill_file = skill_dir / "SKILL.md"
        
        if skill_file.exists():
            # Skill exists - read and adapt to context
            base_skill = skill_file.read_text(encoding="utf-8")
            if project_context and self.llm:
                return self._adapt_skill_to_context(base_skill, project_context)
            return base_skill
        else:
            # Skill doesn't exist - generate it
            print(f"[SkillGenetics] Skill '{skill_name}' not found. Generating...")
            return self._generate_skill(skill_name, project_context)
    
    def _generate_skill(self, skill_name: str, project_context: str) -> Optional[str]:
        """Generate a new skill using LLM and save it."""
        if not self.llm:
            print("[SkillGenetics] No LLM available for skill generation.")
            return None
            
        # Read existing skills to understand the format
        example_skills = self._get_example_skills()
        
        prompt = f"""Generate a professional-grade SKILL.md file for a skill called "{skill_name}".

CONTEXT OF THE PROJECT WHERE IT WILL BE USED:
{project_context[:1000] if project_context else "General purpose"}

EXAMPLES OF EXISTING SKILLS (follow this format):
{example_skills[:2000]}

REQUIREMENTS:
1. Follow the YAML frontmatter + Markdown format
2. Be extremely detailed and actionable
3. Include real code examples where applicable
4. Cover edge cases and best practices
5. Make it production-ready and professional

Generate ONLY the SKILL.md content, no explanation."""

        system_prompt = """You are an expert skill architect. 
You create detailed, professional skill documentation that enables AI agents to perform complex tasks.
Your skills are known for being comprehensive, practical, and immediately usable."""

        try:
            skill_content = self.llm.generate(prompt, system_prompt=system_prompt)
            
            # Validate content
            if not skill_content or skill_content.startswith("Error") or "Gemini Error" in skill_content:
                print(f"[SkillGenetics] Generation failed with LLM error: {skill_content}")
                return None

            # Save the generated skill
            skill_dir = self.skills_path / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(skill_content, encoding="utf-8")
            
            print(f"[SkillGenetics] Created new skill: {skill_name}")
            print(f"[SkillGenetics] Saved to: {skill_file}")
            
            # Adapt to current project context
            if project_context:
                return self._adapt_skill_to_context(skill_content, project_context)
            return skill_content
            
        except Exception as e:
            print(f"[SkillGenetics] Failed to generate skill: {e}")
            return None
    
    def _adapt_skill_to_context(self, skill_content: str, project_context: str) -> str:
        """Adapt a generic skill to the specific project context."""
        if not self.llm:
            return skill_content
            
        prompt = f"""Adapt this skill to the specific project context below.
Keep all the core instructions but customize examples, terminology, and focus areas.

SKILL CONTENT:
{skill_content[:3000]}

PROJECT CONTEXT:
{project_context[:1000]}

Return the adapted skill content maintaining the same structure."""

        try:
            adapted = self.llm.generate(prompt, system_prompt="You adapt skills to project contexts while preserving their core functionality.")
            return adapted
        except Exception as e:
            print(f"[SkillGenetics] Adaptation failed, using base skill: {e}")
            return skill_content
    
    def _get_example_skills(self) -> str:
        """Read existing skills to use as examples."""
        examples = []
        
        for skill_dir in self.skills_path.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    try:
                        content = skill_file.read_text(encoding="utf-8")
                        examples.append(f"--- SKILL: {skill_dir.name} ---\n{content[:500]}...")
                        if len(examples) >= 2:  # Max 2 examples
                            break
                    except:
                        pass
        
        if not examples:
            # Provide a template example
            return self.SKILL_TEMPLATE.format(
                skill_name="example-skill",
                description="An example skill template",
                purpose="Shows the structure of a well-formed skill",
                usage="Reference this when creating new skills",
                instructions="1. Follow this format\n2. Be detailed\n3. Include examples",
                examples="```python\n# Example code here\n```",
                best_practices="- Keep instructions clear\n- Include error handling"
            )
        
        return "\n\n".join(examples)
    
    def list_skills(self) -> list:
        """List all available skills."""
        skills = []
        for skill_dir in self.skills_path.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skills.append(skill_dir.name)
        return skills


# Integration function for BuilderService
def ensure_skill(skill_name: str, project_context: str = "") -> Optional[str]:
    """
    Convenience function to get or generate a skill.
    Uses LLMProvider if available.
    """
    try:
        from llm_provider import LLMProvider
        llm = LLMProvider()
    except:
        llm = None
    
    service = SkillGeneticsService(llm_provider=llm)
    return service.get_skill(skill_name, project_context)
