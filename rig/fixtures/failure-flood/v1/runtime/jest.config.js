'use strict';

// This fixture's own Jest run — substrate under measurement, never this
// repo's verification surface (decisions/0015-a-...md, Clause A). All paths
// are resolved from __dirname (this file's real location under runtime/),
// never from process.cwd(), so the config works whether it is invoked from
// runtime/ (npm test / npx jest) or from the fixture root — and keeps
// working once a per-run materialisation copies src/, tests/, runtime/
// somewhere else with the same relative layout.

const path = require('path');

const RUNTIME_ROOT = __dirname;
const FIXTURE_ROOT = path.resolve(RUNTIME_ROOT, '..');

/** @type {import('jest').Config} */
module.exports = {
  rootDir: FIXTURE_ROOT,
  testEnvironment: 'node',
  testMatch: [path.join(FIXTURE_ROOT, 'tests', '**', '*.test.ts')],
  moduleFileExtensions: ['ts', 'js', 'json'],
  transform: {
    '^.+\\.ts$': [
      require.resolve('ts-jest'),
      { tsconfig: path.join(RUNTIME_ROOT, 'tsconfig.json') },
    ],
  },
};
