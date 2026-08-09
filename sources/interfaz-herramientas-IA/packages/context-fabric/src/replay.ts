import { hashProjectionState } from './hash.js';
import { projectEvents, selectCanonicalProjection } from './projections.js';

import type { EventLog } from './event-log.js';
import type { ProjectedState } from './projections.js';
import type { Event } from '@cockpit/contracts';

/** Replay the full event log from scratch and return projected state. */
export function replayFromEventLog(eventLog: EventLog): ProjectedState {
  const storedEvents = eventLog.getEvents();
  const events: Event[] = storedEvents.map((stored) => {
    const base = {
      eventId: stored.eventId,
      eventType: stored.eventType,
      aggregateId: stored.aggregateId,
      aggregateType: stored.aggregateType,
      version: stored.version as 1,
      timestamp: stored.timestamp,
      metadata: stored.metadata,
    };
    return { ...base, ...stored.payload } as unknown as Event;
  });
  return projectEvents(events);
}

/**
 * Verify deterministic replay: project events twice and compare hashes.
 * Returns comparison result.
 */
export function verifyDeterministicReplay(eventLog: EventLog): {
  deterministic: boolean;
  firstHash: string;
  secondHash: string;
} {
  const first = replayFromEventLog(eventLog);
  const firstHash = hashProjectionState(selectCanonicalProjection(first));

  const second = replayFromEventLog(eventLog);
  const secondHash = hashProjectionState(selectCanonicalProjection(second));

  return {
    deterministic: firstHash === secondHash,
    firstHash,
    secondHash,
  };
}

/** Replay up to a given sequence number for time-travel queries. */
export function replayToSequence(eventLog: EventLog, sequence: number): ProjectedState {
  const storedEvents = eventLog.getEvents({ afterSequence: 0, limit: sequence });
  const events: Event[] = storedEvents.map((stored) => {
    const base = {
      eventId: stored.eventId,
      eventType: stored.eventType,
      aggregateId: stored.aggregateId,
      aggregateType: stored.aggregateType,
      version: stored.version as 1,
      timestamp: stored.timestamp,
      metadata: stored.metadata,
    };
    return { ...base, ...stored.payload } as unknown as Event;
  });
  return projectEvents(events);
}
