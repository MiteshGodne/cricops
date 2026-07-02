export default function PlayerRosterRow({ player }) {
  return (
    <tr className="border-b">
      <td className="py-2">{player.full_name}</td>
      <td>{player.player_role}</td>
      <td>{player.nationality || '-'}</td>
      <td>{player.is_active ? 'Active' : 'Inactive'}</td>
      {/* <td>{player.team_name}</td> */}
    </tr>
  );
}
