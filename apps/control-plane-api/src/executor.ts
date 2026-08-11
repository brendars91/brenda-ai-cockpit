import { spawn } from 'node:child_process';
import type { CockpitStore, CommandRecord } from './storage.js';

export interface AllowedAction {
  readonly id: string;
  readonly command: string;
  readonly args: readonly string[];
  readonly timeoutMs: number;
  readonly outputLimit: number;
  readonly cwd?: string;
}

export interface ExecutionResult {
  readonly actionId: string;
  readonly exitCode: number | null;
  readonly timedOut: boolean;
  readonly stdout: string;
  readonly stderr: string;
}

export const defaultActionCatalog: readonly AllowedAction[] = [
  { id: 'run_secret_scan', command: 'python3', args: ['tools/secret_scan.py', '.'], timeoutMs: 120_000, outputLimit: 20_000 },
  { id: 'run_validate_repo', command: 'python3', args: ['tools/validate_repo.py'], timeoutMs: 120_000, outputLimit: 20_000 },
  { id: 'run_typecheck', command: 'npm', args: ['run', 'typecheck'], timeoutMs: 300_000, outputLimit: 40_000 },
  { id: 'run_tests', command: 'npm', args: ['run', 'test'], timeoutMs: 300_000, outputLimit: 40_000 },
  { id: 'run_build', command: 'npm', args: ['run', 'build'], timeoutMs: 300_000, outputLimit: 40_000 },
  { id: 'run_verify', command: 'npm', args: ['run', 'verify'], timeoutMs: 600_000, outputLimit: 60_000 },
];

function truncate(value: string, limit: number): string {
  if (value.length <= limit) return value;
  return `${value.slice(0, limit)}\n[truncated ${value.length - limit} chars]`;
}

export function findAllowedAction(actionId: string, catalog: readonly AllowedAction[] = defaultActionCatalog): AllowedAction | undefined {
  return catalog.find((action) => action.id === actionId);
}

export function runAllowedAction(action: AllowedAction, defaultCwd: string): Promise<ExecutionResult> {
  return new Promise((resolve) => {
    let stdout = '';
    let stderr = '';
    let timedOut = false;
    const child = spawn(action.command, [...action.args], { cwd: action.cwd ?? defaultCwd, shell: false, stdio: ['ignore', 'pipe', 'pipe'] });
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill('SIGTERM');
    }, action.timeoutMs);

    child.stdout.on('data', (chunk) => { stdout = truncate(stdout + chunk.toString(), action.outputLimit); });
    child.stderr.on('data', (chunk) => { stderr = truncate(stderr + chunk.toString(), action.outputLimit); });
    child.on('close', (exitCode) => {
      clearTimeout(timer);
      resolve({ actionId: action.id, exitCode, timedOut, stdout, stderr });
    });
    child.on('error', (error) => {
      clearTimeout(timer);
      resolve({ actionId: action.id, exitCode: 127, timedOut, stdout, stderr: truncate(`${stderr}\n${error.message}`, action.outputLimit) });
    });
  });
}

export async function executeQueuedCommand(store: CockpitStore, commandId: string, defaultCwd: string, catalog: readonly AllowedAction[] = defaultActionCatalog): Promise<CommandRecord> {
  const command = store.listCommands(500).find((item) => item.id === commandId);
  if (!command) throw new Error(`command ${commandId} not found`);
  const action = findAllowedAction(command.target, catalog);
  if (!action) {
    store.markCommandRunning(commandId);
    return store.completeCommand(commandId, 'failed', { error: 'action_not_allowed', target: command.target });
  }
  store.markCommandRunning(commandId);
  const result = await runAllowedAction(action, defaultCwd);
  return store.completeCommand(commandId, result.exitCode === 0 && !result.timedOut ? 'succeeded' : 'failed', result);
}
