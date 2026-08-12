import { CONFIRM_POSITIONS, getSeedWords, isConfirmCorrect, isPickCorrect } from '../src/confirmSeed';

const SAMPLE_SEED =
  'abandon ability able about above absent absorb abstract absurd abuse access accident';
// words: [0]=abandon [1]=ability [2]=able [3]=about [4]=above [5]=absent [6]=absorb [7]=abstract [8]=absurd [9]=abuse [10]=access [11]=accident

describe('CONFIRM_POSITIONS', () => {
  it('is [2, 6, 10]', () => {
    expect(CONFIRM_POSITIONS).toEqual([2, 6, 10]);
  });
});

describe('getSeedWords', () => {
  it('splits a clean seed into 12 words', () => {
    expect(getSeedWords(SAMPLE_SEED)).toHaveLength(12);
  });

  it('trims leading and trailing whitespace', () => {
    expect(getSeedWords(`  ${SAMPLE_SEED}  `)).toHaveLength(12);
  });

  it('handles repeated internal spaces', () => {
    const spacey = SAMPLE_SEED.replace(/ /g, '   ');
    expect(getSeedWords(spacey)).toEqual(getSeedWords(SAMPLE_SEED));
  });

  it('returns individual words correctly', () => {
    const words = getSeedWords(SAMPLE_SEED);
    expect(words[0]).toBe('abandon');
    expect(words[2]).toBe('able');
    expect(words[11]).toBe('accident');
  });
});

describe('isPickCorrect', () => {
  it('returns true when the word at position matches', () => {
    expect(isPickCorrect(SAMPLE_SEED, 2, 'able')).toBe(true);
    expect(isPickCorrect(SAMPLE_SEED, 6, 'absorb')).toBe(true);
    expect(isPickCorrect(SAMPLE_SEED, 10, 'access')).toBe(true);
  });

  it('returns false when the word does not match', () => {
    expect(isPickCorrect(SAMPLE_SEED, 2, 'abandon')).toBe(false);
    expect(isPickCorrect(SAMPLE_SEED, 6, 'wrong')).toBe(false);
  });

  it('is case-sensitive', () => {
    expect(isPickCorrect(SAMPLE_SEED, 2, 'Able')).toBe(false);
  });
});

describe('isConfirmCorrect', () => {
  it('returns true when all picks match CONFIRM_POSITIONS', () => {
    // CONFIRM_POSITIONS = [2, 6, 10]
    // word[2] = 'able', word[6] = 'absorb', word[10] = 'access'
    expect(isConfirmCorrect(SAMPLE_SEED, ['able', 'absorb', 'access'])).toBe(true);
  });

  it('returns false when one pick is wrong', () => {
    expect(isConfirmCorrect(SAMPLE_SEED, ['able', 'wrong', 'access'])).toBe(false);
  });

  it('returns false when a pick is null', () => {
    expect(isConfirmCorrect(SAMPLE_SEED, ['able', null, 'access'])).toBe(false);
  });

  it('returns false when all picks are null', () => {
    expect(isConfirmCorrect(SAMPLE_SEED, [null, null, null])).toBe(false);
  });
});
