import assert from 'node:assert/strict';
import test from 'node:test';
import { getStaffId } from '../src/staff.js';
import { isAssignedTo } from '../src/assignment.js';

test('reads the staff member ID from a 2026-10 POS session', () => {
  const session = { staffMember: { value: { id: 'gid://shopify/StaffMember/123' } } };
  assert.equal(getStaffId(session), 'gid://shopify/StaffMember/123');
});

test('returns undefined when no staff member is pinned in', () => {
  assert.equal(getStaffId({}), undefined);
});

test('matches the assigned staff member in a 2026-10 POS session', () => {
  const session = { staffMember: { value: { id: 'gid://shopify/StaffMember/123' } } };
  assert.equal(isAssignedTo(session, 'gid://shopify/StaffMember/123'), true);
  assert.equal(isAssignedTo(session, 'gid://shopify/StaffMember/456'), false);
});

test('does not match staff when no member is pinned in', () => {
  assert.equal(isAssignedTo({}, 'gid://shopify/StaffMember/123'), false);
});
