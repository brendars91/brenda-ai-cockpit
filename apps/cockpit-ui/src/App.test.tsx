import { describe, it, expect } from 'vitest';
import { renderToString } from 'react-dom/server';
import { App } from './App';
import { summary, costBreakdown, toolStats, memoryFacts } from '@cockpit/telemetry-reader';

describe('cockpit-web real data render', () => {
  it('renders the cockpit shell with real telemetry numbers', () => {
    const html = renderToString(<App />);
    expect(html).toContain('Brenda AI Cockpit');
    expect(html).toContain('Hermes Real Telemetry Observatory');
    expect(html).toContain(String(summary.total_sessions));
    expect(html).toContain(String(memoryFacts.length));
  });

  it('renders all six dashboard tabs', () => {
    const html = renderToString(<App />);
    for (const label of ['Cost Intelligence', 'Evidence Ledger', 'Session Forensics', 'Cron Health', 'Tool Analytics', 'Memory Observatory']) {
      expect(html).toContain(label);
    }
  });

  it('renders real model and tool data from snapshots', () => {
    const html = renderToString(<App />);
    expect(html).toContain(costBreakdown[0].model);
    expect(html).toContain(toolStats[0].tool_name);
  });
});
