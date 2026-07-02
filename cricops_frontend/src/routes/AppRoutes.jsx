import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import { useAuth } from '../context/AuthContext';
import { ROLES } from '../constants/roles';

import Login from '../features/accounts/pages/Login';
import Register from '../features/accounts/pages/Register';
import ProfileDashboard from '../features/accounts/pages/ProfileDashboard';
import VenueListView from '../features/venues/pages/VenueListView';
import PlayerDirectory from '../features/players/pages/PlayerDirectory';
import TournamentBrowse from '../features/tournaments/pages/TournamentBrowse';

import OrganizerDashboard from '../features/organizer/pages/OrganizerDashboard';
import TournamentForm from '../features/organizer/pages/TournamentForm';
import TournamentManage from '../features/organizer/pages/TournamentManage';
import MatchManage from '../features/organizer/pages/MatchManage';

import TeamHeadDashboard from '../features/teamhead/pages/TeamHeadDashboard';
import ManageSquad from '../features/teamhead/pages/ManageSquad';
import ApplyTournament from '../features/teamhead/pages/ApplyTournament';

import UmpireDashboard from '../features/matches/pages/UmpireDashboard';
import UmpireScoringConsole from '../features/matches/pages/UmpireScoringConsole';
import MatchCenterListView from '../features/matches/pages/MatchCenterListView';

import TournamentDetail from '../features/tournaments/pages/TournamentDetail';

function RoleHome() {
  const { user } = useAuth();
  if (!user) return <TournamentBrowse />;
  if (user.role === ROLES.ORGANIZER) return <Navigate to="/organizer" replace />;
  if (user.role === ROLES.TEAMHEAD) return <Navigate to="/teamhead" replace />;
  if (user.role === ROLES.UMPIRE) return <Navigate to="/umpire" replace />;
  return <TournamentBrowse />;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<RoleHome />} />
      <Route path="/tournaments" element={<TournamentBrowse />} />
      <Route path="/matches" element={<MatchCenterListView />} />
      <Route path="/venues" element={<VenueListView />} />
      <Route path="/players" element={<PlayerDirectory />} />
      <Route path="/profile" element={<ProtectedRoute><ProfileDashboard /></ProtectedRoute>} />
      <Route path="/tournaments/:id" element={<TournamentDetail />} />

      {/* ORGANIZER */}
      <Route path="/organizer" element={<ProtectedRoute allowedRoles={[ROLES.ORGANIZER]}><OrganizerDashboard /></ProtectedRoute>} />
      <Route path="/organizer/tournaments/new" element={<ProtectedRoute allowedRoles={[ROLES.ORGANIZER]}><TournamentForm /></ProtectedRoute>} />
      <Route path="/organizer/tournaments/:id/edit" element={<ProtectedRoute allowedRoles={[ROLES.ORGANIZER]}><TournamentForm /></ProtectedRoute>} />
      <Route path="/organizer/tournaments/:id/manage" element={<ProtectedRoute allowedRoles={[ROLES.ORGANIZER]}><TournamentManage /></ProtectedRoute>} />
      <Route path="/organizer/matches/:matchId/manage" element={<ProtectedRoute allowedRoles={[ROLES.ORGANIZER]}><MatchManage /></ProtectedRoute>} />

      {/* TEAMHEAD */}
      <Route path="/teamhead" element={<ProtectedRoute allowedRoles={[ROLES.TEAMHEAD]}><TeamHeadDashboard /></ProtectedRoute>} />
      <Route path="/teamhead/teams/:teamId/squad/:tournamentId" element={<ProtectedRoute allowedRoles={[ROLES.TEAMHEAD]}><ManageSquad /></ProtectedRoute>} />
      <Route path="/teamhead/apply" element={<ProtectedRoute allowedRoles={[ROLES.TEAMHEAD]}><ApplyTournament /></ProtectedRoute>} />

      {/* UMPIRE */}
      <Route path="/umpire" element={<ProtectedRoute allowedRoles={[ROLES.UMPIRE]}><UmpireDashboard /></ProtectedRoute>} />
      <Route path="/matches/:matchId/score" element={<ProtectedRoute allowedRoles={[ROLES.UMPIRE]}><UmpireScoringConsole /></ProtectedRoute>} />
    </Routes>
  );
}