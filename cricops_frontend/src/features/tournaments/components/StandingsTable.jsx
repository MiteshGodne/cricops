export default function StandingsTable({ standings }) {
  if (!standings?.length) return <p className="text-gray-500">No standings yet.</p>;
  return (
    <div className="overflow-x-auto rounded-xl border shadow-sm">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
          <tr>
            <th className="p-3 text-left">#</th>
            <th className="p-3 text-left">Team</th>
            <th className="p-3 text-center">P</th>
            <th className="p-3 text-center">W</th>
            <th className="p-3 text-center">L</th>
            <th className="p-3 text-center">T</th>
            <th className="p-3 text-center">NR</th>
            <th className="p-3 text-center font-bold text-gray-700">Pts</th>
            <th className="p-3 text-center">NRR</th>
          </tr>
        </thead>
        <tbody>
          {standings.map((s, i) => (
            <tr key={s.tournament_standing_id} className={`border-t ${i === 0 ? 'bg-yellow-50' : 'hover:bg-gray-50'}`}>
              <td className="p-3 text-gray-400 font-medium">{i + 1}</td>
              <td className="p-3 font-semibold">{s.team_name || s.team}</td>
              <td className="p-3 text-center">{s.matches_played}</td>
              <td className="p-3 text-center text-green-600">{s.matches_won}</td>
              <td className="p-3 text-center text-red-500">{s.matches_lost}</td>
              <td className="p-3 text-center">{s.matches_tied}</td>
              <td className="p-3 text-center text-gray-400">{s.matches_no_result}</td>
              <td className="p-3 text-center font-bold text-blue-700">{s.points}</td>
              <td className="p-3 text-center text-gray-500">{Number(s.net_run_rate).toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}