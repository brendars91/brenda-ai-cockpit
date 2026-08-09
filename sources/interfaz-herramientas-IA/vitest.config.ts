import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['**/tests/**/*.test.ts'],
    passWithNoTests: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'html'],
      thresholds: {
        branches: 85,
        functions: 85,
        lines: 85,
        statements: 85,
      },
      include: [
        'packages/*/src/**/*.ts',
        'packages/adapters/*/src/**/*.ts',
        'orchestrator/src/**/*.ts',
      ],
    },
  },
});
