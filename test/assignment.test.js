import { expect, test } from 'vitest';
import { isAssignedTo } from '../src/assignment.js';

test('matches a pinned staff member in a 2026-10 POS session', () => {
  const id = 'gid://shopify/StaffMember/123';
  const session = { staffMember: { value: { id } } };
  expect(isAssignedTo(session, id)).toBe(true);
});

test('never assigns an absent staff member in a 2026-10 POS session', () => {
  expect(isAssignedTo({}, undefined)).toBe(false);
});
