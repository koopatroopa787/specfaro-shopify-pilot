import { getStaffId } from './staff.js';

export function isAssignedTo(session, staffId) {
  const currentStaffId = getStaffId(session);
  return currentStaffId !== undefined && currentStaffId === staffId;
}
