import { useEffect, useState } from 'react'
import client from '../api/client'
import CollectionCard from '../components/CollectionCard'
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
        <ul className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {collections.map((collection) => (
            <CollectionCard key={collection.id} collection={collection} />
          ))}
          <li>
            <button
              type="button"
              onClick={() => setCreating(true)}
              className="flex h-full min-h-40 w-full flex-col items-center justify-center rounded-lg border border-dashed border-gray-400 text-gray-600 hover:bg-white"
            >
              <span className="text-3xl">+</span>
              <span className="text-lg">New collection</span>
            </button>
          </li>
        </ul>
      )}

      {creating && <NewCollectionDialog onClose={() => setCreating(false)} onCreated={handleCreated} />}
    </div>
  )
}
