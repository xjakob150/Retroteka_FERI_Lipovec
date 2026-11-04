import { Link } from 'react-router'

export function VisibilityLabel({ collection }) {
  if (collection.is_hidden) {
    return <span className="rounded-full bg-gray-800 px-3 py-0.5 text-sm text-white">Hidden by moderator</span>
  }
  if (collection.is_public) {
    return <span className="rounded-full border border-gray-500 px-3 py-0.5 text-sm">Public</span>
  }
  return <span className="rounded-full border border-gray-300 px-3 py-0.5 text-sm text-gray-500">Private</span>
}

export default function CollectionCard({ collection }) {
  return (
    <li>
      <Link
        to={`/collections/${collection.id}`}
        className="flex h-full flex-col rounded-lg border border-gray-300 bg-white p-5 hover:border-gray-500 focus:ring-2 focus:ring-gray-400 focus:outline-none"
      >
      <div className="mb-4 flex items-start justify-between gap-3">
        <h2 className="min-w-0 text-xl font-semibold break-words">{collection.name}</h2>
        <div className="shrink-0">
          <VisibilityLabel collection={collection} />
        </div>
      </div>

      {collection.covers.length > 0 ? (
        <div className="mb-4 flex gap-2">
          {collection.covers.map((cover, index) =>
            cover ? (
              <img
                key={index}
                src={cover}
                alt=""
                loading="lazy"
                className="h-16 w-12 rounded bg-gray-200 object-cover"
              />
            ) : (
              <div key={index} className="h-16 w-12 rounded border border-gray-300 bg-gray-200" />
            ),
          )}
        </div>
      ) : (
        <p className="mb-4 flex h-16 items-center text-gray-500">No games yet</p>
      )}

      <p className="mt-auto text-xs font-semibold tracking-wide text-gray-600 uppercase">Items</p>
      <p className="text-2xl font-semibold">{collection.item_count}</p>
      </Link>
    </li>
  )
}
