import { expect, test } from 'vitest';
import { getStaffId } from '../src/staff.js';
import { isAssignedTo } from '../src/assignment.js';

test('reads the staffMember ID from a 2026-10 POS session', () => {
  const session = { staffMember: { value: { id: 'gid://shopify/StaffMember/123' } } };
  expect(getStaffId(session)).toBe('gid://shopify/StaffMember/123');
});

test('returns undefined when no staff member is pinned in', () => {
  expect(getStaffId({})).toBeUndefined();
});

test('matches the assigned staff member in a 2026-10 POS session', () => {
  const session = { staffMember: { value: { id: 'gid://shopify/StaffMember/123' } } };
  expect(isAssignedTo(session, 'gid://shopify/StaffMember/123')).toBe(true);
  expect(isAssignedTo(session, 'gid://shopify/StaffMember/456')).toBe(false);
});

test('does not match staff when no member is pinned in', () => {
  expect(isAssignedTo({}, 'gid://shopify/StaffMember/123')).toBe(false);
});
