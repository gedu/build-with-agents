import { formatTokenAmount } from '../src/formatTokenAmount';
import { loadCases } from './_loadCases';

describe('formatTokenAmount', () => {
  it('converts a whole amount (no fractional part)', () => {
    expect(formatTokenAmount('1000000', 6)).toBe('1.00');
  });

  it('converts a fractional amount', () => {
    expect(formatTokenAmount('12500000', 6)).toBe('12.50');
  });

  it('returns "0.00" for zero', () => {
    expect(formatTokenAmount('0', 6)).toBe('0.00');
  });

  it('returns "0.00" for null', () => {
    expect(formatTokenAmount(null, 6)).toBe('0.00');
  });

  it('returns "0.00" for undefined', () => {
    expect(formatTokenAmount(undefined, 6)).toBe('0.00');
  });

  it('returns "0.00" for empty string', () => {
    expect(formatTokenAmount('', 6)).toBe('0.00');
  });

  it('truncates (does not round up) when more than 2 decimal places', () => {
    // 1999999 base units / 10^6 = 1.999999 — must truncate to 1.99, not round to 2.00
    expect(formatTokenAmount('1999999', 6)).toBe('1.99');
  });

  it('handles a large amount without float precision loss', () => {
    // 999999999999000000 base units / 10^6 = 999999999999.00
    expect(formatTokenAmount('999999999999000000', 6)).toBe('999999999999.00');
  });
});

// Amplified table (tools/generate-cases.py, design.md Decision 9a). `[]`
// when no case table was generated for this run — see ./_loadCases.ts.
const amplified = loadCases('formatTokenAmount');
const describeAmplified = amplified.length > 0 ? describe : describe.skip;

describeAmplified('formatTokenAmount (amplified)', () => {
  it.each(amplified.map((c: any) => [c.case_id, c.baseUnits, c.decimals, c.expected]))(
    'case %i: formatTokenAmount(%j, %j) -> %j',
    (_caseId: number, baseUnits: string | null, decimals: number, expected: string) => {
      expect(formatTokenAmount(baseUnits, decimals)).toBe(expected);
    },
  );
});
