export function isAssignedTo(session, staffId) {
  const assignedId = session?.staffMember?.value?.id;
  return assignedId != null && assignedId === staffId;
}
