import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';
import stylistic from '@stylistic/eslint-plugin';

export default [
  {
    files: ['src/**/*.ts'],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module',
      },
      globals: {
        process: 'readonly',
        console: 'readonly',
      },
    },
    plugins: {
      '@typescript-eslint': tseslint,
      '@stylistic': stylistic,
    },
    rules: {
      'no-console': 'off',
      '@stylistic/arrow-parens': ['error', 'always'],
      '@stylistic/arrow-spacing': ['error', { 'before': true, 'after': true }],
      '@stylistic/block-spacing': 'error',
      '@stylistic/comma-spacing': ['error', { 'before': false, 'after': true }],
      '@stylistic/eol-last': ['error', 'always'],
      '@stylistic/indent': ['error', 2],
      '@stylistic/lines-between-class-members': ['error', 'always'],
      '@stylistic/max-len': ['error', { 'code': 88 }],
      '@stylistic/max-statements-per-line': ['error', { 'max': 1 }],
      '@stylistic/multiline-ternary': ['error', 'always'],
      '@stylistic/newline-per-chained-call': ['error', { 'ignoreChainWithDepth': 2 }],
      '@stylistic/no-mixed-spaces-and-tabs': 'error',
      '@stylistic/no-multi-spaces': 'error',
      '@stylistic/no-multiple-empty-lines': 'error',
      '@stylistic/object-curly-spacing': ['error', 'always'],
      '@stylistic/quotes': ['error', 'single', { avoidEscape: true }],
      '@stylistic/padding-line-between-statements': [
        'error',
        { blankLine: 'always', prev: '*', next: 'return' },
        { blankLine: 'always', prev: ['const', 'let', 'var'], next: '*'},
        { blankLine: 'never', prev: ['const', 'let', 'var'], next: ['const', 'let', 'var'] },
      ],
      '@stylistic/semi': ['error', 'always'],
      '@stylistic/space-before-blocks': 'error',
      '@stylistic/no-trailing-spaces': 'error',
    },
  },
];