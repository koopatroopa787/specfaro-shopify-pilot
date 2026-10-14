export function isAssignedTo(session, staffId) {
  const assignedStaffId = session.staffMember?.value?.id;
  return assignedStaffId !== undefined && assignedStaffId === staffId;
}
