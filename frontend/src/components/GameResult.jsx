export default function GameResult({ game }) {
  const details = [
    game.release_year,
    game.genres.join(', '),
    game.platforms.map((platform) => platform.abbreviation || platform.name).join(', '),
  ].filter(Boolean)

  return (
    <li className="flex gap-4 border-b border-gray-200 py-4">
      {game.cover_url ? (
        <img
          src={game.cover_url}
          alt=""
          loading="lazy"
          className="h-24 w-18 shrink-0 rounded bg-gray-200 object-cover"
        />
      ) : (
        <div className="h-24 w-18 shrink-0 rounded border border-gray-300 bg-gray-200" />
      )}
      <div className="min-w-0">
        <h2 className="text-lg font-semibold">{game.title}</h2>
        <p className="text-gray-500">{details.join(' · ')}</p>
      </div>
    </li>
  )
}
