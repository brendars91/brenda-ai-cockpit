#!/usr/bin/env python3
"""Generate real telemetry snapshots from Hermes databases.
Produces sanitized JSON snapshots (metadata only, no message content)."""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

HOME = "/home/ubuntu/.hermes"
OUT = Path("/home/ubuntu/brenda-domain-repos/brenda-ai-cockpit/packages/telemetry-reader/src/snapshots")
OUT.mkdir(parents=True, exist_ok=True)

def safe_json_query(db_path, query, params=()):
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()
        result = [dict(r) for r in rows]
        conn.close()
        return result
    except Exception as e:
        return {"error": str(e)}

# 1. Session forensics
sessions = safe_json_query(f"{HOME}/state.db", """
    SELECT id, source, model, started_at, ended_at, message_count, tool_call_count,
           input_tokens, output_tokens, reasoning_tokens, billing_provider,
           estimated_cost_usd, title, chat_type, profile_name
    FROM sessions ORDER BY started_at DESC LIMIT 200
""")
Path(OUT / "sessions.json").write_text(json.dumps(sessions, indent=2, default=str))

# 2. Cost intelligence
cost_rows = safe_json_query(f"{HOME}/state.db", """
    SELECT model, billing_provider,
           COUNT(*) as session_count,
           SUM(input_tokens) as total_input_tokens,
           SUM(output_tokens) as total_output_tokens,
           SUM(reasoning_tokens) as total_reasoning_tokens,
           SUM(estimated_cost_usd) as total_cost,
           AVG(input_tokens) as avg_input_per_session,
           AVG(output_tokens) as avg_output_per_session
    FROM sessions WHERE model IS NOT NULL
    GROUP BY model ORDER BY total_input_tokens DESC
""")
Path(OUT / "cost-intelligence.json").write_text(json.dumps(cost_rows, indent=2, default=str))

# 3. Tool analytics
tools = safe_json_query(f"{HOME}/state.db", """
    SELECT tool_name, COUNT(*) as call_count,
           COUNT(DISTINCT session_id) as sessions_used_in
    FROM messages WHERE tool_name IS NOT NULL
    GROUP BY tool_name ORDER BY call_count DESC
""")
Path(OUT / "tool-analytics.json").write_text(json.dumps(tools, indent=2, default=str))

# 4. Cron health
crons = safe_json_query(f"{HOME}/cron/executions.db", """
    SELECT status, COUNT(*) as count FROM executions GROUP BY status
""")
Path(OUT / "cron-health.json").write_text(json.dumps(crons, indent=2, default=str))

# 5. Evidence ledger
evidence = safe_json_query(f"{HOME}/verification_evidence.db", """
    SELECT id, created_at, session_id, command, canonical_command, kind
    FROM verification_events ORDER BY created_at DESC
""")
Path(OUT / "evidence-ledger.json").write_text(json.dumps(evidence, indent=2, default=str))

# 6. Memory observatory
memory = safe_json_query(f"{HOME}/memory_store.db", """
    SELECT fact_id, content, category, trust_score, tags FROM facts ORDER BY fact_id
""")
Path(OUT / "memory-observatory.json").write_text(json.dumps(memory, indent=2, default=str))

# Summary
summary = {
    "generated_at": datetime.now().isoformat(),
    "total_sessions": len(sessions) if isinstance(sessions, list) else 0,
    "total_cost_tracked": sum(r.get("total_cost") or 0 for r in cost_rows) if isinstance(cost_rows, list) else 0,
    "total_tool_calls": sum(r.get("call_count", 0) for r in tools) if isinstance(tools, list) else 0,
    "total_cron_executions": sum(r.get("count", 0) for r in crons) if isinstance(crons, list) else 0,
    "total_evidence_events": len(evidence) if isinstance(evidence, list) else 0,
    "total_facts": len(memory) if isinstance(memory, list) else 0,
}
Path(OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))

print(f"Snapshots generated:")
print(json.dumps(summary, indent=2))
