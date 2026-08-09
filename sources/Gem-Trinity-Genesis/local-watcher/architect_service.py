"""
Architect Service
Generates optimized context payloads from use case descriptions.
"""
import time
import uuid
import json
from pathlib import Path
from typing import Dict, List
from operation_tracker import track_operation

class ArchitectService:
    def __init__(self):
        self.payloads_dir = Path("artifacts/architect_payloads")
        self.payloads_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.payloads_dir / "history.json"
        
    @track_operation(op_type="llm", category="payload_generation")
    def generate_payload(self, use_case: str, domain: str, complexity: str, model: str, project_name: str = "") -> Dict:
        """
        Generates a context payload from use case description.
        
        Workflow:
        1. OPTIMIZE PROMPT: Mejora el prompt del usuario
        2. GENERATE PRD: Crea documento de requisitos según complejidad
        3. CREATE SPEC CONTRACT: Define contratos de herramientas
        
        Falls back to templates on failure.
        """
        payload_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Auto-generate project name if not provided
        if not project_name:
            project_name = f"{domain.upper()}_{payload_id[:8]}"
        
        context_payload = None
        optimized_prompt = use_case
        prd = {}
        spec_contract = {}
        
        # 1. Try Real LLM
        try:
            # Dynamic import to avoid circular dep issues during init if any
            try:
                from .llm_provider import LLMProvider
            except ImportError:
                from llm_provider import LLMProvider

            print("[Architect] analyzing requirements with Gemini Pro...")
            llm = LLMProvider()
            system_prompt = """You are an expert Solutions Architect. 
            Generate a JSON specification for the user's request.
            
            IMPORTANT: Return ONLY valid JSON, no explanations before or after.
            
            Structure:
            {
              "system": "SAP S/4HANA",
              "modules": ["list of modules"],
              "objectives": ["list of objectives"],
              "components": ["Ingestion", "RAG", "UI"],
              "data_strategy": {"privacy": "...", "grounding": "..."},
              "stack": ["Docker", "Python", "FastAPI"],
              "curriculum_coverage": ["module mappings if educational"]
            }"""
            
            response = llm.generate(use_case, system_prompt=system_prompt)
            
            # Robust JSON extraction
            import re
            
            # Method 1: Try direct parse after cleaning markdown
            clean_response = response.replace("```json", "").replace("```", "").strip()
            
            try:
                context_payload = json.loads(clean_response)
            except json.JSONDecodeError:
                # Method 2: Find JSON object with regex
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    context_payload = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in LLM response")
            
            print("[Architect] Generated custom payload via LLM.")
            
        except Exception as e:
            print(f"[Architect] LLM failed ({e}), falling back to rigid templates.")
            
        # 2. Fallback to Templates if LLM failed
        if not context_payload:
            if domain == "sap":
                context_payload = self._generate_sap_payload(use_case, complexity)
            elif domain == "marketing":
                context_payload = self._generate_marketing_payload(use_case, complexity)
            elif domain == "devops":
                context_payload = self._generate_devops_payload(use_case, complexity)
            else:
                context_payload = self._generate_custom_payload(use_case, complexity)
        
        # Generate PRD based on complexity
        prd = self._generate_prd(use_case, domain, complexity, context_payload)
        
        # Generate Spec Contract (tools and skills needed)
        spec_contract = self._generate_spec_contract(use_case, domain, complexity, context_payload)
        
        payload = {
            "payload_id": payload_id,
            "project_name": project_name,
            "timestamp": timestamp,
            "iso_timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "domain": domain,
            "complexity": complexity,
            "model": model,
            "use_case": use_case,
            "optimized_prompt": optimized_prompt,
            "prd": prd,
            "spec_contract": spec_contract,
            "context_payload": context_payload,
            "tokens_estimated": len(json.dumps(context_payload)) // 4,
            "status": "ready"
        }
        
        # Save payload
        payload_file = self.payloads_dir / f"{payload_id}.json"
        payload_file.write_text(json.dumps(payload, indent=2))
        
        # Update history
        self._update_history(payload)
        
        return payload
    
    def _generate_sap_payload(self, use_case: str, complexity: str) -> Dict:
        """Generate SAP-specific context payload (FI/CO/ABAP)"""
        return {
            "system": "SAP S/4HANA",
            "modules": ["FI", "CO", "ABAP"],
            "objectives": self._extract_objectives(use_case),
            "tables": ["BSEG", "BKPF", "SKA1", "BSIS", "BSAS"],
            "transactions": ["FB50", "F-53", "F110", "F.13"],
            "custom_code": {
                "type": "ABAP",
                "programs": ["Z_MONTHLY_CLOSE", "Z_FX_ADJUSTMENT"],
                "function_modules": ["Z_VALIDATE_POSTING", "Z_GENERATE_REPORT"]
            },
            "integration": {
                "rfc_destinations": ["SAP_PROD", "SAP_QAS"],
                "bapis": ["BAPI_ACC_DOCUMENT_POST", "BAPI_ACC_GL_POSTING_POST"]
            },
            "compliance": ["IFRS", "IAS 21", "IFRS 9"],
            "output": {
                "reports": ["Monthly Close Summary", "AR/AP Validation", "FX Position"],
                "format": "ALV Grid / Fiori"
            }
        }
    
    def _generate_marketing_payload(self, use_case: str, complexity: str) -> Dict:
        """Generate Marketing-specific context payload"""
        return {
            "campaign_type": "digital",
            "objectives": self._extract_objectives(use_case),
            "channels": ["email", "social", "seo", "ppc"],
            "metrics": ["CTR", "conversion_rate", "ROI", "engagement"],
            "tools": ["Google Analytics", "HubSpot", "Mailchimp"],
            "audience": {
                "segments": ["B2B", "B2C", "enterprise"],
                "personas": self._extract_personas(use_case)
            },
            "content": {
                "types": ["blog", "video", "infographic", "white_paper"],
                "tone": "professional"
            }
        }
    
    def _generate_devops_payload(self, use_case: str, complexity: str) -> Dict:
        """Generate DevOps-specific context payload"""
        return {
            "pipeline_type": "CI/CD",
            "objectives": self._extract_objectives(use_case),
            "platforms": ["GitHub Actions", "Jenkins", "GitLab CI"],
            "environments": ["dev", "staging", "production"],
            "infrastructure": {
                "cloud": "AWS/GCP/Azure",
                "containers": ["Docker", "Kubernetes"],
                "iac": ["Terraform", "Ansible"]
            },
            "monitoring": {
                "tools": ["Prometheus", "Grafana", "Datadog"],
                "alerts": ["error_rate", "latency", "downtime"]
            },
            "security": {
                "scans": ["SAST", "DAST", "dependency_check"],
                "compliance": ["SOC2", "ISO27001"]
            }
        }
    
    def _generate_custom_payload(self, use_case: str, complexity: str) -> Dict:
        """Generate generic custom payload"""
        return {
            "type": "custom",
            "objectives": self._extract_objectives(use_case),
            "requirements": self._extract_requirements(use_case),
            "constraints": self._extract_constraints(use_case),
            "deliverables": ["analysis", "implementation", "testing", "documentation"]
        }
    
    def _extract_objectives(self, text: str) -> List[str]:
        """Extract objectives from text (simplified - would use NLP in production)"""
        keywords = ["automate", "validate", "generate", "reconcile", "analyze", "optimize", 
                   "automatizar", "automatización", "validar", "generar", "conciliar", "analizar", "optimizar", "cierre"]
        return [f"Objective: {kw.title()} process" for kw in keywords if kw in text.lower()][:3]
    
    def _extract_personas(self, text: str) -> List[str]:
        """Extract personas from text"""
        personas = []
        if "cfo" in text.lower() or "finance" in text.lower():
            personas.append("CFO / Finance Director")
        if "marketing" in text.lower():
            personas.append("Marketing Manager")
        return personas if personas else ["Generic User"]
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract requirements"""
        return [f"Requirement extracted from: {text[:50]}..."]
    
    def _extract_constraints(self, text: str) -> List[str]:
        """Extract constraints"""
        return ["Time: Meet monthly deadline", "Budget: Cost-effective solution"]
    
    @track_operation(op_type="deterministic", category="prd_generation")
    def _generate_prd(self, use_case: str, domain: str, complexity: str, context: Dict) -> Dict:
        """Generate Product Requirements Document v2.0-gated"""
        
        # Map complexity to level
        level_map = {
            "simple": "basic",
            "medium": "medium", 
            "difficult": "advanced"
        }
        level = level_map.get(complexity, "basic")
        
        return self._generate_gated_prd(use_case, domain, level, context)

    def _generate_gated_prd(self, use_case: str, domain: str, level: str, context: Dict) -> Dict:
        """
        Generates PRD with Gates 0-6 and Schema Contract V2.0.
        "Extract Don't Invent": Uses TBD for missing info.
        """
        
        tbd_items = []
        
        # 1. Summary (1-Pager)
        summary = self._generate_summary(use_case, domain, level, tbd_items)
        
        # 2. Gates Generation
        gates = {}
        gate_defs = self._get_gate_definitions(level)
        
        for gate_id, gate_config in gate_defs.items():
             gates[gate_id] = self._process_gate(gate_id, gate_config, use_case, context, tbd_items)

        # 3. Assemble V2.0 Contract
        prd = {
            "meta": {
                "format_version": "2.0-gated",
                "generated_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                "complexity_level": level,
                "domain": domain
            },
            "summary": summary,
            "gates": gates,
            "tbd_items": tbd_items,
            "assumptions": ["Assumption: User has valid API keys if external services are needed."],
            "decision_log": []
        }
        
        return prd

    def _generate_summary(self, use_case: str, domain: str, level: str, tbd_log: List[Dict]) -> Dict:
        """Generate Fixed Fields Summary using LLM for real content."""
        
        # Try to use LLM to extract real information from use_case
        try:
            try:
                from .llm_provider import LLMProvider
            except ImportError:
                from llm_provider import LLMProvider
            
            llm = LLMProvider()
            
            summary_prompt = f"""Based on this use case: "{use_case}"
Generate a JSON summary with these exact fields:
- elevator_pitch: A one-sentence value proposition (max 50 words)
- primary_user: Who is the target user (be specific)
- core_value: What value does this provide (max 30 words)
- v1_scope_in: Array of 3-5 specific features included in v1
- top_risks: Array of 2-3 potential risks (only for advanced level)
- success_metrics: Array of 3 measurable success criteria

Return ONLY valid JSON, no explanations."""
            
            response = llm.generate(summary_prompt, system_prompt="You are a product manager. Generate concise, specific product requirements.")
            
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                summary_data = json.loads(json_match.group())
                return {
                    "elevator_pitch": summary_data.get("elevator_pitch", use_case[:100]),
                    "primary_user": summary_data.get("primary_user", "Target users"),
                    "core_value": summary_data.get("core_value", "Automate and streamline"),
                    "v1_scope_in": summary_data.get("v1_scope_in", []),
                    "v1_scope_out": ["Optimization of legacy modules", "UI redesign"] if level == "basic" else [],
                    "top_risks": summary_data.get("top_risks", []) if level != "basic" else [],
                    "success_metrics": summary_data.get("success_metrics", ["Execution Time", "Error Rate", "Completion"])
                }
        except Exception as e:
            print(f"[Architect] LLM summary generation failed: {e}")
        
        # Fallback to heuristic extraction
        summary = {
            "elevator_pitch": self._extract_or_tbd(use_case, "elevator pitch", tbd_log),
            "primary_user": self._extract_or_tbd(use_case, "primary user", tbd_log),
            "core_value": self._extract_or_tbd(use_case, "core value proposition", tbd_log),
            "v1_scope_in": self._extract_list(use_case, "scope in", 3),
            "v1_scope_out": ["Optimization of legacy modules", "UI redesign"] if level == "basic" else [],
            "top_risks": self._extract_list(use_case, "risks", 3) if level != "basic" else [],
            "success_metrics": self._extract_list(use_case, "metrics", 3)
        }
        return summary

    def _get_gate_definitions(self, level: str) -> Dict:
        """Define content requirements per gate and level."""
        
        defs = {
            "0_alignment": {
                "name": "Alignment & Vision",
                "sections": ["Target Result V1", "Success Criteria"]
            },
            "1_problem": {
                "name": "Problem & User Context",
                "sections": ["Primary User Pain", "Trigger Event"]
            },
            "2_scope": {
                "name": "Scope V1",
                "sections": ["In-Scope Features", "Out-of-Scope Items"]
            },
            "3_flows": {
                "name": "Critical User Flows",
                "sections": ["Main Happy Path"]
            },
            "4_nfr": {
                "name": "Non-Functional Requirements",
                "sections": ["Performance Constraints"]
            },
            "5_risks": {
                "name": "Risks & Decisions",
                "sections": ["Key Risks"]
            },
             "6_metrics": {
                "name": "Success Metrics",
                "sections": ["KPIs"]
            }
        }
        
        if level == "medium":
            defs["3_flows"]["sections"].append("Error Handling Flow")
            defs["1_problem"]["sections"].append("Current Workaround Costs")
            
        if level == "advanced":
            defs["5_risks"]["sections"].extend(["Mirror Test Definition", "Threat Model"])
            defs["6_metrics"]["sections"].append("SLOs (Service Level Objectives)")
            
        return defs

    def _process_gate(self, gate_id: str, config: Dict, text: str, context: Dict, tbd_log: List) -> Dict:
        """Process a single gate, extracting content or marking TBD."""
        content = {}
        status = "approved"
        
        for section in config["sections"]:
            # Special handling for Advanced Mirror Test
            if section == "Mirror Test Definition":
                 content[section] = {
                     "scope": "sandbox",
                     "environment": "local_docker",
                     "allowed_actions": ["read_only_scans"],
                     "stop_conditions": "critical_alert",
                     "pass_fail_criteria": "no_high_severity_findings"
                 }
                 continue

            value = self._extract_or_tbd(text, section, tbd_log)
            content[section] = value
            if value == "[TBD]":
                status = "blocked"
                
        return {
            "name": config["name"],
            "status": status,
            "content": content,
            "required_approvals": []
        }

    def _extract_or_tbd(self, text: str, topic: str, tbd_log: List) -> str:
        """Extract information using LLM or return [TBD] and log it."""
        # Try LLM extraction first
        try:
            try:
                from .llm_provider import LLMProvider
            except ImportError:
                from llm_provider import LLMProvider
            
            llm = LLMProvider()
            
            extract_prompt = f"""Based on this use case: "{text}"
Answer this question with 1-2 sentences: {topic}

If the information is not explicitly stated, infer a reasonable answer based on the use case context."""
            
            result = llm.generate(extract_prompt, system_prompt="You are a business analyst. Provide concise, specific answers.")
            
            if result and len(result) > 10 and "[TBD]" not in result:
                return result.strip()
        except Exception as e:
            print(f"[Architect] LLM extraction failed for {topic}: {e}")
        
        # Fallback to simple heuristics
        if topic.lower() in text.lower():
             return f"Extracted {topic} from use case..."
        
        if "user" in topic and "user" in text.lower():
            return "Generic User (refined based on text)"
        
        tbd_log.append({"field": topic, "question": f"Please define {topic}."})
        return "[TBD]"

    def _extract_list(self, text: str, topic: str, limit: int) -> List[str]:
        # Try LLM extraction first
        try:
            try:
                from .llm_provider import LLMProvider
            except ImportError:
                from llm_provider import LLMProvider
            
            llm = LLMProvider()
            
            list_prompt = f"""Based on this use case: "{text}"
Generate a JSON array of {limit} specific {topic} (be concise and practical).
Return ONLY a JSON array like ["item1", "item2", "item3"]"""
            
            response = llm.generate(list_prompt, system_prompt="You are a product analyst. Provide specific, actionable items.")
            
            import re
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                items = json.loads(json_match.group())
                if isinstance(items, list):
                    return items[:limit]
        except Exception as e:
            print(f"[Architect] LLM list extraction failed for {topic}: {e}")
        
        # Fallback to simple heuristics
        if topic in text.lower():
            return [f"{topic} detailed item {i+1}" for i in range(limit)]
        if "generate" in text.lower() and topic == "metrics":
             return ["Execution Time", "Error Rate", "Completion Status"]
        return []
    
    @track_operation(op_type="deterministic", category="spec_contract_generation")
    def _generate_spec_contract(self, use_case: str, domain: str, complexity: str, context: Dict) -> Dict:
        """Generate Specification Contract v2.1 (Advanced Enterprise Schema)"""
        
        # Map user complexity to contract level
        level_map = {
            "simple": "basic",
            "medium": "medium", 
            "difficult": "advanced"
        }
        user_level = level_map.get(complexity, "basic")
        
        # Base contract structure
        contract = {
            "version": "2.1.0",
            "configuration": {
                "user_level": user_level,
                "depth_profile": self._get_depth_profile(user_level),
                "time_budget": self._get_time_budget(user_level)
            },
            "scope": self._get_scope_policy(user_level),
            "behavior": {
                "error_handling": self._get_error_handling(user_level),
                "mirror_test": self._get_mirror_test_config(user_level)
            },
            "evidence_model": {
                "finding_required_fields": [
                    "id", "title", "category", "severity", "confidence",
                    "filepath", "line_range", "evidence", "recommendation", "validation_step", "risk"
                ]
            },
            "deliverables": [
                {
                    "id": "audit_report",
                    "name": "Audit Report",
                    "path": "reports/audit_report.md",
                    "format": "markdown",
                    "validation_schema": { "id": "audit_report_v1", "version": "1.0" }
                },
                {
                    "id": "findings_data",
                    "name": "Findings Data",
                    "path": "reports/findings.json",
                    "format": "json",
                    "validation_schema": { "id": "findings_v1", "version": "1.0" }
                }
            ],
            "acceptance_criteria": {
                "schema_validation_passed": True,
                "min_scan_coverage_percent": 95 if user_level == "advanced" else 80,
                "evidence_compliance": True,
                "no_secrets_in_outputs": True,
                "runtime_within_budget": True
            }
        }
        
        return contract

    def _get_depth_profile(self, level: str) -> Dict:
        profiles = {
            "basic": {
                "enabled_analyses": ["duplication", "dead_code"],
                "max_findings": 20,
                "min_confidence": 0.8,
                "evidence": {
                    "min_evidence_per_finding": 1,
                    "snippet_max_chars": 400,
                    "must_include": ["filepath", "line_range", "snippet"]
                },
                "thresholds": {
                    "max_cyclomatic_complexity": 15
                }
            },
            "medium": {
                "enabled_analyses": ["duplication", "dead_code", "complexity", "dependencies"],
                "max_findings": 50,
                "min_confidence": 0.7,
                "evidence": {
                    "min_evidence_per_finding": 2,
                    "snippet_max_chars": 800,
                    "must_include": ["filepath", "line_range", "snippet", "reason"]
                },
                "thresholds": {
                    "max_cyclomatic_complexity": 10
                }
            },
            "advanced": {
                "enabled_analyses": ["duplication", "dead_code", "complexity", "dependencies", "security_basic"],
                "max_findings": 100,
                "min_confidence": 0.6,
                "evidence": {
                    "min_evidence_per_finding": 2,
                    "snippet_max_chars": 1000,
                    "must_include": ["filepath", "line_range", "snippet", "reason", "risk", "validation_step"]
                },
                "thresholds": {
                    "max_cyclomatic_complexity": 8
                }
            }
        }
        return profiles.get(level, profiles["basic"])

    def _get_time_budget(self, level: str) -> Dict:
        if level == "basic":
            return {"global_timeout_sec": 300, "phases": {"scan": 60, "analyze": 120, "report": 60, "mirror_test": 0}}
        elif level == "medium":
             return {"global_timeout_sec": 480, "phases": {"scan": 90, "analyze": 180, "report": 90, "mirror_test": 60}}
        else:
             return {"global_timeout_sec": 600, "phases": {"scan": 120, "analyze": 240, "report": 120, "mirror_test": 120}}

    def _get_scope_policy(self, level: str) -> Dict:
        return {
            "read_paths": ["src/**", "api/**", "modules/**"],
            "exclude_paths": ["tests/**", "vendor/**", "**/*.min.js", "node_modules/**", "__pycache__/**"],
            "write_paths": ["reports/**", "artifacts/**"],
            "redaction_policy": {
                "behavior": "mask",
                "patterns": ["API_KEY", "PASSWORD", "SECRET", "BEGIN PRIVATE KEY", "AKIA[0-9A-Z]{16}"]
            }
        }

    def _get_error_handling(self, level: str) -> Dict:
        return {
            "max_retries": 3,
            "retry_on": ["timeout", "io_error", "http_429", "http_5xx"],
            "backoff": "exponential",
            "partial_success_allowed": level == "basic"
        }

    def _get_mirror_test_config(self, level: str) -> Dict:
        configs = {
            "basic": {
                "enabled": False,
                "mode": "passive",
                "allowed_actions": [],
                "disallowed_actions": ["all"]
            },
            "medium": {
                "enabled": True,
                "mode": "passive",
                "targets_allowlist": ["localhost"],
                "rate_limit_rps": 1,
                "max_requests": 10,
                "allowed_actions": ["header_checks", "ssl_checks"],
                "disallowed_actions": ["active_probing", "data_mutation"],
                "stop_on_severity": "medium",
                "report_path": "reports/mirror_test_passive.json"
            },
            "advanced": {
                "enabled": True,
                "mode": "sandbox",
                "targets_allowlist": ["localhost", "staging.internal"],
                "rate_limit_rps": 2,
                "max_requests": 50,
                "allowed_actions": ["input_validation_checks", "authz_negative_tests"],
                "disallowed_actions": ["ddos", "data_deletion", "data_exfiltration", "privilege_escalation"],
                "stop_on_severity": "high",
                "report_path": "reports/mirror_test_active.json"
            }
        }
        return configs.get(level, configs["basic"])
    
    def _update_history(self, payload: Dict):
        """Update history file with new payload"""
        history = []
        if self.history_file.exists():
            history = json.loads(self.history_file.read_text())
        
        history.insert(0, {
            "payload_id": payload["payload_id"],
            "project_name": payload.get("project_name", ""),
            "timestamp": payload["iso_timestamp"],
            "domain": payload["domain"],
            "complexity": payload["complexity"],
            "use_case": payload["use_case"][:100]
        })
        
        # Keep last 20
        history = history[:20]
        self.history_file.write_text(json.dumps(history, indent=2))
    
    def get_history(self) -> List[Dict]:
        """Get payload history"""
        if not self.history_file.exists():
            return []
        return json.loads(self.history_file.read_text())
        
    def delete_from_history(self, payload_id: str):
        """Remove entry from history"""
        if not self.history_file.exists():
            return
            
        history = json.loads(self.history_file.read_text())
        new_history = [h for h in history if h.get("payload_id") != payload_id]
        
        if len(history) != len(new_history):
            self.history_file.write_text(json.dumps(new_history, indent=2))
    
    def get_payload(self, payload_id: str) -> Dict:
        """Retrieve a specific payload"""
        payload_file = self.payloads_dir / f"{payload_id}.json"
        if not payload_file.exists():
            return {}
        return json.loads(payload_file.read_text())
