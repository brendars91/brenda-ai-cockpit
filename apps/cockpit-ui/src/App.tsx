import { useEffect, useMemo, useState } from 'react';
import {
  summary,
  costBreakdown,
  toolStats,
  cronHealth,
  evidenceLedger,
  memoryFacts,
  sessions,
  getTotalTokens,
  getConcentrationRisk,
  getCronSuccessRate,
  getCostAnomalies,
  getAverageTrustScore,
  getToolCategories,
  getModelComparison,
} from '@cockpit/telemetry-reader';
import { getExecutiveBrief, getTopRecommendations } from '@cockpit/intelligence';
import './styles.css';

type Dashboard = 'operations' | 'cost' | 'evidence' | 'sessions' | 'cron' | 'tools' | 'memory';
type CommandStatus = 'queued' | 'pending_approval' | 'denied' | 'running' | 'succeeded' | 'failed' | 'cancelled';

interface CommandRecord {
  readonly id: string;
  readonly requestedBy: string;
  readonly action: string;
  readonly target: string;
  readonly risk: string;
  readonly status: CommandStatus;
  readonly policyDecision: string;
  readonly policyReason: string;
  readonly createdAt: string;
  readonly updatedAt: string;
}

interface AuditEvent {
  readonly id: number;
  readonly createdAt: string;
  readonly kind: string;
  readonly actor: string;
  readonly subject: string;
  readonly eventHash: string;
}

interface ApiState {
  readonly loading: boolean;
  readonly error: string | null;
  readonly commands: readonly CommandRecord[];
  readonly audit: readonly AuditEvent[];
  readonly chainOk: boolean | null;
}

const dashboards: { id: Dashboard; label: string; subtitle: string }[] = [
  { id: 'operations', label: 'Operator Console', subtitle: 'Auth, commands, approvals y audit chain' },
  { id: 'cost', label: 'Cost Intelligence', subtitle: 'Modelos, tokens, coste y concentración' },
  { id: 'evidence', label: 'Evidence Ledger', subtitle: 'Verificaciones reales y comandos canónicos' },
  { id: 'sessions', label: 'Session Forensics', subtitle: 'Sesiones, intensidad y anomalías' },
  { id: 'cron', label: 'Cron Health', subtitle: 'Ejecuciones, fallo y salud operacional' },
  { id: 'tools', label: 'Tool Analytics', subtitle: 'Mapa de uso de herramientas' },
  { id: 'memory', label: 'Memory Observatory', subtitle: 'Facts, confianza y memoria operacional' },
];

const allowedActions = [
  { id: 'run_secret_scan', label: 'Secret scan', risk: 'R2' },
  { id: 'run_validate_repo', label: 'Validate repo', risk: 'R2' },
  { id: 'run_typecheck', label: 'Typecheck', risk: 'R2' },
  { id: 'run_tests', label: 'Tests', risk: 'R2' },
  { id: 'run_build', label: 'Build', risk: 'R2' },
  { id: 'run_verify', label: 'Full verify', risk: 'R2' },
] as const;

function formatNumber(n: number): string {
  return new Intl.NumberFormat('en-US').format(Math.round(n));
}

function formatMoney(n: number): string {
  return `$${n.toFixed(2)}`;
}

function pct(value: number, total: number): number {
  return total <= 0 ? 0 : Math.round((value / total) * 100);
}

async function apiFetch<T>(apiBase: string, token: string, path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Authorization', `Bearer ${token}`);
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  const response = await fetch(`${apiBase.replace(/\/$/, '')}${path}`, { ...init, headers });
  const json = await response.json() as T & { error?: string; message?: string };
  if (!response.ok) throw new Error(json.message ?? json.error ?? `HTTP ${response.status}`);
  return json;
}

function Bar({ value, max, tone = 'teal' }: { value: number; max: number; tone?: 'teal' | 'amber' | 'red' | 'blue' }) {
  const width = Math.max(3, Math.min(100, pct(value, max)));
  return <div className="bar"><span className={`fill ${tone}`} style={{ width: `${width}%` }} /></div>;
}

function StatCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <article className="stat-card"><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}

function StatusPill({ status }: { status: CommandStatus | 'ok' | 'bad' | 'idle' }) {
  return <span className={`status-pill ${status}`}>{status}</span>;
}

function getDefaultApiBase(): string {
  if (typeof window === 'undefined') return 'http://127.0.0.1:8787';
  const { protocol, hostname } = window.location;
  if (hostname.endsWith('.ts.net')) return `${protocol}//${hostname}:8787`;
  return 'http://127.0.0.1:8787';
}

function OperationsDashboard() {
  const [apiBase, setApiBase] = useState(() => getDefaultApiBase());
  const [token, setToken] = useState('');
  const [selectedAction, setSelectedAction] = useState<(typeof allowedActions)[number]['id']>('run_verify');
  const [state, setState] = useState<ApiState>({ loading: false, error: null, commands: [], audit: [], chainOk: null });

  const tokenReady = token.trim().length > 0;
  const selectedMeta = allowedActions.find((action) => action.id === selectedAction)!;

  async function refresh(): Promise<void> {
    if (!tokenReady) {
      setState((prev) => ({ ...prev, error: 'Introduce un bearer token para consultar endpoints protegidos.' }));
      return;
    }
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [commands, audit] = await Promise.all([
        apiFetch<{ commands: CommandRecord[] }>(apiBase, token, '/api/v1/commands'),
        apiFetch<{ audit: AuditEvent[]; chain_ok: boolean }>(apiBase, token, '/api/v1/audit'),
      ]);
      setState({ loading: false, error: null, commands: commands.commands, audit: audit.audit, chainOk: audit.chain_ok });
    } catch (error) {
      setState((prev) => ({ ...prev, loading: false, error: error instanceof Error ? error.message : String(error) }));
    }
  }

  async function submitCommand(): Promise<void> {
    if (!tokenReady) return;
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      await apiFetch(apiBase, token, '/api/v1/commands', {
        method: 'POST',
        body: JSON.stringify({ action: 'execute', target: selectedMeta.id, risk: selectedMeta.risk, payload: { requested_from: 'cockpit-ui' } }),
      });
      await refresh();
    } catch (error) {
      setState((prev) => ({ ...prev, loading: false, error: error instanceof Error ? error.message : String(error) }));
    }
  }

  async function approve(commandId: string): Promise<void> {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      await apiFetch(apiBase, token, `/api/v1/commands/${commandId}/approve`, { method: 'POST', body: JSON.stringify({ reason: 'approved from operator console' }) });
      await refresh();
    } catch (error) {
      setState((prev) => ({ ...prev, loading: false, error: error instanceof Error ? error.message : String(error) }));
    }
  }

  async function execute(commandId: string): Promise<void> {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      await apiFetch(apiBase, token, `/api/v1/commands/${commandId}/execute`, { method: 'POST', body: JSON.stringify({}) });
      await refresh();
    } catch (error) {
      setState((prev) => ({ ...prev, loading: false, error: error instanceof Error ? error.message : String(error) }));
    }
  }

  useEffect(() => { void refresh(); }, []);

  return <section className="dashboard-panel operations-panel">
    <div className="stats-grid"><StatCard label="API auth" value={tokenReady ? 'configured' : 'missing'} detail="token solo en memoria del navegador" /><StatCard label="Audit chain" value={state.chainOk === null ? 'unknown' : state.chainOk ? 'OK' : 'BROKEN'} detail="hash-chain append-only" /><StatCard label="Commands" value={String(state.commands.length)} detail="cockpit.db queue" /><StatCard label="Allowed actions" value={String(allowedActions.length)} detail="catálogo cerrado, sin shell libre" /></div>
    <div className="panel-grid two">
      <article className="card control-card"><h3>Control privado</h3><label>API base<input value={apiBase} onChange={(event) => setApiBase(event.target.value)} aria-label="API base" /></label><label>Bearer token<input type="password" value={token} onChange={(event) => setToken(event.target.value)} aria-label="Bearer token" autoComplete="off" /></label><label>Acción permitida<select value={selectedAction} onChange={(event) => setSelectedAction(event.target.value as typeof selectedAction)} aria-label="Allowed action">{allowedActions.map((action) => <option value={action.id} key={action.id}>{action.label} · {action.risk}</option>)}</select></label><div className="button-row"><button disabled={!tokenReady || state.loading} onClick={submitCommand}>Queue command</button><button disabled={!tokenReady || state.loading} onClick={refresh}>Refresh</button></div>{state.error ? <p className="error-box">{state.error}</p> : null}</article>
      <article className="card"><h3>Audit ledger</h3><p className="chain-state">Chain: {state.chainOk === null ? <StatusPill status="idle" /> : state.chainOk ? <StatusPill status="ok" /> : <StatusPill status="bad" />}</p>{state.audit.slice(0, 8).map((event) => <div className="compact-row" key={event.id}><span>{event.kind}</span><strong>#{event.id}</strong><small>{event.createdAt} · {event.subject} · {event.eventHash.slice(0, 12)}</small></div>)}</article>
    </div>
    <article className="card command-table"><h3>Command queue</h3>{state.commands.length === 0 ? <p className="muted">Sin comandos en cockpit.db todavía.</p> : state.commands.slice(0, 12).map((command) => <div className="command-row" key={command.id}><div><strong>{command.target}</strong><small>{command.id} · {command.action} · {command.risk} · {command.policyReason}</small></div><StatusPill status={command.status} /><div className="button-row compact"><button disabled={command.status !== 'pending_approval' || state.loading} onClick={() => approve(command.id)}>Approve</button><button disabled={command.status !== 'queued' || state.loading} onClick={() => execute(command.id)}>Execute</button></div></div>)}</article>
  </section>;
}

function CostDashboard() {
  const totals = getTotalTokens();
  const risk = getConcentrationRisk();
  const comparison = getModelComparison();
  const maxTokens = Math.max(...costBreakdown.map((m) => m.total_input_tokens));
  return <section className="dashboard-panel"><div className="stats-grid"><StatCard label="Input tokens" value={formatNumber(totals.input)} detail="acumulado por modelo" /><StatCard label="Output tokens" value={formatNumber(totals.output)} detail="salida total registrada" /><StatCard label="Coste trackeado" value={formatMoney(summary.total_cost_tracked)} detail="cost_status estimado" /><StatCard label="Riesgo concentración" value={`${risk?.percentage ?? 0}%`} detail={risk?.model ?? 'sin dato'} /></div><div className="panel-grid two"><article className="card"><h3>Consumo por modelo</h3>{costBreakdown.slice(0, 8).map((m) => <div className="metric-row" key={m.model}><div><strong>{m.model}</strong><span>{m.session_count} sesiones · {formatMoney(m.total_cost)}</span></div><Bar value={m.total_input_tokens} max={maxTokens} tone={m.total_cost > 0 ? 'amber' : 'teal'} /></div>)}</article><article className="card"><h3>Eficiencia comparativa</h3>{comparison.slice(0, 8).map((m) => <div className="compact-row" key={m.model}><span>{m.model}</span><strong>{formatNumber(m.tokensPerSession)} tok/sesión</strong><small>{formatMoney(m.costPerSession)}/sesión · eff {m.efficiencyScore}</small></div>)}</article></div></section>;
}

function EvidenceDashboard() {
  return <section className="dashboard-panel"><div className="stats-grid"><StatCard label="Eventos verificados" value={String(evidenceLedger.length)} detail="verification_evidence.db" /><StatCard label="Tipos de gate" value={String(new Set(evidenceLedger.map((e) => e.kind)).size)} detail="kind únicos" /><StatCard label="Último comando" value={evidenceLedger[0]?.kind ?? 'n/a'} detail="canon registrado" /></div><article className="card"><h3>Timeline de evidencia</h3>{evidenceLedger.slice(0, 12).map((e) => <div className="timeline-item" key={e.id}><span className="dot" /><div><strong>{e.kind}</strong><p>{e.canonical_command || e.command}</p><small>{e.created_at} · {e.session_id}</small></div></div>)}</article></section>;
}

function SessionsDashboard() {
  const topCost = sessions.slice(0, 5);
  const active = sessions.slice(0, 5);
  const anomalies = getCostAnomalies();
  return <section className="dashboard-panel"><div className="stats-grid"><StatCard label="Sesiones snapshot" value={String(summary.total_sessions)} detail="últimas 200 sanitizadas" /><StatCard label="Anomalías coste" value={String(anomalies.length)} detail=">2x media coste" /><StatCard label="Top tools en sesión" value={String(active[0]?.tool_call_count ?? 0)} detail={active[0]?.model ?? 'n/a'} /></div><div className="panel-grid two"><article className="card"><h3>Sesiones más caras</h3>{topCost.map((s) => <div className="compact-row" key={s.id}><span>{s.title || s.id}</span><strong>{formatMoney(s.estimated_cost_usd ?? 0)}</strong><small>{s.model} · {formatNumber(s.input_tokens + s.output_tokens)} tokens</small></div>)}</article><article className="card"><h3>Sesiones más activas</h3>{active.map((s) => <div className="compact-row" key={s.id}><span>{s.title || s.id}</span><strong>{s.tool_call_count} tool calls</strong><small>{s.model} · {s.message_count} mensajes</small></div>)}</article></div></section>;
}

function CronDashboard() {
  const rate = getCronSuccessRate();
  const total = cronHealth.reduce((sum, c) => sum + c.count, 0);
  const max = Math.max(...cronHealth.map((c) => c.count));
  return <section className="dashboard-panel"><div className="stats-grid"><StatCard label="Success rate" value={`${rate}%`} detail="cron executions" /><StatCard label="Ejecuciones" value={String(total)} detail="cron/executions.db" /><StatCard label="Failures" value={String(cronHealth.find((c) => c.status === 'failed')?.count ?? 0)} detail="requiere clustering fase 4" /></div><article className="card"><h3>Estados de ejecución</h3>{cronHealth.map((c) => <div className="metric-row" key={c.status}><div><strong>{c.status}</strong><span>{c.count} ejecuciones · {pct(c.count, total)}%</span></div><Bar value={c.count} max={max} tone={c.status === 'failed' ? 'red' : 'teal'} /></div>)}</article></section>;
}

function ToolsDashboard() {
  const cats = getToolCategories();
  const max = Math.max(...toolStats.map((t) => t.call_count));
  return <section className="dashboard-panel"><div className="stats-grid"><StatCard label="Tool calls" value={formatNumber(summary.total_tool_calls)} detail="messages.tool_name" /><StatCard label="Herramientas únicas" value={String(toolStats.length)} detail="catalog uso real" /><StatCard label="Categorías" value={String(Object.keys(cats).length)} detail="execution/reading/writing/meta" /></div><div className="panel-grid two"><article className="card"><h3>Top tools</h3>{toolStats.slice(0, 10).map((t) => <div className="metric-row" key={t.tool_name}><div><strong>{t.tool_name}</strong><span>{t.call_count} calls · {t.sessions_used_in} sesiones</span></div><Bar value={t.call_count} max={max} tone="blue" /></div>)}</article><article className="card"><h3>Categorías funcionales</h3>{Object.entries(cats).map(([cat, count]) => <div className="compact-row" key={cat}><span>{cat}</span><strong>{formatNumber(count)}</strong><small>{pct(count, summary.total_tool_calls)}% del total</small></div>)}</article></div></section>;
}

function MemoryDashboard() {
  const avg = getAverageTrustScore();
  const categories = memoryFacts.reduce<Record<string, number>>((acc, f) => { acc[f.category] = (acc[f.category] ?? 0) + 1; return acc; }, {});
  const lowTrust = memoryFacts.filter((f) => f.trust_score < 0.5);
  return <section className="dashboard-panel"><div className="stats-grid"><StatCard label="Facts" value={String(memoryFacts.length)} detail="memory_store.db" /><StatCard label="Trust medio" value={String(avg)} detail="0-1 score" /><StatCard label="Low trust" value={String(lowTrust.length)} detail="<0.5" /></div><div className="panel-grid two"><article className="card"><h3>Categorías de memoria</h3>{Object.entries(categories).map(([cat, count]) => <div className="compact-row" key={cat}><span>{cat}</span><strong>{count}</strong><small>{pct(count, memoryFacts.length)}% facts</small></div>)}</article><article className="card"><h3>Facts críticos recientes</h3>{memoryFacts.slice(0, 6).map((f) => <div className="fact" key={f.fact_id}><strong>#{f.fact_id} · trust {f.trust_score}</strong><p>{f.content.slice(0, 180)}{f.content.length > 180 ? '…' : ''}</p></div>)}</article></div></section>;
}

function DashboardBody({ active }: { active: Dashboard }) {
  if (active === 'operations') return <OperationsDashboard />;
  if (active === 'cost') return <CostDashboard />;
  if (active === 'evidence') return <EvidenceDashboard />;
  if (active === 'sessions') return <SessionsDashboard />;
  if (active === 'cron') return <CronDashboard />;
  if (active === 'tools') return <ToolsDashboard />;
  return <MemoryDashboard />;
}

function IntelligenceStrip() {
  const brief = getExecutiveBrief();
  const top = getTopRecommendations();
  return <section className="intelligence-strip" aria-label="Operational intelligence"><article className="score-card"><span>Operational score</span><strong>{brief.score.score}/100 · {brief.score.grade}</strong><small>cron {brief.score.components.cron}% · cost {brief.score.components.cost}% · memory {brief.score.components.memory}%</small></article><article className="card recommendations"><h3>Top recommendations</h3>{top.slice(0, 3).map((f) => <div className={`finding ${f.severity}`} key={f.id}><strong>{f.title}</strong><p>{f.evidence}</p><small>{f.recommendation}</small></div>)}</article></section>;
}

export function App() {
  const [active, setActive] = useState<Dashboard>('operations');
  const activeMeta = dashboards.find((d) => d.id === active)!;
  const generated = useMemo(() => new Date(summary.generated_at).toLocaleString('es-ES'), []);
  return <main className="cockpit-shell"><section className="hero"><div><p className="eyebrow">Hermes Private Operator Control Plane</p><h1>Brenda AI Cockpit</h1><p>Observability y operación privada sobre {summary.total_sessions} sesiones, {formatNumber(summary.total_tool_calls)} tool calls, {summary.total_cron_executions} crons y {memoryFacts.length} facts. Auth bearer, queue auditada y acciones cerradas.</p></div><div className="hero-card"><span>snapshot</span><strong>{generated}</strong><small>top tool: {toolStats[0]?.tool_name ?? 'n/a'} · datos sanitizados</small></div></section><IntelligenceStrip /><nav className="dashboard-tabs" aria-label="Dashboards">{dashboards.map((d) => <button key={d.id} className={d.id === active ? 'active' : ''} onClick={() => setActive(d.id)}><strong>{d.label}</strong><span>{d.subtitle}</span></button>)}</nav><section className="section-title"><p className="eyebrow">{activeMeta.label}</p><h2>{activeMeta.subtitle}</h2></section><DashboardBody active={active} /></main>;
}
