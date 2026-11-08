import { useEffect, useRef, useState } from 'react'
import client from '../api/client'

export default function RemoveItemDialog({ item, onClose, onRemoved }) {
  const dialog = useRef(null)
  const [error, setError] = useState('')
  const [removing, setRemoving] = useState(false)

  useEffect(() => {
    dialog.current.showModal()
  }, [])

  async function handleRemove() {
    setError('')
    setRemoving(true)
    try {
      await client.delete(`/items/${item.id}/`)
      onRemoved()
    } catch {
      setError('Could not remove this copy. Please try again.')
      setRemoving(false)
    }
  }

  return (
    <dialog
      ref={dialog}
      onClose={onClose}
      aria-labelledby="remove-item-title"
      aria-describedby="remove-item-copy"
      className="m-auto w-[calc(100%-2rem)] max-w-md rounded-lg border border-gray-300 p-0 backdrop:bg-black/40"
    >
      <div className="p-6">
        <h2 id="remove-item-title" className="mb-3 text-xl font-semibold">
          Remove this copy?
        </h2>
        <p id="remove-item-copy" className="mb-5">
          <span className="font-semibold break-words">{item.game.title}</span>
          <br />
          <span className="text-gray-600">
            {[item.platform.abbreviation || item.platform.name, item.region_label, item.condition_label].join(' · ')}
          </span>
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
            onClick={handleRemove}
            disabled={removing}
            className="rounded-md bg-gray-800 px-4 py-2 font-medium text-white hover:bg-gray-700 disabled:opacity-50"
          >
            Remove
          </button>
        </div>
      </div>
    </dialog>
  )
}
