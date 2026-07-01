export const ROLES = {
  PENDING: 'PENDING',
  ORGANIZER: 'ORGANIZER',
  TEAMHEAD: 'TEAMHEAD',
  UMPIRE: 'UMPIRE',
  VIEWER: 'VIEWER',
  REJECTED: 'REJECTED',
};

export const isOrganizer = (user) => user?.role === ROLES.ORGANIZER;
export const isTeamHead = (user) => user?.role === ROLES.TEAMHEAD;
export const isUmpire = (user) => user?.role === ROLES.UMPIRE;
