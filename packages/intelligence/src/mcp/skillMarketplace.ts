import { readdir, readFile, stat } from 'node:fs/promises';
import { join } from 'node:path';

export interface SkillMetadata {
  name: string;
  version: string;
  description?: string;
  category?: string;
  trust_score: number;
  tags: string[];
  file_path: string;
}

export async function listSkills(skillsDir: string = '/home/ubuntu/.hermes/skills'): Promise<SkillMetadata[]> {
  const entries = await readdir(skillsDir, { withFileTypes: true });
  const skills: SkillMetadata[] = [];

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const skillPath = join(skillsDir, entry.name);
    const skillFile = join(skillPath, 'SKILL.md');

    try {
      const stats = await stat(skillFile);
      if (!stats.isFile()) continue;
    } catch {
      continue;
    }

    const content = await readFile(skillFile, 'utf-8');
    const frontmatterEnd = content.indexOf('---', 3);
    const frontmatter = frontmatterEnd > 0 ? content.substring(3, frontmatterEnd).trim() : '';
    const metadata: Record<string, string> = {};

    for (const line of frontmatter.split('\n')) {
      const [key, ...valueParts] = line.split(':');
      if (!key) continue;
      const value = valueParts.join(':').trim();
      metadata[key.trim()] = value;
    }

    skills.push({
      name: entry.name,
      version: metadata.version ?? '0.0.0',
      description: metadata.description ?? '',
      category: metadata.category ?? 'general',
      trust_score: parseFloat(metadata.trust_score ?? '0.5'),
      tags: (metadata.tags ?? '').split(',').map(t => t.trim()).filter(Boolean),
      file_path: skillFile,
    });
  }

  return skills;
}

export async function getSkillsHandler() {
  try {
    const skills = await listSkills();
    return {
      skills,
      total: skills.length,
      updated_at: new Date().toISOString(),
    };
  } catch (error) {
    throw new Error(`Failed to list skills: ${error instanceof Error ? error.message : String(error)}`);
  }
}