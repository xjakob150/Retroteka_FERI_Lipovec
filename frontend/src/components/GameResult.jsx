import { Link } from 'react-router'

export default function GameResult({ game, onAdd, addedTo }) {
  const details = [
    game.release_year,
    game.genres.join(', '),
    game.platforms.map((platform) => platform.abbreviation || platform.name).join(', '),
  ].filter(Boolean)

  return (
    <li className="flex flex-wrap gap-4 border-b border-gray-200 py-4 sm:flex-nowrap">
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
      <div className="min-w-0 flex-1">
        <h2 className="text-lg font-semibold">{game.title}</h2>
        <p className="text-gray-500">{details.join(' · ')}</p>
        {game.owned?.length > 0 && (
          <ul aria-label="In your collections" className="mt-2 flex flex-wrap gap-2">
            {game.owned.map(({ platform, collection }) => (
              <li key={`${platform.id}-${collection.id}`} className="max-w-full">
                <Link
                  to={`/collections/${collection.id}`}
                  className="inline-block max-w-full rounded-xl bg-gray-800 px-3 py-0.5 text-sm break-words text-white hover:bg-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
                >
                  In collection · {platform.abbreviation || platform.name} · {collection.name}
                </Link>
              </li>
            ))}
          </ul>
        )}
        {addedTo && (
          <p role="status" className="mt-1 text-sm">
            Added to{' '}
            <Link to={`/collections/${addedTo.id}`} className="font-medium underline">
              {addedTo.name}
            </Link>
          </p>
        )}
      </div>
      {/* Na telefonu gre gumb v svojo vrstico, da naslov ostane širok. */}
      {onAdd && (
        <div className="basis-full sm:basis-auto sm:shrink-0 sm:self-center">
          <button
            type="button"
            onClick={() => onAdd(game)}
            className="rounded-md bg-gray-800 px-3 py-2 font-medium whitespace-nowrap text-white hover:bg-gray-700"
          >
            + Add to collection
          </button>
        </div>
      )}
    </li>
  )
}
