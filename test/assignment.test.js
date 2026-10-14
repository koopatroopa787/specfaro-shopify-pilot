import assert from 'node:assert/strict';
import test from 'node:test';
import { isAssignedTo } from '../src/assignment.js';

test('matches a pinned staff member in a 2026-10 POS session', () => {
  const id = 'gid://shopify/StaffMember/123';
  const session = { staffMember: { value: { id } } };
  assert.equal(isAssignedTo(session, id), true);
});

test('never assigns an absent staff member in a 2026-10 POS session', () => {
  assert.equal(isAssignedTo({}, undefined), false);
});
