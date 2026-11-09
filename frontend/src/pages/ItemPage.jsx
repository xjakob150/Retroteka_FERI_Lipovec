import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import client from '../api/client'
import { purchasePrice } from '../components/CollectionItems'
import EditItemDialog from '../components/EditItemDialog'
import EstimatedPrice from '../components/EstimatedPrice'
import MoveToMenu from '../components/MoveToMenu'
import RemoveItemDialog from '../components/RemoveItemDialog'

function Row({ label, children }) {
  return (
    <div className="grid grid-cols-[8rem_1fr] gap-4 py-1.5">
      <dt className="text-xs font-semibold tracking-wide text-gray-600 uppercase">{label}</dt>
      <dd className="break-words">{children}</dd>
    </div>
  )
}

export default function ItemPage() {
  const { id } = useParams()
  const [item, setItem] = useState(null)
  const [collections, setCollections] = useState([])
  const [status, setStatus] = useState('loading')
  const [editing, setEditing] = useState(false)
  const [removing, setRemoving] = useState(false)
  const [moving, setMoving] = useState(false)
  const [notice, setNotice] = useState('')
  const navigate = useNavigate()

  async function handleMove(target) {
    setNotice('')
    setMoving(true)
    try {
      const response = await client.patch(`/items/${item.id}/`, { collection: target.id })
      setItem(response.data)
      setNotice(`Moved to ${target.name}`)
    } catch {
      setNotice('⚠ Could not move this copy. Please try again.')
    }
    setMoving(false)
  }

  const loadItem = useCallback(async () => {
    setStatus('loading')
    try {
      const [itemResponse, collectionsResponse] = await Promise.all([
        client.get(`/items/${id}/`),
        client.get('/collections/'),
      ])
      setItem(itemResponse.data)
      setCollections(collectionsResponse.data)
      setStatus('ready')
    } catch (error) {
      setStatus(error.response?.status === 404 ? 'not-found' : 'failed')
    }
  }, [id])

  useEffect(() => {
    loadItem()
  }, [loadItem])

  if (status === 'loading') {
    return <p className="text-gray-500">Loading…</p>
  }

  if (status === 'not-found') {
    return (
      <div className="py-10 text-center">
        <h1 className="mb-2 text-2xl font-semibold">Item not found</h1>
        <Link to="/collections" className="underline">
          Back to My collections
        </Link>
      </div>
    )
  }

  if (status === 'failed') {
    return (
      <div role="alert" className="rounded-md border border-dashed border-gray-500 p-3">
        <p>⚠ Could not load this item.</p>
        <button type="button" onClick={loadItem} className="mt-2 underline">
          Try again
        </button>
      </div>
    )
  }

  const { game } = item
  const collection = collections.find((entry) => entry.id === item.collection)
  const details = [
    game.release_year,
    `Released on: ${game.platforms.map((platform) => platform.abbreviation || platform.name).join(', ')}`,
  ].filter(Boolean)

  return (
    <div>
      <nav aria-label="Breadcrumb" className="mb-2 text-gray-500">
        <Link to="/collections" className="hover:text-gray-900 hover:underline">
          My collections
        </Link>{' '}
        /{' '}
        <Link to={`/collections/${item.collection}`} className="hover:text-gray-900 hover:underline">
          {collection?.name}
        </Link>{' '}
        / <span className="text-gray-700">{game.title}</span>
      </nav>

      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <h1 className="min-w-0 text-3xl font-bold break-words">{game.title}</h1>
        <div className="flex shrink-0 flex-wrap gap-3">
          <button
            type="button"
            onClick={() => setEditing(true)}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 font-medium hover:bg-gray-100"
          >
            Edit
          </button>
          <MoveToMenu
            collections={collections}
            currentId={item.collection}
            disabled={moving}
            onMove={handleMove}
          />
          <button
            type="button"
            onClick={() => setRemoving(true)}
            className="rounded-md border border-dashed border-gray-400 bg-white px-4 py-2 font-medium hover:bg-gray-100"
          >
            Remove
          </button>
        </div>
      </div>

      {notice && (
        <p role="status" className="mb-4 rounded-md border border-gray-300 bg-white p-3">
          {notice}
        </p>
      )}

      <div className="grid gap-6 md:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
        <section aria-label="Game">
          {game.cover_url ? (
            <img src={game.cover_url} alt="" className="mb-4 w-full max-w-xs rounded bg-gray-200 object-cover" />
          ) : (
            <div className="mb-4 aspect-[3/4] w-full max-w-xs rounded border border-gray-300 bg-gray-200" />
          )}
          {game.genres.length > 0 && (
            <ul className="mb-2 flex flex-wrap gap-2">
              {game.genres.map((genre) => (
                <li key={genre} className="rounded-full border border-gray-300 bg-white px-3 py-0.5 text-sm">
                  {genre}
                </li>
              ))}
            </ul>
          )}
          <p className="mb-3 text-gray-500">{details.join(' · ')}</p>
          {game.summary && <p className="text-gray-700">{game.summary}</p>}
        </section>

        <div className="flex flex-col gap-6 self-start">
          <section aria-labelledby="this-copy" className="rounded-lg border border-gray-300 bg-white p-5">
            <h2 id="this-copy" className="mb-3 text-xl font-semibold">
              This copy
            </h2>
            <dl>
              <Row label="Platform">{item.platform.abbreviation || item.platform.name}</Row>
              <Row label="Region">{item.region_label}</Row>
              <Row label="Condition">{item.condition_label}</Row>
              <Row label="Purchase price">{purchasePrice(item)}</Row>
              <Row label="Notes">{item.notes || '—'}</Row>
            </dl>
          </section>
          <EstimatedPrice item={item} />
        </div>
      </div>

      {removing && (
        <RemoveItemDialog
          item={item}
          onClose={() => setRemoving(false)}
          onRemoved={() => navigate(`/collections/${item.collection}`, { replace: true })}
        />
      )}

      {editing && (
        <EditItemDialog
          item={item}
          onClose={() => setEditing(false)}
          onSaved={(saved) => {
            setItem(saved)
            setEditing(false)
          }}
        />
      )}
    </div>
  )
}
