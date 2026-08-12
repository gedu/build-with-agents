export type TransactionDirection = 'in' | 'out';

/** A transfer as returned by a token-transfers indexer endpoint. */
export type IndexerTransfer = {
  transactionHash: string;
  blockNumber: number;
  amount: string;
  timestamp: number;
  from: string;
  to: string;
  label: string;
};

/** The app's transaction model — one row of activity. */
export type Transaction = {
  hash: string;
  direction: TransactionDirection;
  peer: string;
  amount: string;
  timestamp: number;
  blockNumber: number;
  feeAmount: string | null;
};

const TRANSACTION_LABEL = 'transaction';
const PAYMASTER_LABEL = 'paymasterTransaction';

/**
 * Maps raw indexer transfers to the app's Transaction list: keeps only the
 * real transfers (the paired `paymasterTransaction` rows become each outgoing
 * tx's fee), derives direction/peer against the account, and sorts newest-first.
 */
export function parseTransfers(transfers: IndexerTransfer[], account: string): Transaction[] {
  const accountLc = account.toLowerCase();

  const feeByHash = new Map<string, string>();
  for (const transfer of transfers) {
    if (transfer.label === PAYMASTER_LABEL) {
      feeByHash.set(transfer.transactionHash, transfer.amount);
    }
  }

  return transfers
    .filter((transfer) => transfer.label === TRANSACTION_LABEL)
    .map((transfer): Transaction => {
      const direction: TransactionDirection =
        transfer.to.toLowerCase() === accountLc ? 'in' : 'out';
      return {
        hash: transfer.transactionHash,
        direction,
        peer: direction === 'in' ? transfer.from : transfer.to,
        amount: transfer.amount,
        timestamp: transfer.timestamp,
        blockNumber: transfer.blockNumber,
        feeAmount: direction === 'out' ? (feeByHash.get(transfer.transactionHash) ?? null) : null,
      };
    })
    .sort((a, b) => b.timestamp - a.timestamp);
}
