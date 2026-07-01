export default function TournamentSquadGrid({ squad }) {
  return (
    <table className="w-full text-sm text-left mt-4">
      <thead><tr className="border-b font-semibold"><th>#</th><th>Player</th><th>Role</th><th>Playing XI</th></tr></thead>
      <tbody>
        {squad.map((s) => (
          <tr key={s.squad_id} className="border-b">
            <td>{s.jersey_number}</td>
            <td>{s.player_name || s.player}</td>
            <td>{s.squad_role}</td>
            <td>{s.is_playing_xi ? 'Yes' : 'No'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
