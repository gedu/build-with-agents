import { isValidEthereumAddress } from '../src/isValidEthereumAddress';
import { loadCases } from './_loadCases';

describe('isValidEthereumAddress', () => {
  it('accepts a 0x-prefixed 40-hex-char address', () => {
    expect(isValidEthereumAddress('0x1234567890abcdef1234567890abcdef12345678')).toBe(true);
  });

  it('accepts a mixed-case (checksummed) address without enforcing the checksum', () => {
    expect(isValidEthereumAddress('0xaA8E23Fb1079EA71e0a56F48a2aA51851D8433D0')).toBe(true);
  });

  it('rejects an address that is too short', () => {
    expect(isValidEthereumAddress('0x123')).toBe(false);
  });

  it('rejects an address that is too long', () => {
    expect(isValidEthereumAddress('0x1234567890abcdef1234567890abcdef123456789')).toBe(false);
  });

  it('rejects an address missing the 0x prefix', () => {
    expect(isValidEthereumAddress('1234567890abcdef1234567890abcdef12345678')).toBe(false);
  });

  it('rejects an address with a non-hex character', () => {
    expect(isValidEthereumAddress('0x1234567890abcdef1234567890abcdef1234567g')).toBe(false);
  });

  it('rejects an empty string', () => {
    expect(isValidEthereumAddress('')).toBe(false);
  });

  it('rejects the bare 0x prefix', () => {
    expect(isValidEthereumAddress('0x')).toBe(false);
  });
});

// Amplified table (tools/generate-cases.py, design.md Decision 9a). `[]`
// when no case table was generated for this run — see ./_loadCases.ts.
const amplified = loadCases('isValidEthereumAddress');
const describeAmplified = amplified.length > 0 ? describe : describe.skip;

describeAmplified('isValidEthereumAddress (amplified)', () => {
  it.each(amplified.map((c: any) => [c.case_id, c.address, c.expected]))(
    'case %i: isValidEthereumAddress(%j) -> %j',
    (_caseId: number, address: string, expected: boolean) => {
      expect(isValidEthereumAddress(address)).toBe(expected);
    },
  );
});
