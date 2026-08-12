import { decodeBalanceHex, encodeBalanceOf } from '../src/balanceOfCall';

const ADDRESS = '0x998Cb71fC83Df5E21a3927E8861Aa33995522175';

describe('encodeBalanceOf', () => {
  it('builds balanceOf calldata: selector + left-padded address', () => {
    expect(encodeBalanceOf(ADDRESS)).toBe(
      '0x70a08231000000000000000000000000998cb71fc83df5e21a3927e8861aa33995522175',
    );
  });

  it('lowercases the address', () => {
    expect(encodeBalanceOf(ADDRESS)).toBe(encodeBalanceOf(ADDRESS.toLowerCase()));
  });

  it('produces a 0x + 8 selector + 64 data hex string', () => {
    expect(encodeBalanceOf(ADDRESS)).toHaveLength(74);
  });
});

describe('decodeBalanceHex', () => {
  it('decodes a uint256 hex result to a base-units string', () => {
    expect(
      decodeBalanceHex('0x00000000000000000000000000000000000000000000000000000000035a405e'),
    ).toBe('56246366');
  });

  it('returns "0" for an all-zero result', () => {
    expect(decodeBalanceHex(`0x${'0'.repeat(64)}`)).toBe('0');
  });

  it('returns "0" for a bare 0x result', () => {
    expect(decodeBalanceHex('0x')).toBe('0');
  });

  it('returns "0" for an empty string', () => {
    expect(decodeBalanceHex('')).toBe('0');
  });
});
