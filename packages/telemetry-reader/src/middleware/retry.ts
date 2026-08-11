export interface RetryOptions {
  readonly maxAttempts?: number;
  readonly baseDelayMs?: number;
  readonly factor?: number;
  readonly retryable?: (error: unknown) => boolean;
}

export interface RetryAttempt {
  readonly attempt: number;
  readonly delayMs: number;
  readonly error: unknown;
}

export class RetryMiddleware {
  public readonly attempts: RetryAttempt[] = [];

  public async execute<T>(operation: () => Promise<T> | T, options: RetryOptions = {}): Promise<T> {
    const maxAttempts = Math.max(1, options.maxAttempts ?? 3);
    const baseDelayMs = Math.max(0, options.baseDelayMs ?? 100);
    const factor = Math.max(1, options.factor ?? 2);
    const retryable = options.retryable ?? (() => true);

    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      try {
        return await operation();
      } catch (error) {
        if (attempt >= maxAttempts || !retryable(error)) {
          throw error;
        }
        const delayMs = Math.round(baseDelayMs * factor ** (attempt - 1));
        this.attempts.push({ attempt, delayMs, error });
        await new Promise((resolve) => setTimeout(resolve, delayMs));
      }
    }
    throw new Error('retry middleware reached unreachable state');
  }
}

export const telemetryRetry = new RetryMiddleware();
