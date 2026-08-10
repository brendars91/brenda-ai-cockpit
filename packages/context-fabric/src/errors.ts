/** Custom error hierarchy for @cockpit/context-fabric */

export class ContextFabricError extends Error {
  public constructor(message: string) {
    super(message);
    this.name = 'ContextFabricError';
  }
}

export class DuplicateEventError extends ContextFabricError {
  public constructor(eventId: string) {
    super(`Duplicate event_id: ${eventId}`);
    this.name = 'DuplicateEventError';
  }
}

export class HashChainError extends ContextFabricError {
  public constructor(message: string) {
    super(message);
    this.name = 'HashChainError';
  }
}

export class ProjectionError extends ContextFabricError {
  public constructor(message: string) {
    super(message);
    this.name = 'ProjectionError';
  }
}
