import { expect, test } from 'vitest';
import leftPad from 'left-pad';

test('the pilot can use a public npm dependency', () => {
  expect(leftPad('x', 3, '0')).toBe('00x');
});
