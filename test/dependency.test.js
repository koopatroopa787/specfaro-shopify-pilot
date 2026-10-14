import assert from 'node:assert/strict';
import test from 'node:test';
import leftPad from 'left-pad';

test('the pilot can use a public npm dependency', () => {
  assert.equal(leftPad('x', 3, '0'), '00x');
});
