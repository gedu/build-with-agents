export type KeypadKey =
  | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '.' | 'back';

/**
 * Applies one custom-keypad press to the current amount string.
 * - A digit on a lone "0" replaces it (no leading zeros).
 * - Only one decimal point is allowed; "." on an empty value yields "0.".
 * - Fractional digits are capped at `maxDecimals`.
 * - "back" removes the last character.
 */
export function applyKeypadInput(current: string, key: KeypadKey, maxDecimals: number): string {
  if (key === 'back') {
    return current.slice(0, -1);
  }

  if (key === '.') {
    if (current.includes('.')) return current;
    if (current === '') return '0.';
    return `${current}.`;
  }

  // key is a digit
  if (current === '' || current === '0') {
    return key === '0' ? '0' : key;
  }

  const dotIndex = current.indexOf('.');
  if (dotIndex !== -1 && current.length - dotIndex - 1 > maxDecimals) {
    return current;
  }

  return current + key;
}
