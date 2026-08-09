import React from 'react';
import { createRoot } from 'react-dom/client';

import './styles.css';

// --- Types matching backend contracts ---

type ConnectionState = 'connecting' | 'connected' | 'disconnected';

interface BackendEvent {
  readonly sequence: number;
  readonly event_type: string;
  readonly aggregate_id: string;
  readonly timestamp: string;
  readonly payload: Record<string, unknown>;
  readonly idempotency_key: string | null;
}

interface QuotaWindow {
  readonly budget: number;
  readonly consumed: number;
  readonly remaining: number;
  readonly window_start: string;
  readonly window_end: string;
}

interface QuotaStatus {
  readonly provider: string;
  readonly frozen: boolean;
  readonly rolling_5h: QuotaWindow;
  readonly weekly: QuotaWindow;
}

interface AgentInfo {
  readonly id: string;
  readonly name: string;
  readonly status: string;
  readonly adapter: string;
}

interface HealthInfo {
  readonly status: string;
  readonly version: string;
}

function ratio(remaining: number, budget: number): number {
  if (budget === 0) return 0;
  return Math.max(0, Math.min(100, Math.round((remaining / budget) * 100)));
}

function providerLabel(provider: string): string {
  const labels: Record<string, string> = {
    zai: 'Z.AI GLM-5.1',
    chatgpt: 'ChatGPT / Codex',
    claude: 'Claude Pro',
  };
  return labels[provider] ?? provider;
}

function barColor(pct: number): string {
  if (pct > 50) return '#47f0b5';
  if (pct > 20) return '#ffd166';
  return '#ff6b6b';
}

function App(): React.ReactElement {
  const [connection, setConnection] = React.useState<ConnectionState>('connecting');
  const [events, setEvents] = React.useState<readonly BackendEvent[]>([]);
  const [quotas, setQuotas] = React.useState<readonly QuotaStatus[]>([]);
  const [agents, setAgents] = React.useState<readonly AgentInfo[]>([]);
  const [health, setHealth] = React.useState<HealthInfo | null>(null);

  // Fetch initial data from REST API
  const fetchAll = React.useCallback(async () => {
    try {
      const [eventsRes, agentsRes, healthRes] = await Promise.all([
        fetch('/api/events'),
        fetch('/api/agents'),
        fetch('/api/health'),
      ]);

      if (eventsRes.ok) {
        const raw: BackendEvent[] = await eventsRes.json();
        setEvents(raw.slice(0, 50));
      }
      if (agentsRes.ok) setAgents(await agentsRes.json());
      if (healthRes.ok) setHealth(await healthRes.json());

      // Fetch quota per provider
      const providers = ['zai', 'chatgpt', 'claude'];
      const quotaResults = await Promise.allSettled(
        providers.map(async (p) => {
          const r = await fetch(`/api/quota/${p}`);
          return r.ok ? ((await r.json()) as QuotaStatus) : null;
        }),
      );
      const validQuotas = quotaResults
        .filter(
          (r): r is PromiseFulfilledResult<QuotaStatus> =>
            r.status === 'fulfilled' && r.value !== null,
        )
        .map((r) => r.value);
      setQuotas(validQuotas);
    } catch {
      // API not available yet — will retry via WS
    }
  }, []);

  // WebSocket for live events
  React.useEffect(() => {
    fetchAll();

    const ws = new WebSocket(
      `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/ws/events`,
    );

    ws.addEventListener('open', () => setConnection('connected'));
    ws.addEventListener('close', () => setConnection('disconnected'));
    ws.addEventListener('error', () => setConnection('disconnected'));
    ws.addEventListener('message', (message) => {
      if (typeof message.data !== 'string') return;
      try {
        const event: BackendEvent = JSON.parse(message.data);
        if (event.event_type && event.aggregate_id) {
          setEvents((current) => [event, ...current].slice(0, 50));
        }
      } catch {
        // ignore malformed messages
      }
    });

    return () => ws.close();
  }, [fetchAll]);

  // Periodic quota refresh every 30s
  React.useEffect(() => {
    const interval = setInterval(fetchAll, 30_000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Paperclip · AgentOS · Hermes · Claude Code · Codex · Obsidian</p>
          <h1>Cockpit Unificado Multi-Agente</h1>
          <p className="subtitle">
            Plano de control event-sourced con Quota Governor visible desde el primer día.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {health && <span className="version-badge">v{health.version}</span>}
          <div className={`status status-${connection}`}>{connection}</div>
        </div>
      </section>

      {/* Agents strip */}
      {agents.length > 0 && (
        <section className="agents-strip">
          {agents.map((agent) => (
            <div className="agent-chip" key={agent.id}>
              <span className="agent-dot" />
              <span>{agent.name}</span>
              <code>{agent.adapter}</code>
            </div>
          ))}
        </section>
      )}

      {/* Quota cards */}
      <section className="grid">
        {quotas.map((quota) => {
          const rolling = ratio(quota.rolling_5h.remaining, quota.rolling_5h.budget);
          const weekly = ratio(quota.weekly.remaining, quota.weekly.budget);
          return (
            <article className="card" key={quota.provider}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <h2>{providerLabel(quota.provider)}</h2>
                {quota.frozen && <span className="frozen-badge">FROZEN</span>}
              </div>
              <div className="metric">
                <span>Ventana 5h</span>
                <strong>
                  {quota.rolling_5h.consumed}/{quota.rolling_5h.budget}
                </strong>
              </div>
              <div className="bar">
                <span
                  style={{
                    width: `${rolling}%`,
                    background: barColor(rolling),
                  }}
                />
              </div>
              <div className="metric">
                <span>Semanal</span>
                <strong>
                  {quota.weekly.consumed}/{quota.weekly.budget}
                </strong>
              </div>
              <div className="bar">
                <span
                  style={{
                    width: `${weekly}%`,
                    background: barColor(weekly),
                  }}
                />
              </div>
            </article>
          );
        })}
      </section>

      {/* Event log */}
      <section className="panel">
        <div className="panel-heading">
          <h2>Event Log vivo</h2>
          <span>{events.length} eventos</span>
        </div>
        <div className="timeline">
          {events.map((event, idx) => (
            <article className="event" key={`${event.sequence}-${idx}`}>
              <time>{new Date(event.timestamp).toLocaleTimeString()}</time>
              <div>
                <strong>
                  #{event.sequence} · {event.event_type}
                </strong>
                <p>
                  {event.payload && Object.keys(event.payload).length > 0
                    ? JSON.stringify(event.payload)
                    : '—'}
                </p>
                <code>{event.aggregate_id}</code>
              </div>
            </article>
          ))}
          {events.length === 0 && (
            <p style={{ color: '#6b7a94', padding: '18px' }}>
              Sin eventos aún. Lanza una tarea desde la API para ver actividad aquí.
            </p>
          )}
        </div>
      </section>
    </main>
  );
}

const root = document.getElementById('root');
if (root === null) {
  throw new Error('root element not found');
}

createRoot(root).render(<App />);
