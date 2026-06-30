export const ENDPOINTS = {
    // accounts
    REGISTER: '/accounts/register/',
    LOGIN: '/accounts/login/',
    REFRESH: '/accounts/token/refresh/',
    ME: '/accounts/me/',
    USERS: '/accounts/users/',
    APPROVE_ORGANIZER: (id) => `/accounts/users/${id}/approve-organizer/`,
    REJECT_USER: (id) => `/accounts/users/${id}/reject/`,
  
    // venues
    VENUES: '/venues/',
  
    // players
    PLAYERS: '/players/',
  
    // teams
    TEAMS: '/teams/teams/',
    SQUADS: '/teams/squads/',
  
    // tournaments
    REGULATIONS: '/tournaments/regulations/',
    TOURNAMENTS: '/tournaments/tournaments/',
    APPLICATIONS: '/tournaments/applications/',
    SUBMIT_APPLICATION: '/tournaments/applications/submit-application/',
    REAPPLY: (id) => `/tournaments/applications/${id}/reapply/`,
    GROUPS: '/tournaments/groups/',
    STANDINGS: '/tournaments/standings/',
    ORGANIZERS: '/tournaments/organizers/',
    OPEN_TOURNAMENTS: '/tournaments/organizers/open/',
  
    // matches
    MATCHES: '/matches/matches/',
    ABANDON_MATCH: (id) => `/matches/matches/${id}/abandon/`,
    ASSIGN_UMPIRE: (id) => `/matches/matches/${id}/assign-umpire/`,
    TEAM_MATCHES: '/matches/team-matches/',
    SUBMIT_TOSS: '/matches/team-matches/submit-toss/',
    INNINGS: '/matches/innings/',
    DELIVERIES: '/matches/deliveries-list/',
    SUBMIT_DELIVERY: '/matches/deliveries/submit/',
    LIVE_SCORE: (matchId) => `/matches/matches/${matchId}/live-score/`,
    SWAP_STRIKER: (matchId) => `/matches/matches/${matchId}/swap-striker/`,
    APPROVE_UMPIRE: '/matches/umpires/approve/',
  };