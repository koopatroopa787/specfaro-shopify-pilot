export function isAssignedTo(session, staffId) {
  return session.currentSession.staffMemberId === staffId;
}
