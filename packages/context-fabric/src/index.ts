// @cockpit/context-fabric — Event-sourced canon with deterministic replay

export { createDatabase, initializeDatabase, closeDatabase } from './database.js';
export { EventLog } from './event-log.js';
export type { StoredEvent } from './event-log.js';
export { IdempotencyStore } from './idempotency-store.js';
export { ProjectionEngine } from './projection-engine.js';
export {
  emptyProjectedState,
  reduceEvent,
  projectEvents,
  selectCanonicalProjection,
} from './projections.js';
export type {
  ProjectedState,
  SessionProjection,
  TaskProjection,
  AgentProjection,
  RunProjection,
  IssueProjection,
  KnowledgeProjection,
  SystemProjection,
} from './projections.js';
export { replayFromEventLog, verifyDeterministicReplay, replayToSequence } from './replay.js';
export { canonicalJson, sha256, hashEvent, hashProjectionState } from './hash.js';
export {
  ContextFabricError,
  DuplicateEventError,
  HashChainError,
  ProjectionError,
} from './errors.js';
