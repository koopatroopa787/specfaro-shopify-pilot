export function isAssignedTo(session, staffId) {
  const currentStaffId = session?.staffMember?.value?.id;
  return currentStaffId !== undefined && currentStaffId === staffId;
}
