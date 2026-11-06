import { useState } from 'react'
import client from '../api/client'

export default function ModeratorBar({ collection, isOwn, onChanged }) {
  const [working, setWorking] = useState(false)
  const [error, setError] = useState('')

  async function change(action) {
    setError('')
    setWorking(true)
    try {
      const response = await client.post(`/public/collections/${collection.id}/${action}/`)
      onChanged(response.data)
    } catch {
      setError('⚠ Could not change the visibility. Please try again.')
    }
    setWorking(false)
  }

  const buttonClass =
    'shrink-0 rounded-md border border-gray-300 bg-white px-4 py-2 font-medium hover:bg-gray-100 disabled:opacity-50'

  return (
    <section
      aria-label="Moderation"
      className="mt-4 flex flex-col items-start gap-x-4 gap-y-3 rounded-lg border-2 border-dashed border-gray-400 p-4 sm:flex-row sm:flex-wrap sm:items-center"
    >
      <span className="rounded border border-gray-400 px-2 py-0.5 text-xs font-semibold tracking-wide uppercase">
        Moderator
      </span>
      {collection.is_hidden ? (
        <>
          <p className="min-w-0 sm:flex-1">This collection is hidden from other visitors.</p>
          {isOwn ? (
            // Svoje zbirke moderator ne more razkriti (US-12), zato gumba ni.
            <p className="text-gray-600">Another moderator or administrator must make it visible again.</p>
          ) : (
            <button type="button" onClick={() => change('unhide')} disabled={working} className={buttonClass}>
              Make visible
            </button>
          )}
        </>
      ) : (
        <>
          <p className="min-w-0 sm:flex-1">
            Hide this collection if its name, description or content is inappropriate. It will not be deleted.
          </p>
          <button type="button" onClick={() => change('hide')} disabled={working} className={buttonClass}>
            Hide collection
          </button>
        </>
      )}
      {error && (
        <p role="alert" className="basis-full text-sm">
          {error}
        </p>
      )}
    </section>
  )
}
