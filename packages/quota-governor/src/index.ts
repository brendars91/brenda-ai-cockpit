export type QuotaProviderName = 'zai' | 'chatgpt' | 'claude';
export type QuotaWindowType = 'rolling_5h' | 'weekly';
export type QuotaDecisionKind = 'allow' | 'defer' | 'deny' | 'degrade';
export type TaskValue = 'low' | 'normal' | 'critical';

export interface ProviderQuotaPolicy {
  readonly rolling5hBudget: number;
  readonly weeklyBudget: number;
  readonly warningThreshold: number;
}

export type QuotaPolicy = Readonly<Record<QuotaProviderName, ProviderQuotaPolicy>>;

export interface CreateQuotaPolicyInput {
  readonly zai: ProviderQuotaPolicy;
  readonly chatgpt: ProviderQuotaPolicy;
  readonly claude: ProviderQuotaPolicy;
}

export interface QuotaGovernorOptions {
  readonly policy: QuotaPolicy;
  readonly now?: () => Date;
}

export interface QuotaCheckRequest {
  readonly provider: QuotaProviderName;
  readonly estimatedTokens: number;
  readonly taskValue: TaskValue;
  readonly alternativeProviders?: readonly QuotaProviderName[];
}

export interface QuotaDecision {
  readonly provider: QuotaProviderName;
  readonly decision: QuotaDecisionKind;
  readonly reason: string;
  readonly retryAfter?: string;
  readonly alternativeProvider?: QuotaProviderName;
}

export interface ConsumptionRecord {
  readonly provider: QuotaProviderName;
  readonly tokensUsed: number;
  readonly source: string;
}

export interface UsageEvent extends ConsumptionRecord {
  readonly recordedAt: string;
}

export interface QuotaWindowSnapshot {
  readonly provider: QuotaProviderName;
  readonly windowType: QuotaWindowType;
  readonly budget: number;
  readonly consumed: number;
  readonly remaining: number;
  readonly windowStart: string;
  readonly windowEnd: string;
  readonly projectedExhaustion?: string;
}

export interface FreezeState {
  readonly frozen: boolean;
  readonly reason?: string;
  readonly by?: string;
  readonly provider?: QuotaProviderName;
  readonly frozenAt?: string;
}

interface MutableWindowState {
  budget: number;
  consumed: number;
  windowStart: Date;
  windowEnd: Date;
}

type WindowStateByType = Record<QuotaWindowType, MutableWindowState>;
type WindowState = Record<QuotaProviderName, WindowStateByType>;

const FIVE_HOURS_MS = 5 * 60 * 60 * 1000;
const WEEK_MS = 7 * 24 * 60 * 60 * 1000;

export function createDefaultQuotaPolicy(input: CreateQuotaPolicyInput): QuotaPolicy {
  return {
    zai: input.zai,
    chatgpt: input.chatgpt,
    claude: input.claude,
  };
}

function iso(date: Date): string {
  return date.toISOString();
}

function addMs(date: Date, ms: number): Date {
  return new Date(date.getTime() + ms);
}

function cloneDate(date: Date): Date {
  return new Date(date.getTime());
}

export class QuotaGovernor {
  private readonly policy: QuotaPolicy;
  private readonly now: () => Date;
  private readonly windows: WindowState;
  private readonly usageEvents: UsageEvent[];
  private freezeState: FreezeState;

  public constructor(options: QuotaGovernorOptions) {
    this.policy = options.policy;
    this.now = options.now ?? (() => new Date());
    this.windows = this.createInitialWindows();
    this.usageEvents = [];
    this.freezeState = { frozen: false };
  }

  public check(request: QuotaCheckRequest): QuotaDecision {
    this.refreshWindows();

    if (this.freezeState.frozen) {
      return {
        provider: request.provider,
        decision: 'deny',
        reason: `global freeze active: ${this.freezeState.reason ?? 'unspecified'}`,
      };
    }

    const limitingWindow = this.getMostConstrainedWindow(request.provider);

    if (request.estimatedTokens > limitingWindow.remaining) {
      return {
        provider: request.provider,
        decision: 'deny',
        reason: `insufficient quota for ${request.provider}: needs ${request.estimatedTokens}, remaining ${limitingWindow.remaining}`,
      };
    }

    if (this.isNearWarningThreshold(request.provider)) {
      if (request.taskValue === 'low') {
        return {
          provider: request.provider,
          decision: 'defer',
          reason: `${request.provider} near warning threshold`,
          retryAfter: limitingWindow.windowEnd,
        };
      }

      const alternativeProvider = this.findAlternativeProvider(request);
      if (alternativeProvider !== undefined && request.taskValue === 'normal') {
        return {
          provider: request.provider,
          decision: 'degrade',
          reason: `${request.provider} near warning threshold; route to ${alternativeProvider}`,
          alternativeProvider,
        };
      }
    }

    return { provider: request.provider, decision: 'allow', reason: 'quota available' };
  }

  public recordConsumption(record: ConsumptionRecord): void {
    this.refreshWindows();
    const recordedAt = iso(this.now());
    this.usageEvents.push({ ...record, recordedAt });

    const providerWindows = this.windows[record.provider];
    providerWindows.rolling_5h.consumed += record.tokensUsed;
    providerWindows.weekly.consumed += record.tokensUsed;

    if (providerWindows.rolling_5h.consumed > providerWindows.rolling_5h.budget) {
      this.activateProviderFreeze(record.provider, 'rolling_5h quota exhausted');
    }

    if (providerWindows.weekly.consumed > providerWindows.weekly.budget) {
      this.activateProviderFreeze(record.provider, 'weekly quota exhausted');
    }
  }

  public getWindow(provider: QuotaProviderName, windowType: QuotaWindowType): QuotaWindowSnapshot {
    this.refreshWindows();
    return this.snapshotWindow(provider, windowType, this.windows[provider][windowType]);
  }

  public getAllWindows(): readonly QuotaWindowSnapshot[] {
    this.refreshWindows();
    return (['zai', 'chatgpt', 'claude'] as const).flatMap((provider) => [
      this.getWindow(provider, 'rolling_5h'),
      this.getWindow(provider, 'weekly'),
    ]);
  }

  public getUsageEvents(): readonly UsageEvent[] {
    return [...this.usageEvents];
  }

  public freeze(reason: string, by: string): void {
    this.freezeState = { frozen: true, reason, by, frozenAt: iso(this.now()) };
  }

  public unfreeze(by: string): void {
    this.freezeState = { frozen: false, by };
  }

  public isFrozen(): boolean {
    return this.freezeState.frozen;
  }

  public getFreezeState(): FreezeState {
    return { ...this.freezeState };
  }

  private createInitialWindows(): WindowState {
    const current = this.now();
    const makeProvider = (provider: QuotaProviderName): WindowStateByType => ({
      rolling_5h: {
        budget: this.policy[provider].rolling5hBudget,
        consumed: 0,
        windowStart: cloneDate(current),
        windowEnd: addMs(current, FIVE_HOURS_MS),
      },
      weekly: {
        budget: this.policy[provider].weeklyBudget,
        consumed: 0,
        windowStart: cloneDate(current),
        windowEnd: addMs(current, WEEK_MS),
      },
    });

    return {
      zai: makeProvider('zai'),
      chatgpt: makeProvider('chatgpt'),
      claude: makeProvider('claude'),
    };
  }

  private refreshWindows(): void {
    const current = this.now();
    for (const provider of ['zai', 'chatgpt', 'claude'] as const) {
      for (const windowType of ['rolling_5h', 'weekly'] as const) {
        const window = this.windows[provider][windowType];
        if (current >= window.windowEnd) {
          window.consumed = 0;
          window.windowStart = cloneDate(current);
          window.windowEnd = addMs(current, windowType === 'rolling_5h' ? FIVE_HOURS_MS : WEEK_MS);
        }
      }
    }
  }

  private getMostConstrainedWindow(provider: QuotaProviderName): QuotaWindowSnapshot {
    const rolling = this.getWindow(provider, 'rolling_5h');
    const weekly = this.getWindow(provider, 'weekly');
    return rolling.remaining <= weekly.remaining ? rolling : weekly;
  }

  private isNearWarningThreshold(provider: QuotaProviderName): boolean {
    const threshold = this.policy[provider].warningThreshold;
    return ['rolling_5h', 'weekly'].some((windowType) => {
      const window = this.windows[provider][windowType as QuotaWindowType];
      const remainingRatio = (window.budget - window.consumed) / window.budget;
      return remainingRatio <= threshold;
    });
  }

  private findAlternativeProvider(request: QuotaCheckRequest): QuotaProviderName | undefined {
    return request.alternativeProviders?.find((provider) => {
      const decision = this.check({
        provider,
        estimatedTokens: request.estimatedTokens,
        taskValue: 'critical',
      });
      return decision.decision === 'allow';
    });
  }

  private activateProviderFreeze(provider: QuotaProviderName, reason: string): void {
    this.freezeState = {
      frozen: true,
      provider,
      reason,
      by: 'quota-governor',
      frozenAt: iso(this.now()),
    };
  }

  private snapshotWindow(
    provider: QuotaProviderName,
    windowType: QuotaWindowType,
    window: MutableWindowState,
  ): QuotaWindowSnapshot {
    const remaining = window.budget - window.consumed;
    const base = {
      provider,
      windowType,
      budget: window.budget,
      consumed: window.consumed,
      remaining,
      windowStart: iso(window.windowStart),
      windowEnd: iso(window.windowEnd),
    };

    if (window.consumed <= 0) {
      return base;
    }

    const elapsedMs = Math.max(1, this.now().getTime() - window.windowStart.getTime());
    const tokensPerMs = window.consumed / elapsedMs;
    const projectedExhaustion = iso(addMs(this.now(), Math.max(0, remaining / tokensPerMs)));
    return { ...base, projectedExhaustion };
  }
}
