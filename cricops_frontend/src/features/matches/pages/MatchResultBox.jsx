export default function MatchResultBox({ match, teamA, teamB }) {
    if (match.result_type === 'TIE') {
        return (
            <div>
                <span className="text-xs font-semibold text-gray-500 uppercase">{match.round_type} · Round {match.round_number}</span>
                <p className="font-semibold mt-1">{teamA} vs {teamB}</p>
                <p className="text-sm text-gray-500">Played at : {match.start_date ? new Date(match.start_date).toLocaleString() : 'Date TBD'}</p>
                <div className="result-box result-tie">Result : TIE </div>
            </div>
        )
    }
    return (
        <div>
            <span className="text-xs font-semibold text-gray-500 uppercase">{match.round_type} · Round {match.round_number}</span>
            <p className="font-semibold mt-1">{teamA} vs {teamB}</p>
            <p className="text-sm text-gray-500">Played at : {match.start_date ? new Date(match.start_date).toLocaleString() : 'Date TBD'}</p>
            <div className="result-box result-win">Result : {match.result_note}</div>
        </div>
    );
}