import js from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  { ignores: ['node_modules/', 'test-results/', 'playwright-report.json'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  { files: ['**/*.mjs'], languageOptions: { globals: { process: 'readonly', setTimeout: 'readonly' } } },
  { files: ['**/*.ts'], rules: { '@typescript-eslint/no-explicit-any': 'off' } },
);
