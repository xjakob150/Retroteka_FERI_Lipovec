import { useEffect, useState } from 'react'
import client from '../api/client'
import NewCollectionDialog from '../components/NewCollectionDialog'

export default function MyCollectionsPage() {
  const [collections, setCollections] = useState(null)
  const [failed, setFailed] = useState(false)
  const [creating, setCreating] = useState(false)

  async function loadCollections() {
    setFailed(false)
    try {
      const response = await client.get('/collections/')
      setCollections(response.data)
    } catch {
      setFailed(true)
    }
  }

  useEffect(() => {
    loadCollections()
  }, [])

  function handleCreated() {
    setCreating(false)
    loadCollections()
  }

  const newCollectionButton = (
    <button
      type="button"
      onClick={() => setCreating(true)}
      className="shrink-0 rounded-md bg-gray-800 px-4 py-2 font-medium whitespace-nowrap text-white hover:bg-gray-700"
    >
      + New collection
    </button>
  )

  return (
    <div>
      <div className="mb-6 flex items-center justify-between gap-4">
        <h1 className="text-3xl font-bold">My collections</h1>
        {newCollectionButton}
      </div>

      {failed && (
        <div role="alert" className="rounded-md border border-dashed border-gray-500 p-3">
          <p>⚠ Could not load your collections.</p>
          <button type="button" onClick={loadCollections} className="mt-2 underline">
            Try again
          </button>
        </div>
      )}

      {!collections && !failed && <p className="text-gray-500">Loading…</p>}

      {collections?.length === 0 && <p className="text-gray-500">You have no collections yet.</p>}

      {collections?.length > 0 && (
        <ul className="divide-y divide-gray-200 rounded-lg border border-gray-300 bg-white">
          {collections.map((collection) => (
            <li key={collection.id} className="flex items-center justify-between gap-4 p-4">
              <div className="min-w-0">
                <h2 className="truncate text-lg font-semibold">{collection.name}</h2>
                <p className="text-gray-500">
                  {collection.item_count} {collection.item_count === 1 ? 'item' : 'items'}
                </p>
              </div>
              <span className="shrink-0 rounded-full border border-gray-400 px-3 py-0.5 text-sm">
                {collection.is_public ? 'Public' : 'Private'}
              </span>
            </li>
          ))}
          <li>
            <button
              type="button"
              onClick={() => setCreating(true)}
              className="w-full p-4 text-left text-gray-600 hover:bg-gray-50"
            >
              + New collection
            </button>
          </li>
        </ul>
      )}

      {creating && <NewCollectionDialog onClose={() => setCreating(false)} onCreated={handleCreated} />}
    </div>
  )
}
