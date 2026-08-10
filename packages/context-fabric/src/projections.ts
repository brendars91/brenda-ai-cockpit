import type { Event } from '@cockpit/contracts';

// ── Projection State Types ──

export interface SessionProjection {
  readonly id: string;
  readonly status: string;
  readonly adapter: string;
  readonly agentName: string;
  readonly model: string;
  readonly worktree: string;
  readonly taskId?: string;
  readonly exitCode?: number;
  readonly outputCount: number;
  readonly lastOutput?: string;
}

export interface TaskProjection {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly priority: string;
  readonly parentId?: string;
  readonly status: string;
  readonly agentId?: string;
  readonly adapter?: string;
  readonly sessionId?: string;
  readonly result?: string;
}

export interface AgentProjection {
  readonly id: string;
  readonly name: string;
  readonly adapter: string;
  readonly capabilities: readonly string[];
  readonly model: string;
  readonly status: string;
  readonly latency?: number;
}

export interface RunProjection {
  readonly id: string;
  readonly taskId: string;
  readonly sessionId: string;
  readonly adapter: string;
  readonly contextPacketHash: string;
  readonly percent?: number;
  readonly message?: string;
  readonly exitCode?: number;
  readonly status: string;
}

export interface IssueProjection {
  readonly id: string;
  readonly issueId: string;
  readonly title: string;
  readonly status: string;
  readonly priority: string;
  readonly assignee?: string;
  readonly commentCount: number;
}

export interface KnowledgeProjection {
  readonly id: string;
  readonly path: string;
  readonly content: string;
  readonly level: string;
}

export interface SystemProjection {
  readonly frozen: boolean;
  readonly freezeReason?: string;
  readonly quotaWarnings: Record<string, { remaining: number; windowEndsAt: string }>;
  readonly quotaExhausted: readonly string[];
}

export interface ProjectedState {
  readonly sessions: Record<string, SessionProjection>;
  readonly tasks: Record<string, TaskProjection>;
  readonly agents: Record<string, AgentProjection>;
  readonly runs: Record<string, RunProjection>;
  readonly issues: Record<string, IssueProjection>;
  readonly knowledge: Record<string, KnowledgeProjection>;
  readonly system: SystemProjection;
}

// ── Factory ──

export function emptyProjectedState(): ProjectedState {
  return {
    sessions: {},
    tasks: {},
    agents: {},
    runs: {},
    issues: {},
    knowledge: {},
    system: {
      frozen: false,
      quotaWarnings: {},
      quotaExhausted: [],
    },
  };
}

// ── Reducer ──

/** Immutable reducer: applies an event to the state, returning new state. */
export function reduceEvent(state: ProjectedState, event: Event): ProjectedState {
  switch (event.eventType) {
    // ── Session events ──
    case 'session.created': {
      const e = event;
      const session: SessionProjection = {
        id: e.aggregateId,
        status: 'created',
        adapter: e.adapter,
        agentName: e.agentName,
        model: e.model,
        worktree: e.worktree,
        outputCount: 0,
      };
      return { ...state, sessions: { ...state.sessions, [e.aggregateId]: session } };
    }
    case 'session.started': {
      const e = event;
      const existing = state.sessions[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        sessions: {
          ...state.sessions,
          [e.aggregateId]: {
            ...existing,
            status: 'started',
            taskId: e.taskId,
          },
        },
      };
    }
    case 'session.output': {
      const e = event;
      const existing = state.sessions[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        sessions: {
          ...state.sessions,
          [e.aggregateId]: {
            ...existing,
            outputCount: existing.outputCount + 1,
            lastOutput: e.content,
          },
        },
      };
    }
    case 'session.completed': {
      const e = event;
      const existing = state.sessions[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        sessions: {
          ...state.sessions,
          [e.aggregateId]: {
            ...existing,
            status: 'completed',
            exitCode: e.exitCode,
          },
        },
      };
    }
    case 'session.failed': {
      const e = event;
      const existing = state.sessions[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        sessions: {
          ...state.sessions,
          [e.aggregateId]: {
            ...existing,
            status: 'failed',
            exitCode: e.exitCode,
          },
        },
      };
    }
    case 'session.approval_requested': {
      const existing = state.sessions[event.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        sessions: {
          ...state.sessions,
          [event.aggregateId]: { ...existing, status: 'approval_requested' },
        },
      };
    }
    case 'session.approval_resolved': {
      const e = event;
      const existing = state.sessions[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        sessions: {
          ...state.sessions,
          [e.aggregateId]: { ...existing, status: 'approval_resolved' },
        },
      };
    }

    // ── Task events ──
    case 'task.created': {
      const e = event;
      const task: TaskProjection = {
        id: e.aggregateId,
        title: e.title,
        description: e.description,
        priority: e.priority,
        parentId: e.parentId,
        status: 'created',
      };
      return { ...state, tasks: { ...state.tasks, [e.aggregateId]: task } };
    }
    case 'task.assigned': {
      const e = event;
      const existing = state.tasks[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        tasks: {
          ...state.tasks,
          [e.aggregateId]: {
            ...existing,
            status: 'assigned',
            agentId: e.agentId,
            adapter: e.adapter,
          },
        },
      };
    }
    case 'task.started': {
      const e = event;
      const existing = state.tasks[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        tasks: {
          ...state.tasks,
          [e.aggregateId]: {
            ...existing,
            status: 'started',
            sessionId: e.sessionId,
          },
        },
      };
    }
    case 'task.completed': {
      const e = event;
      const existing = state.tasks[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        tasks: {
          ...state.tasks,
          [e.aggregateId]: { ...existing, status: 'completed', result: e.result },
        },
      };
    }
    case 'task.failed': {
      const existing = state.tasks[event.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        tasks: {
          ...state.tasks,
          [event.aggregateId]: { ...existing, status: 'failed' },
        },
      };
    }

    // ── Agent events ──
    case 'agent.registered': {
      const e = event;
      const agent: AgentProjection = {
        id: e.aggregateId,
        name: e.name,
        adapter: e.adapter,
        capabilities: e.capabilities,
        model: e.model,
        status: 'registered',
      };
      return { ...state, agents: { ...state.agents, [e.aggregateId]: agent } };
    }
    case 'agent.health_checked': {
      const e = event;
      const existing = state.agents[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        agents: {
          ...state.agents,
          [e.aggregateId]: {
            ...existing,
            status: e.status,
            latency: e.latency,
          },
        },
      };
    }
    case 'agent.quota_consumed': {
      // No projection mutation needed beyond maybe tracking usage
      return state;
    }

    // ── Run events ──
    case 'run.created': {
      const e = event;
      const run: RunProjection = {
        id: e.aggregateId,
        taskId: e.taskId,
        sessionId: e.sessionId,
        adapter: e.adapter,
        contextPacketHash: e.contextPacketHash,
        status: 'created',
      };
      return { ...state, runs: { ...state.runs, [e.aggregateId]: run } };
    }
    case 'run.progress': {
      const e = event;
      const existing = state.runs[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        runs: {
          ...state.runs,
          [e.aggregateId]: {
            ...existing,
            percent: e.percent,
            message: e.message,
          },
        },
      };
    }
    case 'run.diff_produced': {
      // No state mutation needed for diff produced
      return state;
    }
    case 'run.completed': {
      const e = event;
      const existing = state.runs[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        runs: {
          ...state.runs,
          [e.aggregateId]: {
            ...existing,
            status: 'completed',
            exitCode: e.exitCode,
          },
        },
      };
    }

    // ── Issue events ──
    case 'issue.created': {
      const e = event;
      const issue: IssueProjection = {
        id: e.aggregateId,
        issueId: e.issueId,
        title: e.title,
        status: e.status,
        priority: e.priority,
        assignee: e.assignee,
        commentCount: 0,
      };
      return { ...state, issues: { ...state.issues, [e.aggregateId]: issue } };
    }
    case 'issue.status_changed': {
      const e = event;
      const existing = state.issues[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        issues: {
          ...state.issues,
          [e.aggregateId]: { ...existing, status: e.to },
        },
      };
    }
    case 'issue.comment_added': {
      const existing = state.issues[event.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        issues: {
          ...state.issues,
          [event.aggregateId]: {
            ...existing,
            commentCount: existing.commentCount + 1,
          },
        },
      };
    }
    case 'approval.requested': {
      // Could be tracked separately; minimal handling for now
      return state;
    }
    case 'approval.resolved': {
      return state;
    }

    // ── Knowledge events ──
    case 'knowledge.created': {
      const e = event;
      const entry: KnowledgeProjection = {
        id: e.aggregateId,
        path: e.path,
        content: e.content,
        level: e.level,
      };
      return {
        ...state,
        knowledge: { ...state.knowledge, [e.aggregateId]: entry },
      };
    }
    case 'knowledge.promoted': {
      const e = event;
      const existing = state.knowledge[e.aggregateId];
      if (!existing) return state;
      return {
        ...state,
        knowledge: {
          ...state.knowledge,
          [e.aggregateId]: { ...existing, level: e.to },
        },
      };
    }
    case 'knowledge.drift_detected': {
      return state;
    }

    // ── Policy events ──
    case 'policy.evaluated': {
      return state;
    }

    // ── System events ──
    case 'system.freeze_activated': {
      const e = event;
      return {
        ...state,
        system: { ...state.system, frozen: true, freezeReason: e.reason },
      };
    }
    case 'system.freeze_deactivated': {
      return {
        ...state,
        system: {
          ...state.system,
          frozen: false,
          freezeReason: undefined,
        },
      };
    }
    case 'system.quota_warning': {
      const e = event;
      return {
        ...state,
        system: {
          ...state.system,
          quotaWarnings: {
            ...state.system.quotaWarnings,
            [e.provider]: {
              remaining: e.remaining,
              windowEndsAt: e.windowEndsAt,
            },
          },
        },
      };
    }
    case 'system.quota_exhausted': {
      const e = event;
      return {
        ...state,
        system: {
          ...state.system,
          quotaExhausted: [...state.system.quotaExhausted, e.provider],
        },
      };
    }

    default: {
      // Exhaustive check – if a new event type is added, we'll see it here
      const _exhaustive: never = event;
      return state;
    }
  }
}

/** Project an array of events into a final state. */
export function projectEvents(events: readonly Event[]): ProjectedState {
  let state = emptyProjectedState();
  for (const event of events) {
    state = reduceEvent(state, event);
  }
  return state;
}

/**
 * Select a canonical representation for hashing.
 * Omits potentially volatile fields to ensure stable hashes.
 */
export function selectCanonicalProjection(state: ProjectedState): unknown {
  return {
    sessions: state.sessions,
    tasks: state.tasks,
    agents: state.agents,
    runs: state.runs,
    issues: state.issues,
    knowledge: state.knowledge,
    system: {
      frozen: state.system.frozen,
      freezeReason: state.system.freezeReason,
      quotaWarnings: state.system.quotaWarnings,
      quotaExhausted: state.system.quotaExhausted,
    },
  };
}
