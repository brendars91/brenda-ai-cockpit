import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { listSkills, getSkillsHandler } from './skillMarketplace';
import { existsSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const TEST_SKILLS_DIR = join(tmpdir(), 'cockpit-skills-test');

function setupTestSkill(name: string, metadata: Record<string, string>, body = '') {
  const dir = join(TEST_SKILLS_DIR, name);
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  const content = `---\n${Object.entries(metadata)
    .map(([k, v]) => `${k}: ${v}`)
    .join('\n')}\n---\n${body}`;
  writeFileSync(join(dir, 'SKILL.md'), content);
}

describe('Skill Marketplace (real filesystem)', () => {
  beforeAll(() => {
    if (existsSync(TEST_SKILLS_DIR)) rmSync(TEST_SKILLS_DIR, { recursive: true });
    mkdirSync(TEST_SKILLS_DIR, { recursive: true });

    setupTestSkill(
      'cost-intel',
      {
        name: 'Cost Intelligence',
        version: '1.2.0',
        description: 'Monitoreo de costos de modelos',
        category: 'analytics',
        trust_score: '0.92',
        tags: 'telemetry, cost, finance',
      },
      '# Cost Intelligence\n\n## Overview\nReal-time cost tracking.',
    );

    setupTestSkill(
      'evidence-ledger',
      {
        name: 'Evidence Ledger',
        version: '0.8.1',
        description: 'Auditoría con evidencia de verificación',
        category: 'security',
        trust_score: '0.88',
        tags: 'verification, audit, ledger',
      },
    );

    setupTestSkill(
      'bad-metadata',
      {},
    );
  });

  afterAll(() => {
    if (existsSync(TEST_SKILLS_DIR)) rmSync(TEST_SKILLS_DIR, { recursive: true });
  });

  it('listSkills parses frontmatter and returns metadata', async () => {
    const skills = await listSkills(TEST_SKILLS_DIR);
    expect(skills.length).toBe(3); // bad-metadata is listed with safe defaults
    const cost = skills.find((s) => s.name === 'cost-intel');
    expect(cost).toBeDefined();
    expect(cost?.version).toBe('1.2.0');
    expect(cost?.category).toBe('analytics');
    expect(cost?.trust_score).toBe(0.92);
    expect(cost?.tags).toContain('telemetry');
    expect(cost?.tags).toContain('finance');
  });

  it('getSkillsHandler returns valid response shape', async () => {
    const result = await getSkillsHandler(TEST_SKILLS_DIR);
    expect(result.total).toBe(3);
    expect(result.skills.length).toBe(3);
    expect(result.updated_at).toBeTruthy();
  });

  it('handles skills directory with no skills gracefully', async () => {
    const emptyDir = join(tmpdir(), 'cockpit-skills-empty-test');
    mkdirSync(emptyDir, { recursive: true });
    try {
      const skills = await listSkills(emptyDir);
      expect(skills.length).toBe(0);
    } finally {
      rmSync(emptyDir, { recursive: true });
    }
  });
});
