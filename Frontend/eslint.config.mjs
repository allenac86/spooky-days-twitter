import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';
import stylistic from '@stylistic/eslint-plugin';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';

export default [
  {
    files: ['app/**/*.tsx', 'app/**/*.ts'],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module',
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        React: 'readonly',
        process: 'readonly',
        console: 'readonly',
      },
    },
    plugins: {
      '@typescript-eslint': tseslint,
      '@stylistic': stylistic,
      'react': react,
      'react-hooks': reactHooks,
    },
    rules: {
      'no-console': 'off',
      '@stylistic/arrow-parens': ['error', 'always'],
      '@stylistic/arrow-spacing': ['error', { 'before': true, 'after': true }],
      '@stylistic/block-spacing': 'error',
      '@stylistic/comma-spacing': ['error', { 'before': false, 'after': true }],
      '@stylistic/eol-last': ['error', 'always'],
      '@stylistic/indent': ['error', 2],
      '@stylistic/jsx-closing-bracket-location': "error",
      '@stylistic/jsx-closing-tag-location': "error",
      '@stylistic/jsx-curly-newline': "error",
      '@stylistic/jsx-equals-spacing': ["error", "never"],
      '@stylistic/jsx-first-prop-new-line': ["error", "always"],
      '@stylistic/jsx-indent-props': ["error", 2],
      '@stylistic/lines-between-class-members': ['error', 'always'],
      '@stylistic/max-len': ['error', { 'code': 88 }],
      '@stylistic/max-statements-per-line': ['error', { 'max': 1 }],
      '@stylistic/multiline-ternary': ['error', 'always'],
      '@stylistic/newline-per-chained-call': ['error', { 'ignoreChainWithDepth': 2 }],
      '@stylistic/no-mixed-spaces-and-tabs': 'error',
      '@stylistic/no-multi-spaces': 'error',
      '@stylistic/no-multiple-empty-lines': 'error',
      '@stylistic/no-trailing-spaces': 'error',
      '@stylistic/object-curly-spacing': ['error', 'always'],
      '@stylistic/padding-line-between-statements': [
        'error',
        { blankLine: 'always', prev: '*', next: 'return' },
        { blankLine: 'always', prev: ['const', 'let', 'var'], next: '*'},
        { blankLine: 'never', prev: ['const', 'let', 'var'], next: ['const', 'let', 'var'] },
      ],
      '@stylistic/quotes': ['error', 'single', { avoidEscape: true }],
      '@stylistic/semi': ['error', 'always'],
      '@stylistic/space-before-blocks': 'error',
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
];