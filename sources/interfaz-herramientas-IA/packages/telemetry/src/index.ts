import pino, { type Logger } from 'pino';

export type TelemetryAttributeValue =
  | string
  | number
  | boolean
  | null
  | readonly TelemetryAttributeValue[]
  | TelemetryAttributes;

export interface TelemetryAttributes {
  readonly [key: string]: TelemetryAttributeValue;
}

export interface SpanStatus {
  readonly code: 0 | 1 | 2;
  readonly message?: string;
}

export interface SpanEvent {
  readonly name: string;
  readonly attributes?: TelemetryAttributes;
  readonly timestamp: string;
}

export interface FinishedSpan {
  readonly name: string;
  readonly attributes: TelemetryAttributes;
  readonly startedAt: string;
  readonly endedAt: string;
  readonly status: SpanStatus;
  readonly events: readonly SpanEvent[];
}

export interface ActiveSpan {
  setAttribute(key: string, value: TelemetryAttributeValue): void;
  addEvent(name: string, attributes?: TelemetryAttributes): void;
  setStatus(status: SpanStatus): void;
}

export interface SpanExporter {
  exportSpan(span: FinishedSpan): void;
}

export interface CounterSample {
  readonly name: string;
  readonly value: number;
  readonly attributes?: TelemetryAttributes;
}

export interface HistogramSample {
  readonly name: string;
  readonly value: number;
  readonly attributes?: TelemetryAttributes;
}

export interface MetricSink {
  recordCounter(name: string, value: number, attributes?: TelemetryAttributes): void;
  recordHistogram(name: string, value: number, attributes?: TelemetryAttributes): void;
}

export interface TelemetryOptions {
  readonly serviceName: string;
  readonly spanExporter?: SpanExporter;
  readonly metricSink?: MetricSink;
  readonly logLevel?: 'silent' | 'fatal' | 'error' | 'warn' | 'info' | 'debug' | 'trace';
}

export interface Telemetry {
  readonly logger: Logger;
  withSpan<T>(
    name: string,
    attributes: TelemetryAttributes,
    fn: (span: ActiveSpan) => Promise<T> | T,
  ): Promise<T>;
  recordCounter(name: string, value: number, attributes?: TelemetryAttributes): void;
  recordHistogram(name: string, value: number, attributes?: TelemetryAttributes): void;
  shutdown(): Promise<void>;
}

const SENSITIVE_KEY_PATTERN = /(token|secret|password|apikey|api_key|authorization|credential)/iu;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function redactValue(key: string, value: unknown): TelemetryAttributeValue {
  if (SENSITIVE_KEY_PATTERN.test(key)) {
    return '[REDACTED]';
  }

  if (Array.isArray(value)) {
    return value.map((entry) => redactValue(key, entry));
  }

  if (isRecord(value)) {
    return redactAttributes(value);
  }

  if (
    typeof value === 'string' ||
    typeof value === 'number' ||
    typeof value === 'boolean' ||
    value === null
  ) {
    return value;
  }

  return String(value);
}

export function redactAttributes(attributes: Record<string, unknown>): TelemetryAttributes {
  return Object.fromEntries(
    Object.entries(attributes).map(([key, value]) => [key, redactValue(key, value)]),
  );
}

class SimpleActiveSpan implements ActiveSpan {
  private readonly attributes: Record<string, TelemetryAttributeValue>;
  private readonly eventsList: SpanEvent[];
  private currentStatus: SpanStatus;

  public constructor(initialAttributes: TelemetryAttributes = {}) {
    this.attributes = { ...initialAttributes };
    this.eventsList = [];
    this.currentStatus = { code: 1 };
  }

  public setAttribute(key: string, value: TelemetryAttributeValue): void {
    this.attributes[key] = value;
  }

  public addEvent(name: string, attributes?: TelemetryAttributes): void {
    this.eventsList.push({ name, attributes, timestamp: new Date().toISOString() });
  }

  public setStatus(status: SpanStatus): void {
    this.currentStatus = status;
  }

  public finish(name: string, startedAt: string): FinishedSpan {
    return {
      name,
      attributes: redactAttributes(this.attributes),
      startedAt,
      endedAt: new Date().toISOString(),
      status: this.currentStatus,
      events: [...this.eventsList],
    };
  }
}

export class InMemorySpanExporter implements SpanExporter {
  private readonly spans: FinishedSpan[] = [];

  public exportSpan(span: FinishedSpan): void {
    this.spans.push(span);
  }

  public getFinishedSpans(): readonly FinishedSpan[] {
    return [...this.spans];
  }

  public clear(): void {
    this.spans.length = 0;
  }
}

export class ConsoleSpanExporter implements SpanExporter {
  private readonly spans: FinishedSpan[] = [];

  public exportSpan(span: FinishedSpan): void {
    this.spans.push(span);
  }

  public getSpans(): readonly FinishedSpan[] {
    return [...this.spans];
  }
}

export class InMemoryMetricSink implements MetricSink {
  public readonly counters: CounterSample[] = [];
  public readonly histograms: HistogramSample[] = [];

  public recordCounter(name: string, value: number, attributes?: TelemetryAttributes): void {
    this.counters.push({ name, value, attributes });
  }

  public recordHistogram(name: string, value: number, attributes?: TelemetryAttributes): void {
    this.histograms.push({ name, value, attributes });
  }
}

export function createTelemetry(options: TelemetryOptions): Telemetry {
  const spanExporter = options.spanExporter ?? new ConsoleSpanExporter();
  const metricSink = options.metricSink ?? new InMemoryMetricSink();
  const logger = pino({
    level: options.logLevel ?? 'info',
    base: { service: options.serviceName },
    enabled: options.logLevel !== 'silent',
  });

  return {
    logger,

    async withSpan<T>(
      name: string,
      attributes: TelemetryAttributes,
      fn: (span: ActiveSpan) => Promise<T> | T,
    ): Promise<T> {
      const startedAt = new Date().toISOString();
      const span = new SimpleActiveSpan(redactAttributes(attributes));
      try {
        const result = await fn(span);
        span.setStatus({ code: 1 });
        spanExporter.exportSpan(span.finish(name, startedAt));
        return result;
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        span.addEvent('exception', { message });
        span.setStatus({ code: 2, message });
        spanExporter.exportSpan(span.finish(name, startedAt));
        throw error;
      }
    },

    recordCounter(name: string, value: number, attributes?: TelemetryAttributes): void {
      metricSink.recordCounter(
        name,
        value,
        attributes === undefined ? undefined : redactAttributes(attributes),
      );
    },

    recordHistogram(name: string, value: number, attributes?: TelemetryAttributes): void {
      metricSink.recordHistogram(
        name,
        value,
        attributes === undefined ? undefined : redactAttributes(attributes),
      );
    },

    async shutdown(): Promise<void> {
      await Promise.resolve();
    },
  };
}
