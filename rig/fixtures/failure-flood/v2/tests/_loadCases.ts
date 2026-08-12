import * as fs from 'fs';
import * as path from 'path';

/**
 * Loads a generated, amplified case table for `moduleName` (tools/generate-
 * cases.py, design.md Decision 9a). Returns `[]` when `FAILURE_FLOOD_CASE_DIR`
 * is unset or the file is missing — this keeps the clean fixture's own base
 * suite (verified 6 suites / 59 tests / 0 failures at sdd/failure-flood-
 * triage PR3a-ii) byte-for-byte unaffected until a real run generates cases
 * into a machine-local directory outside <repo>; nothing amplified is ever
 * committed. Filename does not end in `.test.ts`, so Jest's `testMatch`
 * never treats this file as a suite of its own.
 */
export function loadCases(moduleName: string): any[] {
  const dir = process.env.FAILURE_FLOOD_CASE_DIR;
  if (!dir) return [];
  const file = path.join(dir, `${moduleName}.json`);
  if (!fs.existsSync(file)) return [];
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}
