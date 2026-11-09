import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import client from '../api/client'
import { VisibilityLabel } from '../components/CollectionCard'
import ModeratorBar from '../components/ModeratorBar'
import { useAuth } from '../context/AuthContext'

function PublicItemCard({ item }) {
  const details = [item.platform.abbreviation || item.platform.name, item.region_label, item.condition_label]
  return (
    <li className="flex flex-col rounded-lg border border-gray-300 bg-white p-3">
      {item.game.cover_url ? (
        <img
          src={item.game.cover_url}
          alt=""
          loading="lazy"
          className="mb-3 aspect-[3/4] w-full rounded bg-gray-200 object-cover"
        />
      ) : (
        <div className="mb-3 aspect-[3/4] w-full rounded border border-gray-300 bg-gray-200" />
      )}
      <p className="font-semibold break-words">{item.game.title}</p>
      <p className="text-sm text-gray-500">{details.join(' · ')}</p>
    </li>
  )
}

export default function PublicCollectionPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const [collection, setCollection] = useState(null)
  const [status, setStatus] = useState('loading')

  const loadCollection = useCallback(async () => {
    setStatus('loading')
    try {
      const response = await client.get(`/public/collections/${id}/`)
      setCollection(response.data)
      setStatus('ready')
    } catch (error) {
      setStatus(error.response?.status === 404 ? 'not-found' : 'failed')
    }
  }, [id])

  useEffect(() => {
    loadCollection()
  }, [loadCollection])

  if (status === 'loading') {
    return <p className="text-gray-500">Loading…</p>
  }

  if (status === 'not-found') {
    return (
      <div className="py-10 text-center">
        <h1 className="mb-2 text-2xl font-semibold">Collection not found</h1>
        <Link to="/public" className="underline">
          Back to Public collections
        </Link>
      </div>
    )
  }

  if (status === 'failed') {
    return (
      <div role="alert" className="rounded-md border border-dashed border-gray-500 p-3">
        <p>⚠ Could not load this collection.</p>
        <button type="button" onClick={loadCollection} className="mt-2 underline">
          Try again
        </button>
      </div>
    )
  }

  const isOwner = user?.username === collection.owner
  const isModerator = user?.role === 'moderator' || user?.role === 'admin'

  return (
    <div>
      <nav aria-label="Breadcrumb" className="mb-2 text-gray-500">
        <Link to="/public" className="hover:text-gray-900 hover:underline">
          Public collections
        </Link>{' '}
        / <span className="text-gray-700">{collection.name}</span>
      </nav>

      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-3xl font-bold break-words">{collection.name}</h1>
        {collection.is_hidden && <VisibilityLabel collection={collection} />}
      </div>
      <p className="mt-1 text-gray-500">by {collection.owner} · Public collection</p>
      {collection.description && <p className="mt-1 text-gray-700">{collection.description}</p>}

      {isModerator && (
        <ModeratorBar
          collection={collection}
          isOwn={isOwner}
          onChanged={(changed) => setCollection({ ...collection, ...changed })}
        />
      )}

      {isOwner && (
        <p role="note" className="mt-4 rounded-md border border-gray-300 bg-white p-3">
          This is your collection ·{' '}
          <Link to={`/collections/${collection.id}`} className="font-medium underline">
            Manage in My collections
          </Link>
        </p>
      )}

      <div className="my-6 flex flex-wrap items-end gap-x-8 gap-y-2">
        <div>
          <p className="text-xs font-semibold tracking-wide text-gray-600 uppercase">Items</p>
          <p className="text-2xl font-semibold">{collection.item_count}</p>
        </div>
        <p className="text-gray-500">Purchase prices and notes are private to the owner</p>
      </div>

      {collection.items.length > 0 ? (
        <ul className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
          {collection.items.map((item) => (
            <PublicItemCard key={item.id} item={item} />
          ))}
        </ul>
      ) : (
        <p className="rounded-lg border border-dashed border-gray-400 py-12 text-center text-lg">
          This collection is empty
        </p>
      )}
    </div>
  )
}
