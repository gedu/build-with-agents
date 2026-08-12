import { parseTransfers, type IndexerTransfer } from '../src/parseTransfers';
import { loadCases } from './_loadCases';

const ACCOUNT = '0x998Cb71fC83Df5E21a3927E8861Aa33995522175';
const ACCOUNT_LC = ACCOUNT.toLowerCase();
const OTHER = '0xdd1ffde9c04268d555b1f965c510b2d46bc230c3';
const PAYMASTER = '0x8b1f6cb5d062aa2ce8d581942bbb960420d875ba';

function transfer(overrides: Partial<IndexerTransfer>): IndexerTransfer {
  return {
    transactionHash: '0xhash',
    blockNumber: 100,
    amount: '10.0',
    timestamp: 1000,
    from: ACCOUNT_LC,
    to: OTHER,
    label: 'transaction',
    ...overrides,
  };
}

describe('parseTransfers', () => {
  it('returns an empty array for no transfers', () => {
    expect(parseTransfers([], ACCOUNT)).toEqual([]);
  });

  it('maps an incoming transfer (to === account)', () => {
    const [tx] = parseTransfers([transfer({ from: OTHER, to: ACCOUNT_LC })], ACCOUNT);
    expect(tx).toMatchObject({ direction: 'in', peer: OTHER, amount: '10.0' });
  });

  it('maps an outgoing transfer with peer = recipient', () => {
    const [tx] = parseTransfers([transfer({ from: ACCOUNT_LC, to: OTHER })], ACCOUNT);
    expect(tx).toMatchObject({ direction: 'out', peer: OTHER });
  });

  it('drops paymasterTransaction rows from the result', () => {
    const result = parseTransfers(
      [
        transfer({ transactionHash: '0xa', label: 'transaction' }),
        transfer({ transactionHash: '0xa', label: 'paymasterTransaction', to: PAYMASTER }),
      ],
      ACCOUNT,
    );
    expect(result).toHaveLength(1);
    expect(result[0]?.hash).toBe('0xa');
  });

  it('attaches the fee from a same-hash paymasterTransaction to an outgoing tx', () => {
    const [tx] = parseTransfers(
      [
        transfer({ transactionHash: '0xa', from: ACCOUNT_LC, to: OTHER, amount: '12.0' }),
        transfer({
          transactionHash: '0xa',
          label: 'paymasterTransaction',
          from: ACCOUNT_LC,
          to: PAYMASTER,
          amount: '1.482513',
        }),
      ],
      ACCOUNT,
    );
    expect(tx?.feeAmount).toBe('1.482513');
  });

  it('leaves feeAmount null for an outgoing tx with no paymaster row', () => {
    const [tx] = parseTransfers([transfer({ from: ACCOUNT_LC, to: OTHER })], ACCOUNT);
    expect(tx?.feeAmount).toBeNull();
  });

  it('leaves feeAmount null for an incoming tx', () => {
    const [tx] = parseTransfers([transfer({ from: OTHER, to: ACCOUNT_LC })], ACCOUNT);
    expect(tx?.feeAmount).toBeNull();
  });

  it('matches the account address case-insensitively', () => {
    const [tx] = parseTransfers([transfer({ from: OTHER, to: ACCOUNT_LC })], ACCOUNT.toUpperCase());
    expect(tx?.direction).toBe('in');
  });

  it('sorts transactions newest-first by timestamp', () => {
    const result = parseTransfers(
      [
        transfer({ transactionHash: '0xold', timestamp: 1000 }),
        transfer({ transactionHash: '0xnew', timestamp: 3000 }),
        transfer({ transactionHash: '0xmid', timestamp: 2000 }),
      ],
      ACCOUNT,
    );
    expect(result.map((t) => t.hash)).toEqual(['0xnew', '0xmid', '0xold']);
  });
});

// Amplified table (tools/generate-cases.py, design.md Decision 9a). `[]`
// when no case table was generated for this run — see ./_loadCases.ts.
const amplified = loadCases('parseTransfers');
const describeAmplified = amplified.length > 0 ? describe : describe.skip;

describeAmplified('parseTransfers (amplified)', () => {
  it.each(amplified.map((c: any) => [c.case_id, c.transfers, c.account, c.expected]))(
    'case %i',
    (_caseId: number, transfers: IndexerTransfer[], account: string, expected: unknown) => {
      expect(parseTransfers(transfers, account)).toEqual(expected);
    },
  );
});
