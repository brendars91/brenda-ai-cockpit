"""
State Store v2.0 - Persistent Workflow State
SQLite-based state persistence for Gem-Trinity Genesis workflows.
"""
import sqlite3
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import threading
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class WorkflowStage(str, Enum):
    """Stages of a workflow"""
    IDLE = "idle"
    ARCHITECTING = "architecting"
    ARCHITECT_REVIEW = "architect_review"
    BUILDING = "building"
    ENGINE_ACTIVE = "engine_active"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowStatus(str, Enum):
    """Status of a workflow"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StateStore:
    """
    Persistent state store using SQLite.

    Features:
    - Workflow state persistence
    - Automatic schema management
    - Thread-safe operations
    - Query by multiple criteria
    - State history tracking
    - Automatic cleanup of old records
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize state store.

        Args:
            db_path: Path to SQLite database. Defaults to artifacts/state.sqlite
        """
        self.db_path = db_path or Path("artifacts/state.sqlite")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Get thread-safe database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            # Workflows table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_id TEXT,
                    agent_id TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    completed_at REAL,
                    data TEXT,  -- JSON data
                    error TEXT,
                    FOREIGN KEY (payload_id) REFERENCES payloads(id),
                    FOREIGN KEY (agent_id) REFERENCES agents(id)
                )
            """)

            # Payloads table (Architect outputs)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payloads (
                    id TEXT PRIMARY KEY,
                    use_case TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    complexity TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    data TEXT NOT NULL,  -- Full payload JSON
                    prd TEXT,  -- PRD JSON
                    spec_contract TEXT  -- Spec contract JSON
                )
            """)

            # Agents table (Builder outputs)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    payload_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    model TEXT NOT NULL,
                    tools TEXT,  -- JSON array
                    script_path TEXT,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    completed_at REAL,
                    data TEXT,  -- Full agent data JSON
                    FOREIGN KEY (payload_id) REFERENCES payloads(id)
                )
            """)

            # Executions table (Engine outputs)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    task TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at REAL NOT NULL,
                    completed_at REAL,
                    logs TEXT,  -- JSON array of logs
                    result TEXT,
                    error TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agents(id)
                )
            """)

            # State history table (for audit trail)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS state_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    data TEXT,
                    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
                )
            """)

            # Indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_workflows_stage ON workflows(stage)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_workflows_created ON workflows(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_payloads_domain ON payloads(domain)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_payload ON agents(payload_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_agent ON executions(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_workflow ON state_history(workflow_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_timestamp ON state_history(timestamp)")

    # ========== Workflow Methods ==========

    def create_workflow(
        self,
        workflow_id: str,
        project_name: str,
        stage: WorkflowStage = WorkflowStage.IDLE,
        status: WorkflowStatus = WorkflowStatus.PENDING,
        payload_id: Optional[str] = None,
        data: Optional[Dict] = None
    ) -> bool:
        """
        Create a new workflow.

        Args:
            workflow_id: Unique workflow ID
            project_name: Project name
            stage: Initial stage
            status: Initial status
            payload_id: Associated payload ID
            data: Additional workflow data

        Returns:
            True if successful
        """
        try:
            now = asyncio.get_event_loop().time()

            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO workflows (id, project_name, stage, status, payload_id, created_at, updated_at, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    workflow_id,
                    project_name,
                    stage.value,
                    status.value,
                    payload_id,
                    now,
                    now,
                    json.dumps(data) if data else None
                ))

            # Record in history
            self._record_history(workflow_id, stage.value, status.value, data)

            logger.info(f"[StateStore] Created workflow: {workflow_id}")
            return True

        except Exception as e:
            logger.error(f"[StateStore] Failed to create workflow: {e}")
            return False

    def update_workflow(
        self,
        workflow_id: str,
        stage: Optional[WorkflowStage] = None,
        status: Optional[WorkflowStatus] = None,
        payload_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        data: Optional[Dict] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Update workflow state.

        Args:
            workflow_id: Workflow ID
            stage: New stage
            status: New status
            agent_id: Associated agent ID
            data: Updated workflow data
            error: Error message if failed

        Returns:
            True if successful
        """
        try:
            now = asyncio.get_event_loop().time()

            updates = ["updated_at = ?"]
            values = [now]

            if stage is not None:
                updates.append("stage = ?")
                values.append(stage.value)

            if status is not None:
                updates.append("status = ?")
                values.append(status.value)

            if payload_id is not None:
                updates.append("payload_id = ?")
                values.append(payload_id)

            if agent_id is not None:
                updates.append("agent_id = ?")
                values.append(agent_id)

            if data is not None:
                updates.append("data = ?")
                values.append(json.dumps(data))

            if error is not None:
                updates.append("error = ?")
                values.append(error)

            if status == WorkflowStatus.COMPLETED:
                updates.append("completed_at = ?")
                values.append(now)

            values.append(workflow_id)

            with self._get_connection() as conn:
                conn.execute(f"""
                    UPDATE workflows
                    SET {', '.join(updates)}
                    WHERE id = ?
                """, values)

            # Record in history if stage or status changed
            if stage is not None or status is not None:
                current = None
                if stage is None or status is None:
                    current = self.get_workflow(workflow_id)

                stage_value = stage.value if stage else (current.get("stage") if current else None)
                status_value = status.value if status else (current.get("status") if current else None)

                if stage_value and status_value:
                    self._record_history(
                        workflow_id,
                        stage_value,
                        status_value,
                        data
                    )

            return True

        except Exception as e:
            logger.error(f"[StateStore] Failed to update workflow: {e}")
            return False

    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow by ID"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,)).fetchone()

            if row:
                return self._row_to_dict(row)
            return None

    def get_workflows_by_stage(self, stage: WorkflowStage) -> List[Dict]:
        """Get all workflows in a specific stage"""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM workflows WHERE stage = ? ORDER BY created_at DESC",
                (stage.value,)
            ).fetchall()

            return [self._row_to_dict(row) for row in rows]

    def get_workflows_by_status(self, status: WorkflowStatus) -> List[Dict]:
        """Get all workflows with a specific status"""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM workflows WHERE status = ? ORDER BY created_at DESC",
                (status.value,)
            ).fetchall()

            return [self._row_to_dict(row) for row in rows]

    def get_active_workflows(self) -> List[Dict]:
        """Get all active (in_progress) workflows"""
        return self.get_workflows_by_status(WorkflowStatus.IN_PROGRESS)

    def get_recent_workflows(self, limit: int = 10) -> List[Dict]:
        """Get recent workflows"""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM workflows ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()

            return [self._row_to_dict(row) for row in rows]

    def get_workflow_history(self, workflow_id: str, limit: int = 50) -> List[Dict]:
        """Get workflow state history"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM state_history
                WHERE workflow_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (workflow_id, limit)).fetchall()

            return [self._row_to_dict(row) for row in rows]

    # ========== Payload Methods ==========

    def save_payload(self, payload_id: str, use_case: str, domain: str,
                     complexity: str, model: str, payload_data: Dict) -> bool:
        """Save architect payload"""
        try:
            now = asyncio.get_event_loop().time()

            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO payloads
                    (id, use_case, domain, complexity, model, created_at, data, prd, spec_contract)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    payload_id,
                    use_case,
                    domain,
                    complexity,
                    model,
                    now,
                    json.dumps(payload_data),
                    json.dumps(payload_data.get("prd")),
                    json.dumps(payload_data.get("spec_contract"))
                ))

            return True

        except Exception as e:
            logger.error(f"[StateStore] Failed to save payload: {e}")
            return False

    def get_payload(self, payload_id: str) -> Optional[Dict]:
        """Get payload by ID"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM payloads WHERE id = ?", (payload_id,)).fetchone()

            if row:
                return self._row_to_dict(row)
            return None

    # ========== Agent Methods ==========

    def save_agent(self, agent_id: str, payload_id: str, name: str,
                   model: str, tools: List[str], agent_data: Dict) -> bool:
        """Save builder agent"""
        try:
            now = asyncio.get_event_loop().time()

            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO agents
                    (id, payload_id, name, model, tools, status, created_at, data, script_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    agent_id,
                    payload_id,
                    name,
                    model,
                    json.dumps(tools),
                    agent_data.get("status", "ready"),
                    now,
                    json.dumps(agent_data),
                    agent_data.get("script_path")
                ))

            return True

        except Exception as e:
            logger.error(f"[StateStore] Failed to save agent: {e}")
            return False

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent by ID"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()

            if row:
                return self._row_to_dict(row)
            return None

    def get_agents_by_payload(self, payload_id: str) -> List[Dict]:
        """Get all agents for a payload"""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM agents WHERE payload_id = ? ORDER BY created_at DESC",
                (payload_id,)
            ).fetchall()

            return [self._row_to_dict(row) for row in rows]

    # ========== Execution Methods ==========

    def save_execution(self, execution_id: str, agent_id: str, task: str,
                       status: str, logs: List[str], result: Optional[str] = None,
                       error: Optional[str] = None) -> bool:
        """Save engine execution"""
        try:
            now = asyncio.get_event_loop().time()

            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO executions (id, agent_id, task, status, started_at, logs, result, error)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution_id,
                    agent_id,
                    task,
                    status,
                    now,
                    json.dumps(logs),
                    result,
                    error
                ))

            return True

        except Exception as e:
            logger.error(f"[StateStore] Failed to save execution: {e}")
            return False

    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get execution by ID"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM executions WHERE id = ?", (execution_id,)).fetchone()

            if row:
                return self._row_to_dict(row)
            return None

    def get_executions_by_agent(self, agent_id: str, limit: int = 20) -> List[Dict]:
        """Get recent executions for an agent"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM executions
                WHERE agent_id = ?
                ORDER BY started_at DESC
                LIMIT ?
            """, (agent_id, limit)).fetchall()

            return [self._row_to_dict(row) for row in rows]

    # ========== Utility Methods ==========

    def _record_history(self, workflow_id: str, stage: Optional[str],
                        status: Optional[str], data: Optional[Dict]):
        """Record state change in history"""
        try:
            now = asyncio.get_event_loop().time()

            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO state_history (workflow_id, stage, status, timestamp, data)
                    VALUES (?, ?, ?, ?, ?)
                """, (workflow_id, stage, status, now, json.dumps(data) if data else None))

        except Exception as e:
            logger.error(f"[StateStore] Failed to record history: {e}")

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert database row to dictionary"""
        result = {}
        for key in row.keys():
            value = row[key]
            # Parse JSON fields
            if key in ["data", "prd", "spec_contract", "tools", "logs"]:
                try:
                    result[key] = json.loads(value) if value else None
                except:
                    result[key] = value
            else:
                result[key] = value
        return result

    def cleanup_old_records(self, days: int = 30):
        """
        Delete records older than specified days.

        Args:
            days: Number of days to keep
        """
        try:
            cutoff = asyncio.get_event_loop().time() - (days * 24 * 60 * 60)

            with self._get_connection() as conn:
                # Delete old workflows
                conn.execute("DELETE FROM workflows WHERE created_at < ?", (cutoff,))

                # Delete old history
                conn.execute("DELETE FROM state_history WHERE timestamp < ?", (cutoff,))

                # Delete old executions
                conn.execute("DELETE FROM executions WHERE started_at < ?", (cutoff,))

            logger.info(f"[StateStore] Cleaned up records older than {days} days")

        except Exception as e:
            logger.error(f"[StateStore] Cleanup failed: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self._get_connection() as conn:
            workflows_count = conn.execute("SELECT COUNT(*) FROM workflows").fetchone()[0]
            payloads_count = conn.execute("SELECT COUNT(*) FROM payloads").fetchone()[0]
            agents_count = conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
            executions_count = conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0]
            history_count = conn.execute("SELECT COUNT(*) FROM state_history").fetchone()[0]

            # Get stage distribution
            stages = conn.execute("""
                SELECT stage, COUNT(*) as count
                FROM workflows
                GROUP BY stage
            """).fetchall()

            stage_distribution = {row[0]: row[1] for row in stages}

            return {
                "total_workflows": workflows_count,
                "total_payloads": payloads_count,
                "total_agents": agents_count,
                "total_executions": executions_count,
                "total_history_records": history_count,
                "stage_distribution": stage_distribution,
                "db_size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "db_path": str(self.db_path)
            }

# Singleton instance
_store: Optional[StateStore] = None

def get_state_store() -> StateStore:
    """Get singleton state store instance"""
    global _store
    if _store is None:
        _store = StateStore()
    return _store
