import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import Skeleton from '../../../components/Skeleton';
import Button from '../../../components/Button';
import LiveScoreWidget from '../components/LiveScoreWidget';
import MatchResultBox from './MatchResultBox';

export default function MatchCenterListView() {
  const { data, loading } = useFetch(ENDPOINTS.MATCHES);
  const { user } = useAuth();
  const order = { LIVE: 0, SCHEDULED: 1, COMPLETED: 2, ABANDONED: 3 };
  const matches = (Array.isArray(data) ? data : data?.results || [])
    .sort((a, b) => order[a.status] - order[b.status]);

  if (loading) return <Skeleton rows={4} />;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Matches</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {matches.map((m) => {
          const teamA = m.teams?.[0] || 'Team A';
          const teamB = m.teams?.[1] || 'Team B';
          return (
            <div key={m.match_id}
              className={`rounded-2xl overflow-hidden bg-blue-50 border-l-5 border-b-5 shadow-md hover:shadow-xl transition-shadow duration-300 ${m.status === 'LIVE' ? 'border-green-300' : 'border-blue-300'}`}>

              {m.status !== 'COMPLETED' && (
                <div className="p-4">
                  <span className="text-xs font-bold text-indigo-600 tracking-widest uppercase block">
                    {m.tournament || 'Unknown Tournament'}
                  </span>
                  <p className="font-bold text-lg text-gray-800 mt-1">
                    {teamA} <span className="text-gray-400 font-normal text-sm mx-2">vs</span> {teamB}
                  </p>
                  <p className="text-xs text-gray-500 mt-1 font-medium">
                    {m.round_type} · R{m.round_number}
                  </p>

                  <div className="mt-4 pt-3 border-t flex justify-between items-center">
                    <div>
                      <span className={`text-[11px] px-3 py-1 rounded-full font-semibold inline-block ${m.status === 'LIVE' ? 'bg-green-100 text-green-700 animate-pulse' :
                          m.status === 'COMPLETED' ? 'bg-gray-100 text-gray-500' :
                            m.status === 'ABANDONED' ? 'bg-red-100 text-red-600' :
                              'bg-blue-100 text-blue-700'
                        }`}>{m.status}</span>
                      <p className="text-xs text-gray-400 mt-1">{m.start_date}</p>
                    </div>
                    {user?.role === 'UMPIRE' && m.primary_umpire === user.user_id && m.status !== 'COMPLETED' && (
                      <Link to={`/matches/${m.match_id}/score`}>
                        {m.status === 'SCHEDULED' && <Button size="sm">Submit Toss</Button>}
                        {m.status === 'LIVE' && <Button size="sm">Score this match</Button>}
                      </Link>
                    )}
                  </div>
                </div>
              )}
              {m.status === 'LIVE' && <LiveScoreWidget matchId={m.match_id} />}
              {m.status === 'COMPLETED' && <MatchResultBox match={m} teamA={teamA} teamB={teamB} />}
            </div>
          );
        })}
      </div>
    </div>
  );
}