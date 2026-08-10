import { RetryMiddleware } from './retry';
import { readSessions, readCosts, readTools, readCron, readEvidence, readMemory } from './readers';

export class TelemetryRetryMiddleware {
  private readonly retry = new RetryMiddleware();
  private readonly maxRetries = 3;

  async readSessions(dbPath: string = '/home/ubuntu/.hermes/state.db', limit = 100): Promise<any> {
    return this.retry.execute(() => readSessions(dbPath, limit), {
      maxAttempts: this.maxRetries,
      baseDelay: 300,
      factor: 2,
    });
  }

  async readCosts(dbPath: string = '/home/ubuntu/.hermes/state.db'): Promise<any> {
    return this.retry.execute(() => readCosts(dbPath), {
      maxAttempts: this.maxRetries,
      baseDelay: 300,
      factor: 2,
    });
  }

  async readTools(dbPath: string = '/home/ubuntu/.hermes/state.db') {
    return this.retry.execute(() => readTools(dbPath), {
      maxAttempts: this.maxRetries,
      baseDelay: 300,
      factor: 2,
    });
  }

  async readCron(dbPath: string = '/home/ubuntu/.hermes/cron/executions.db') {
    return this.retry.execute(() => readCron(dbPath), {
      maxAttempts: this.maxRetries,
      baseDelay: 300,
      factor: 2,
    });
  }

  async readEvidence(dbPath: string = '/home/ubuntu/.hermes/verification_evidence.db') {
    return this.retry.execute(() => readEvidence(dbPath), {
      maxAttempts: this.maxRetries,
      baseDelay: 300,
      factor: 2,
    });
  }

  async readMemory(dbPath: string = '/home/ubuntu/.hermes/memory_store.db') {
    return this.retry.execute(() => readMemory(dbPath), {
      maxAttempts: this.maxRetries,
      baseDelay: 300,
      factor: 2,
    });
  }

  // New hook for pre-tool-call retry
  async readToolCall(path: string): Promise<any> {
    return this.retry.execute(async () => {
      // Simulate a tool call with potential failure
      const db = new Database(dbPath, { readonly: true, fileMustExist: true });
      try {
        const result = await readSessions(dbPath, 1);
        return { success: true, data: result };
      } catch (error) {
        // Simulate transient failure
        throw error;
      } finally {
        db.close();
      }
    });
  }
}

export const telemetryRetry = new TelemetryRetryMiddleware();