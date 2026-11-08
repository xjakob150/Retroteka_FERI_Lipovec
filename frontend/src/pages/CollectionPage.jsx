import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import client from '../api/client'
import { VisibilityLabel } from '../components/CollectionCard'
import CollectionItems from '../components/CollectionItems'
import DeleteCollectionDialog from '../components/DeleteCollectionDialog'
import EditCollectionDialog from '../components/EditCollectionDialog'

export default function CollectionPage() {
  const { id } = useParams()
  const [collection, setCollection] = useState(null)
  const [status, setStatus] = useState('loading')
  const [editing, setEditing] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const navigate = useNavigate()

  const loadCollection = useCallback(async () => {
    setStatus('loading')
    try {
      const response = await client.get(`/collections/${id}/`)
      setCollection(response.data)
      setStatus('ready')
    } catch (error) {
      setStatus(error.response?.status === 404 ? 'not-found' : 'failed')
    }
  }, [id])

  useEffect(() => {
    loadCollection()
  }, [loadCollection])

  function handleSaved(saved) {
    // Odgovor vsebuje samo polja zbirke, izvodi in število ostanejo iz prejšnjega nalaganja.
    setCollection({ ...collection, ...saved })
    setEditing(false)
  }

  if (status === 'loading') {
    return <p className="text-gray-500">Loading…</p>
  }

  if (status === 'not-found') {
    return (
      <div className="py-10 text-center">
        <h1 className="mb-2 text-2xl font-semibold">Collection not found</h1>
        <Link to="/collections" className="underline">
          Back to My collections
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

  return (
    <div>
      <nav aria-label="Breadcrumb" className="mb-2 text-gray-500">
        <Link to="/collections" className="hover:text-gray-900 hover:underline">
          My collections
        </Link>{' '}
        / <span className="text-gray-700">{collection.name}</span>
      </nav>

      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-bold break-words">{collection.name}</h1>
            <VisibilityLabel collection={collection} />
          </div>
          {collection.description && <p className="mt-1 text-gray-600">{collection.description}</p>}
        </div>
        <div className="flex shrink-0 flex-wrap gap-3">
          <button
            type="button"
            onClick={() => setEditing(true)}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 font-medium hover:bg-gray-100"
          >
            Edit
          </button>
          <button
            type="button"
            onClick={() => setDeleting(true)}
            className="rounded-md border border-dashed border-gray-400 bg-white px-4 py-2 font-medium hover:bg-gray-100"
          >
            Delete
          </button>
          <Link
            to="/"
            className="rounded-md bg-gray-800 px-4 py-2 font-medium whitespace-nowrap text-white hover:bg-gray-700"
          >
            + Add game
          </Link>
        </div>
      </div>

      {collection.items.length > 0 ? (
        <CollectionItems items={collection.items} />
      ) : (
        <div className="rounded-lg border border-dashed border-gray-400 py-12 text-center">
          <p className="mb-4 text-lg">This collection is empty</p>
          <Link to="/" className="rounded-md bg-gray-800 px-4 py-2 font-medium text-white hover:bg-gray-700">
            Add game
          </Link>
        </div>
      )}

      {editing && (
        <EditCollectionDialog collection={collection} onClose={() => setEditing(false)} onSaved={handleSaved} />
      )}

      {deleting && (
        <DeleteCollectionDialog
          collection={collection}
          onClose={() => setDeleting(false)}
          onDeleted={() => navigate('/collections', { replace: true })}
        />
      )}
    </div>
  )
}
