import assert from 'node:assert/strict';
import test from 'node:test';
import { getStaffId } from '../src/staff.js';

test('reads the staff member ID from a 2026-10 POS session', () => {
  const session = { staffMember: { value: { id: 'gid://shopify/StaffMember/123' } } };
  assert.equal(getStaffId(session), 'gid://shopify/StaffMember/123');
});

test('returns undefined when no staff member is pinned in', () => {
  assert.equal(getStaffId({}), undefined);
});
