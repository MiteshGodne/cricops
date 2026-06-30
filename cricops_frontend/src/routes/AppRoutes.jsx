import { Routes, Route } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import Login from '../features/accounts/pages/Login';
import Register from '../features/accounts/pages/Register';
import ProfileDashboard from '../features/accounts/pages/ProfileDashboard';
import VenueListView from '../features/venues/pages/VenueListView';
import PlayerDirectory from '../features/players/pages/PlayerDirectory';
import TeamDashboard from '../features/teams/pages/TeamDashboard';
import ManageSquad from '../features/teams/pages/ManageSquad';
import TournamentBrowse from '../features/tournaments/pages/TournamentBrowse';
import TournamentControlPanel from '../features/tournaments/pages/TournamentControlPanel';
import MatchCenterListView from '../features/matches/pages/MatchCenterListView';
import UmpireScoringConsole from '../features/matches/pages/UmpireScoringConsole';
import { ROLES } from '../constants/roles';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<TournamentBrowse />} />
      <Route path="/profile" element={<ProtectedRoute><ProfileDashboard /></ProtectedRoute>} />
      <Route path="/venues" element={<VenueListView />} />
      <Route path="/players" element={<PlayerDirectory />} />
      <Route
        path="/teams"
        element={<ProtectedRoute allowedRoles={[ROLES.TEAMHEAD]}><TeamDashboard /></ProtectedRoute>}
      />
      <Route
        path="/teams/:teamId/squad/:tournamentId"
        element={<ProtectedRoute allowedRoles={[ROLES.TEAMHEAD]}><ManageSquad /></ProtectedRoute>}
      />
      <Route
        path="/tournaments/:id/manage"
        element={<ProtectedRoute allowedRoles={[ROLES.ORGANIZER]}><TournamentControlPanel /></ProtectedRoute>}
      />
      <Route path="/matches" element={<MatchCenterListView />} />
      <Route
        path="/matches/:matchId/score"
        element={<ProtectedRoute allowedRoles={[ROLES.UMPIRE]}><UmpireScoringConsole /></ProtectedRoute>}
      />
    </Routes>
  );
}
