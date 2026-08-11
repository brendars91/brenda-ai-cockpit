export type RiskLevel = 'R0' | 'R1' | 'R2' | 'R3' | 'R4';
export type PrincipalRole = 'owner' | 'operator' | 'viewer' | 'agent';
export type PolicyDecisionKind = 'allow' | 'deny' | 'require_approval';

export interface Principal { readonly id: string; readonly role: PrincipalRole; }
export interface TaskPolicyRequest {
  readonly principal: Principal;
  readonly action: 'read' | 'execute' | 'modify' | 'delete' | 'deploy' | 'credential_access';
  readonly target: string;
  readonly risk: RiskLevel;
  readonly approvals?: readonly string[];
}
export interface PolicyDecision { readonly decision: PolicyDecisionKind; readonly reason: string; readonly requiredApproval?: 'owner' | 'human_operator'; }

const roleRank: Record<PrincipalRole, number> = { viewer: 0, agent: 1, operator: 2, owner: 3 };
const riskRank: Record<RiskLevel, number> = { R0: 0, R1: 1, R2: 2, R3: 3, R4: 4 };

export function evaluatePolicy(request: TaskPolicyRequest): PolicyDecision {
  if (!request.principal.id.trim()) return { decision: 'deny', reason: 'principal id is required' };
  if (!request.target.trim()) return { decision: 'deny', reason: 'target is required' };
  if (request.action === 'credential_access') return { decision: 'deny', reason: 'credential access is outside cockpit automation authority' };
  if (request.action === 'delete' || request.action === 'deploy') {
    if (request.principal.role !== 'owner') return { decision: 'require_approval', reason: `${request.action} requires owner approval`, requiredApproval: 'owner' };
    if (!request.approvals?.includes(request.principal.id)) return { decision: 'require_approval', reason: 'owner approval receipt missing', requiredApproval: 'owner' };
  }
  if (riskRank[request.risk] >= 3 && !request.approvals?.length) return { decision: 'require_approval', reason: `${request.risk} requires explicit approval`, requiredApproval: 'human_operator' };
  if (request.action === 'read') return { decision: 'allow', reason: 'read access allowed' };
  if (roleRank[request.principal.role] < roleRank.operator) return { decision: 'deny', reason: `${request.principal.role} cannot ${request.action}` };
  return { decision: 'allow', reason: 'policy constraints satisfied' };
}
