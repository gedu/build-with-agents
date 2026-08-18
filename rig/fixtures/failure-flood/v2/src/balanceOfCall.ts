// ERC-20 balanceOf(address) — selector keccak256("balanceOf(address)")[:4].
const BALANCE_OF_SELECTOR = '0x70a08231';
const ADDRESS_PADDING = 63;

/**
 * Builds the `data` for an `eth_call` to ERC-20 `balanceOf(address)`:
 * the selector followed by the account address left-padded to 32 bytes.
 */
export function encodeBalanceOf(accountAddress: string): string {
  const address = accountAddress.toLowerCase().replace(/^0x/, '');
  return BALANCE_OF_SELECTOR + address.padStart(ADDRESS_PADDING, '0');
}

/**
 * Decodes an `eth_call` uint256 result into a base-units string. A bare "0x"
 * or empty result (no data) is read as zero.
 */
export function decodeBalanceHex(resultHex: string): string {
  if (resultHex === '' || resultHex === '0x') return '0';
  return BigInt(resultHex).toString();
}
