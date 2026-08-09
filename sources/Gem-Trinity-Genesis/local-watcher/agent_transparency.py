"""
Agent Transparency Logger
Stores input/output logs for each agent for user inspection.
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import uuid


@dataclass
class AgentExecutionLog:
    execution_id: str
    agent_name: str
    agent_type: str  # architect, builder, engine
    timestamp: str
    input_data: Dict
    output_data: Dict
    status: str  # pending, running, success, failed
    error: Optional[str] = None
    duration_ms: Optional[int] = None


class AgentTransparencyLogger:
    def __init__(self):
        self.logs_dir = Path("artifacts/agent_transparency")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.max_logs = 1000  # Keep last 1000 executions
    
    def log_execution_start(
        self, 
        agent_name: str, 
        agent_type: str, 
        input_data: Dict
    ) -> str:
        """Log the start of an agent execution."""
        execution_id = str(uuid.uuid4())
        
        log_entry = AgentExecutionLog(
            execution_id=execution_id,
            agent_name=agent_name,
            agent_type=agent_type,
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            input_data=input_data,
            output_data={},
            status="running"
        )
        
        self._save_log(log_entry)
        return execution_id
    
    def log_execution_complete(
        self, 
        execution_id: str, 
        output_data: Dict, 
        status: str = "success",
        error: Optional[str] = None
    ):
        """Log the completion of an agent execution."""
        log_entry = self._get_log(execution_id)
        if not log_entry:
            return
        
        # Calculate duration
        start_time = datetime.fromisoformat(log_entry.timestamp.replace("Z", "+00:00"))
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        log_entry.output_data = output_data
        log_entry.status = status
        log_entry.error = error
        log_entry.duration_ms = duration_ms
        
        self._save_log(log_entry)
    
    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get a specific execution log."""
        log_entry = self._get_log(execution_id)
        return asdict(log_entry) if log_entry else None
    
    def get_agent_executions(
        self, 
        agent_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get recent executions, optionally filtered by agent type."""
        logs = []
        
        for log_file in sorted(self.logs_dir.glob("*.json"), reverse=True)[:limit]:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_entry = json.load(f)
                    if agent_type is None or log_entry.get('agent_type') == agent_type:
                        logs.append(log_entry)
            except:
                continue
        
        return logs[:limit]
    
    def get_execution_input(self, execution_id: str) -> Optional[Dict]:
        """Get only the input data for an execution."""
        log_entry = self._get_log(execution_id)
        return log_entry.input_data if log_entry else None
    
    def get_execution_output(self, execution_id: str) -> Optional[Dict]:
        """Get only the output data for an execution."""
        log_entry = self._get_log(execution_id)
        return log_entry.output_data if log_entry else None
    
    def get_all_agent_types(self) -> List[str]:
        """Get list of all agent types that have been executed."""
        types = set()
        for log_file in self.logs_dir.glob("*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_entry = json.load(f)
                    if 'agent_type' in log_entry:
                        types.add(log_entry['agent_type'])
            except:
                continue
        return sorted(list(types))
    
    def _save_log(self, log_entry: AgentExecutionLog):
        """Save a log entry to disk."""
        log_file = self.logs_dir / f"{log_entry.execution_id}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(log_entry), f, indent=2, ensure_ascii=False)
        
        # Cleanup old logs
        self._cleanup_old_logs()
    
    def _get_log(self, execution_id: str) -> Optional[AgentExecutionLog]:
        """Get a log entry from disk."""
        log_file = self.logs_dir / f"{execution_id}.json"
        if not log_file.exists():
            return None
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return AgentExecutionLog(**data)
        except:
            return None
    
    def _cleanup_old_logs(self):
        """Remove old log files to keep only max_logs."""
        log_files = sorted(self.logs_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        for log_file in log_files[self.max_logs:]:
            try:
                log_file.unlink()
            except:
                pass


# Global instance
_transparency_logger: Optional[AgentTransparencyLogger] = None


def get_transparency_logger() -> AgentTransparencyLogger:
    """Get the global transparency logger instance."""
    global _transparency_logger
    if _transparency_logger is None:
        _transparency_logger = AgentTransparencyLogger()
    return _transparency_logger
