export const CONFIRM_POSITIONS = [2, 6, 10] as const;

export function getSeedWords(seed: string): string[] {
  return seed.trim().split(/\s+/);
}

export function isPickCorrect(seed: string, position: number, word: string): boolean {
  const seedWord = getSeedWords(seed)[position];
  return seedWord !== undefined && seedWord === word;
}

export function isConfirmCorrect(seed: string, picks: (string | null)[]): boolean {
  return CONFIRM_POSITIONS.every((position, index) => {
    const pick = picks[index];
    return pick != null && isPickCorrect(seed, position, pick);
  });
}
