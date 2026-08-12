import { applyKeypadInput } from '../src/applyKeypadInput';
import { loadCases } from './_loadCases';

const MAX = 6;

describe('applyKeypadInput', () => {
  it('appends the first digit to an empty value', () => {
    expect(applyKeypadInput('', '5', MAX)).toBe('5');
  });

  it('appends a digit to an existing value', () => {
    expect(applyKeypadInput('5', '0', MAX)).toBe('50');
  });

  it('replaces a lone leading zero with a non-zero digit', () => {
    expect(applyKeypadInput('0', '7', MAX)).toBe('7');
  });

  it('keeps a single zero when zero is pressed on zero', () => {
    expect(applyKeypadInput('0', '0', MAX)).toBe('0');
  });

  it('starts a decimal from empty as "0."', () => {
    expect(applyKeypadInput('', '.', MAX)).toBe('0.');
  });

  it('starts a decimal from zero as "0."', () => {
    expect(applyKeypadInput('0', '.', MAX)).toBe('0.');
  });

  it('appends a decimal point to an integer', () => {
    expect(applyKeypadInput('12', '.', MAX)).toBe('12.');
  });

  it('ignores a second decimal point', () => {
    expect(applyKeypadInput('12.5', '.', MAX)).toBe('12.5');
  });

  it('appends a digit after the decimal point', () => {
    expect(applyKeypadInput('0.', '5', MAX)).toBe('0.5');
  });

  it('ignores digits past the decimal cap', () => {
    expect(applyKeypadInput('1.123456', '7', MAX)).toBe('1.123456');
  });

  it('appends the last allowed decimal digit', () => {
    expect(applyKeypadInput('1.12345', '6', MAX)).toBe('1.123456');
  });

  it('backspace removes the last character', () => {
    expect(applyKeypadInput('12', 'back', MAX)).toBe('1');
  });

  it('backspace on a single character yields empty', () => {
    expect(applyKeypadInput('1', 'back', MAX)).toBe('');
  });

  it('backspace on empty stays empty', () => {
    expect(applyKeypadInput('', 'back', MAX)).toBe('');
  });

  it('backspace removes a trailing decimal point', () => {
    expect(applyKeypadInput('12.', 'back', MAX)).toBe('12');
  });
});

// Amplified table (tools/generate-cases.py, design.md Decision 9a). `[]`
// when no case table was generated for this run — see ./_loadCases.ts.
const amplified = loadCases('applyKeypadInput');
const describeAmplified = amplified.length > 0 ? describe : describe.skip;

describeAmplified('applyKeypadInput (amplified)', () => {
  it.each(amplified.map((c: any) => [c.case_id, c.current, c.key, c.maxDecimals, c.expected]))(
    'case %i: applyKeypadInput(%j, %j, %j) -> %j',
    (_caseId: number, current: string, key: string, maxDecimals: number, expected: string) => {
      expect(applyKeypadInput(current, key as any, maxDecimals)).toBe(expected);
    },
  );
});
