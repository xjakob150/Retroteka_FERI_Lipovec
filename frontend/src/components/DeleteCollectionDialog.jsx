import { useEffect, useRef, useState } from 'react'
import client from '../api/client'

function itemsMessage(count) {
  if (count === 0) {
    return 'The collection is empty.'
  }
  return `${count} ${count === 1 ? 'item' : 'items'} will be deleted`
}

export default function DeleteCollectionDialog({ collection, onClose, onDeleted }) {
  const dialog = useRef(null)
  const [error, setError] = useState('')
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    dialog.current.showModal()
  }, [])

  async function handleDelete() {
    setError('')
    setDeleting(true)
    try {
      await client.delete(`/collections/${collection.id}/`)
      onDeleted()
    } catch {
      setError('Could not delete the collection. Please try again.')
      setDeleting(false)
    }
  }

  return (
    <dialog
      ref={dialog}
      onClose={onClose}
      aria-labelledby="delete-collection-title"
      aria-describedby="delete-collection-items"
      className="m-auto w-[calc(100%-2rem)] max-w-md rounded-lg border border-gray-300 p-0 backdrop:bg-black/40"
    >
      <div className="p-6">
        <h2 id="delete-collection-title" className="mb-3 text-xl font-semibold">
          Delete collection?
        </h2>
        <p className="font-semibold break-words">{collection.name}</p>
        <p id="delete-collection-items" className="mb-5 text-gray-600">
          {itemsMessage(collection.item_count)}
        </p>

        {error && (
          <p role="alert" className="mb-4 rounded-md border border-dashed border-gray-500 p-3 text-sm">
            ⚠ {error}
          </p>
        )}

        <div className="flex justify-end gap-3">
          <button
            type="button"
            autoFocus
            onClick={() => dialog.current.close()}
            className="rounded-md border border-gray-300 px-4 py-2 font-medium hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleDelete}
            disabled={deleting}
            className="rounded-md bg-gray-800 px-4 py-2 font-medium text-white hover:bg-gray-700 disabled:opacity-50"
          >
            Delete collection
          </button>
        </div>
      </div>
    </dialog>
  )
}
