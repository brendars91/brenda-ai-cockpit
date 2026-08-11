export type AdapterId = 'hermes' | 'claude-code' | 'codex' | 'paperclip';
export type AdapterHealth = 'available' | 'degraded' | 'unavailable';
export interface AgentAdapter { readonly id: AdapterId; readonly displayName: string; readonly capabilities: readonly string[]; readonly defaultHealth: AdapterHealth; readonly requiresApprovalFor: readonly string[]; }
export const adapters: readonly AgentAdapter[] = [
  { id: 'hermes', displayName: 'Hermes Agent', capabilities: ['orchestration', 'tools', 'memory', 'cron'], defaultHealth: 'available', requiresApprovalFor: ['destructive_system_change'] },
  { id: 'claude-code', displayName: 'Claude Code', capabilities: ['code_editing', 'review', 'test_repair'], defaultHealth: 'degraded', requiresApprovalFor: ['premium_model_spend'] },
  { id: 'codex', displayName: 'OpenAI Codex', capabilities: ['code_editing', 'refactor', 'terminal'], defaultHealth: 'available', requiresApprovalFor: ['external_write'] },
  { id: 'paperclip', displayName: 'Paperclip', capabilities: ['local_search', 'context_retrieval'], defaultHealth: 'available', requiresApprovalFor: [] },
] as const;
export function getAdapter(id: AdapterId): AgentAdapter { const adapter = adapters.find((candidate) => candidate.id === id); if (!adapter) throw new Error(`Unknown adapter: ${id}`); return adapter; }
export function findAdaptersForCapability(capability: string): readonly AgentAdapter[] { const normalized = capability.trim().toLowerCase(); if (!normalized) return []; return adapters.filter((adapter) => adapter.capabilities.some((item) => item.toLowerCase() === normalized)); }
