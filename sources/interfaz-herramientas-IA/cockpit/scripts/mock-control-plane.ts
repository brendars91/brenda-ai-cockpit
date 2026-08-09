import { WebSocketServer } from 'ws';

interface MockEvent {
  readonly sequence: number;
  readonly eventType: string;
  readonly aggregateId: string;
  readonly timestamp: string;
  readonly summary: string;
}

interface MockQuota {
  readonly provider: 'zai' | 'chatgpt' | 'claude';
  readonly rollingRemaining: number;
  readonly rollingBudget: number;
  readonly weeklyRemaining: number;
  readonly weeklyBudget: number;
}

const quotas: readonly MockQuota[] = [
  {
    provider: 'zai',
    rollingRemaining: 820,
    rollingBudget: 1_000,
    weeklyRemaining: 8_700,
    weeklyBudget: 10_000,
  },
  {
    provider: 'chatgpt',
    rollingRemaining: 1_650,
    rollingBudget: 2_000,
    weeklyRemaining: 18_200,
    weeklyBudget: 20_000,
  },
  {
    provider: 'claude',
    rollingRemaining: 1_220,
    rollingBudget: 1_500,
    weeklyRemaining: 13_400,
    weeklyBudget: 15_000,
  },
];

function makeEvent(sequence: number, eventType: string, summary: string): MockEvent {
  return {
    sequence,
    eventType,
    aggregateId: `mock-${sequence}`,
    timestamp: new Date(Date.now() + sequence * 1000).toISOString(),
    summary,
  };
}

const initialEvents: readonly MockEvent[] = [
  makeEvent(1, 'system.freeze_deactivated', 'Control plane ready; global freeze is off.'),
  makeEvent(2, 'system.quota_warning', 'Quota Governor dashboard stream initialized.'),
  makeEvent(3, 'task.created', 'Phase 0 cockpit smoke task created from mock control plane.'),
];

const server = new WebSocketServer({ host: '127.0.0.1', port: 4747, path: '/ws' });
let sequence = initialEvents.length;

server.on('connection', (socket) => {
  socket.send(JSON.stringify({ type: 'snapshot', events: initialEvents, quotas }));

  const timer = setInterval(() => {
    sequence += 1;
    socket.send(
      JSON.stringify({
        type: 'event',
        event: makeEvent(sequence, 'run.progress', `Mock control-plane heartbeat ${sequence}.`),
      }),
    );
  }, 2_000);

  socket.on('close', () => clearInterval(timer));
});

console.log('mock-control-plane listening on ws://127.0.0.1:4747/ws');
