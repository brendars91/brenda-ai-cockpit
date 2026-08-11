import { describe, expect, it } from 'vitest';

import {
  ConsoleSpanExporter,
  createTelemetry,
  InMemoryMetricSink,
  InMemorySpanExporter,
  redactAttributes,
} from '../src/index.js';

describe('@cockpit/telemetry', () => {
  it('records a command span with deterministic attributes', async () => {
    const spanExporter = new InMemorySpanExporter();
    const metrics = new InMemoryMetricSink();
    const telemetry = createTelemetry({
      serviceName: 'cockpit-test',
      spanExporter,
      metricSink: metrics,
      logLevel: 'silent',
    });

    const result = await telemetry.withSpan(
      'command.execute',
      {
        'cockpit.command_type': 'task.create',
        'cockpit.idempotency_key': 'idem-1',
      },
      async (span) => {
        span.setAttribute('cockpit.aggregate_id', 'task-1');
        telemetry.recordCounter('commands.executed', 1, { commandType: 'task.create' });
        return 'ok';
      },
    );

    await telemetry.shutdown();

    expect(result).toBe('ok');
    expect(spanExporter.getFinishedSpans()).toHaveLength(1);
    expect(spanExporter.getFinishedSpans()[0]?.name).toBe('command.execute');
    expect(spanExporter.getFinishedSpans()[0]?.attributes).toMatchObject({
      'cockpit.command_type': 'task.create',
      'cockpit.idempotency_key': 'idem-1',
      'cockpit.aggregate_id': 'task-1',
    });
    expect(metrics.counters).toEqual([
      {
        name: 'commands.executed',
        value: 1,
        attributes: { commandType: 'task.create' },
      },
    ]);
  });

  it('records span errors and rethrows the original error', async () => {
    const spanExporter = new InMemorySpanExporter();
    const telemetry = createTelemetry({
      serviceName: 'cockpit-test',
      spanExporter,
      metricSink: new InMemoryMetricSink(),
      logLevel: 'silent',
    });

    await expect(
      telemetry.withSpan('command.fail', {}, async () => {
        throw new Error('boom');
      }),
    ).rejects.toThrow('boom');

    await telemetry.shutdown();

    const span = spanExporter.getFinishedSpans()[0];
    expect(span?.name).toBe('command.fail');
    expect(span?.status.code).toBe(2);
    expect(span?.events.some((event) => event.name === 'exception')).toBe(true);
  });

  it('redacts sensitive attributes before logging/exporting', () => {
    expect(
      redactAttributes({
        token: 'secret-token',
        apiKey: 'secret-key',
        password: 'secret-password',
        normal: 'visible',
        nested: { secret: 'hidden', ok: 'visible' },
      }),
    ).toEqual({
      token: '[REDACTED]',
      apiKey: '[REDACTED]',
      password: '[REDACTED]',
      normal: 'visible',
      nested: { secret: '[REDACTED]', ok: 'visible' },
    });
  });

  it('console exporter stores exported spans in memory for dashboard base', () => {
    const exporter = new ConsoleSpanExporter();
    exporter.exportSpan({
      name: 'demo',
      attributes: { visible: 'yes' },
      startedAt: '2026-06-07T10:00:00.000Z',
      endedAt: '2026-06-07T10:00:01.000Z',
      status: { code: 1 },
      events: [],
    });

    expect(exporter.getSpans()).toEqual([
      {
        name: 'demo',
        attributes: { visible: 'yes' },
        startedAt: '2026-06-07T10:00:00.000Z',
        endedAt: '2026-06-07T10:00:01.000Z',
        status: { code: 1 },
        events: [],
      },
    ]);
  });
});
