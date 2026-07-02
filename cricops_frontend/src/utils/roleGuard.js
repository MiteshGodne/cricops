export const canManageTournament = (user) => user?.role === 'ORGANIZER';
export const canManageTeam = (user) => user?.role === 'TEAMHEAD';
export const canScore = (user) => user?.role === 'UMPIRE';