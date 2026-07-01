export default function StandingsTable({ standings }) {
  return (
    <table className="w-full text-sm text-left">
      <thead><tr className="border-b font-semibold"><th>Team</th><th>P</th><th>W</th><th>L</th><th>T</th><th>Pts</th><th>NRR</th></tr></thead>
      <tbody>
        {standings.map((s) => (
          <tr key={s.tournament_standing_id} className="border-b">
            <td>{s.team_name || s.team}</td>
            <td>{s.matches_played}</td>
            <td>{s.matches_won}</td>
            <td>{s.matches_lost}</td>
            <td>{s.matches_tied}</td>
            <td className="font-semibold">{s.points}</td>
            <td>{s.net_run_rate}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
