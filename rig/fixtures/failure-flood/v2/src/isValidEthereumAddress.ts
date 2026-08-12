const ETH_ADDRESS = /^0x[0-9a-fA-F]{40}$/;

/**
 * True for "0x" + exactly 40 hex chars. Case-insensitive — no EIP-55 checksum
 * enforcement, which would reject valid all-lowercase addresses.
 */
export function isValidEthereumAddress(address: string): boolean {
  return ETH_ADDRESS.test(address);
}
