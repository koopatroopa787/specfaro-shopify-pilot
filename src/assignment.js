export function isAssignedTo(session, staffId) {
  const staffMemberId = session.staffMember?.value?.id;
  return staffMemberId !== undefined && staffMemberId === staffId;
}
