/**
 * GovernancePort — interface for issue tracking and approval workflows.
 *
 * Adapters implement this port to provide governance capabilities:
 * creating/updating issues, managing approvals, and listing governance state.
 */

import type {
  AdapterCapabilities,
  ApprovalDecision,
  IdempotencyKey,
  PortHealth,
  RiskLevel,
} from './common.js';

// ── Issue Types ──

export type IssuePriority = 'critical' | 'high' | 'medium' | 'low';

export type IssueStatus =
  | 'backlog'
  | 'todo'
  | 'in_progress'
  | 'blocked'
  | 'review'
  | 'done'
  | 'cancelled';

export interface GovernanceIssue {
  readonly issueId: string;
  readonly title: string;
  readonly body: string;
  readonly status: IssueStatus;
  readonly priority: IssuePriority;
  readonly assignee?: string;
  readonly labels: readonly string[];
  readonly createdAt: string;
  readonly updatedAt: string;
}

// ── Issue Requests ──

export interface CreateIssueRequest {
  readonly title: string;
  readonly body: string;
  readonly priority: IssuePriority;
  readonly assignee?: string;
  readonly labels?: readonly string[];
  readonly idempotencyKey: IdempotencyKey;
}

export interface UpdateIssueRequest {
  readonly issueId: string;
  readonly status?: IssueStatus;
  readonly assignee?: string;
  readonly labels?: readonly string[];
  readonly idempotencyKey: IdempotencyKey;
}

// ── Approval Types ──

export interface Approval {
  readonly approvalId: string;
  readonly targetId: string;
  readonly targetType: string;
  readonly action: string;
  readonly risk: RiskLevel;
  readonly decision: ApprovalDecision;
  readonly requestedAt: string;
  readonly resolvedAt?: string;
  readonly resolvedBy?: string;
  readonly reason?: string;
}

export interface CreateApprovalRequest {
  readonly targetId: string;
  readonly targetType: string;
  readonly action: string;
  readonly risk: RiskLevel;
  readonly idempotencyKey: IdempotencyKey;
}

export interface ResolveGovernanceApprovalRequest {
  readonly approvalId: string;
  readonly approved: boolean;
  readonly by: string;
  readonly reason?: string;
  readonly idempotencyKey: IdempotencyKey;
}

// ── Port Interface ──

export interface GovernancePort {
  readonly adapterName: string;
  readonly capabilities: AdapterCapabilities;

  healthCheck(): Promise<PortHealth>;
  createIssue(request: CreateIssueRequest): Promise<GovernanceIssue>;
  updateIssue(request: UpdateIssueRequest): Promise<GovernanceIssue>;
  getIssue(issueId: string): Promise<GovernanceIssue>;
  listIssues(status?: IssueStatus): Promise<readonly GovernanceIssue[]>;
  createApproval(request: CreateApprovalRequest): Promise<Approval>;
  resolveApproval(request: ResolveGovernanceApprovalRequest): Promise<Approval>;
  listApprovals(decision?: ApprovalDecision): Promise<readonly Approval[]>;
}
