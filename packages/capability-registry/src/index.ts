export interface CapabilityRecord { readonly id: string; readonly adapterId: string; readonly capability: string; readonly risk: 'R0' | 'R1' | 'R2' | 'R3' | 'R4'; readonly evidenceRequired: boolean; }
export class CapabilityRegistry {
  private readonly records = new Map<string, CapabilityRecord>();
  public register(record: CapabilityRecord): void { if (!record.id.trim()) throw new Error('capability id is required'); if (!record.capability.trim()) throw new Error('capability name is required'); this.records.set(record.id, record); }
  public get(id: string): CapabilityRecord | undefined { return this.records.get(id); }
  public match(capability: string): readonly CapabilityRecord[] { const normalized = capability.trim().toLowerCase(); return [...this.records.values()].filter((record) => record.capability.toLowerCase() === normalized); }
  public list(): readonly CapabilityRecord[] { return [...this.records.values()].sort((a, b) => a.id.localeCompare(b.id)); }
}
