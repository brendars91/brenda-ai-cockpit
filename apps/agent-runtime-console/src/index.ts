import { adapters, type AdapterHealth, type AdapterId } from '@cockpit/adapters';
import { evaluatePolicy, type RiskLevel } from '@cockpit/policy';

export type RuntimeStatus = 'idle' | 'running' | 'error' | 'degraded';

export interface RuntimeAgentStatus {
  readonly agent_id: AdapterId;
  readonly display_name: string;
  readonly status: RuntimeStatus;
  readonly health: AdapterHealth;
  readonly capabilities: readonly string[];
  readonly last_heartbeat: string;
}

export interface RuntimeCommand {
  readonly agent_id: AdapterId;
  readonly action: 'read' | 'execute' | 'modify' | 'delete' | 'deploy';
  readonly target: string;
  readonly risk: RiskLevel;
  readonly requested_by: string;
  readonly approvals?: readonly string[];
}

export function listRuntimeAgents(now: Date = new Date()): readonly RuntimeAgentStatus[] {
  return adapters.map((adapter) => ({
    agent_id: adapter.id,
    display_name: adapter.displayName,
    status: adapter.defaultHealth === 'available' ? 'idle' : 'degraded',
    health: adapter.defaultHealth,
    capabilities: adapter.capabilities,
    last_heartbeat: now.toISOString(),
  }));
}

export function authorizeRuntimeCommand(command: RuntimeCommand) {
  return evaluatePolicy({
    principal: { id: command.requested_by, role: command.requested_by === 'brenda' ? 'owner' : 'operator' },
    action: command.action,
    target: command.target,
    risk: command.risk,
    approvals: command.approvals,
  });
}
