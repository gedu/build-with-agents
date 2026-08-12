/**
 * Converts a token amount in base units to a fixed 2-decimal display string.
 * Uses BigInt arithmetic to avoid float precision loss on large values.
 * Truncates (does not round up) — a balance must never display larger than it is.
 *
 * @example formatTokenAmount("12500000", 6) // "12.50"
 * @example formatTokenAmount("1999999", 6)  // "1.99" (truncated, not "2.00")
 */
export function formatTokenAmount(
  baseUnits: string | null | undefined,
  decimals: number,
): string {
  if (baseUnits == null || baseUnits === '') return '0.00';

  const raw = BigInt(baseUnits);
  const divisor = BigInt(10) ** BigInt(decimals);

  // Integer part
  const wholePart = raw / divisor;

  // Fractional part — we want exactly 2 decimal places, truncated.
  // Scale down to 2 dp by dividing by 10^(decimals-2).
  const centsDivisor = BigInt(10) ** BigInt(Math.max(decimals - 2, 0));
  const remainder = raw % divisor;
  const cents = remainder / centsDivisor; // truncates automatically (integer division)

  return `${wholePart.toString()}.${cents.toString().padStart(2, '0')}`;
}
