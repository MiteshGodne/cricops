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
    VENUE_DETAIL: (id) => `/venues/${id}/`,
  
    // players
    PLAYERS: '/players/',
    PLAYER_DETAIL: (id) => `/players/${id}/`,
  
    // teams
    TEAMS: '/teams/teams/',
    SQUADS: '/teams/squads/',
    TEAM_DETAIL: (id) => `/teams/teams/${id}/`,
    SQUAD_DETAIL: (id) => `/teams/squads/${id}/`,
  
    // tournaments
    REGULATIONS: '/tournaments/regulations/',
    REGULATION_DETAIL: (id) => `/tournaments/regulations/${id}/`,
    TOURNAMENTS: '/tournaments/tournaments/',
    TOURNAMENT_DETAIL: (id) => `/tournaments/tournaments/${id}/`,
    APPLICATIONS: '/tournaments/applications/',
    APPLICATION_DETAIL: (id) => `/tournaments/applications/${id}/`,
    SUBMIT_APPLICATION: '/tournaments/applications/submit-application/',
    REAPPLY: (id) => `/tournaments/applications/${id}/reapply/`,
    GROUPS: '/tournaments/groups/',
    STANDINGS: '/tournaments/standings/',
    GROUP_DETAIL: (id) => `/tournaments/groups/${id}/`,
    ORGANIZERS: '/tournaments/organizers/',
    OPEN_TOURNAMENTS: '/tournaments/organizers/open/',

    UMPIRES_PENDING: '/accounts/users/?apply_for=UMPIRE&role=PENDING',
    APPROVE_UMPIRE_GLOBAL: '/matches/umpires/approve/',
  
    // matches
    MATCHES: '/matches/matches/',
    MATCH_DETAIL: (id) => `/matches/matches/${id}/`,
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