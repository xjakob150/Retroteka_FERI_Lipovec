import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router'
import client from '../api/client'

const GENERIC_ERROR = 'Something went wrong. Please try again.'
const REGIONS = [
  ['pal', 'PAL'],
  ['ntsc_u', 'NTSC-U'],
  ['ntsc_j', 'NTSC-J'],
]
const CONDITIONS = [
  ['loose', 'Loose'],
  ['cib', 'Complete in box'],
  ['new', 'New / sealed'],
]
const labelClass = 'mb-1 block text-xs font-semibold tracking-wide text-gray-600 uppercase'

function initialPlatform(game, preferredPlatformId) {
  const ids = game.platforms.map((platform) => String(platform.id))
  if (ids.length === 1) {
    return ids[0]
  }
  return ids.includes(String(preferredPlatformId)) ? String(preferredPlatformId) : ''
}

export default function AddToCollectionDialog({ game, preferredPlatformId, onClose, onAdded }) {
  const dialog = useRef(null)
  const [collections, setCollections] = useState(null)
  const [loadFailed, setLoadFailed] = useState(false)
  const [values, setValues] = useState({
    collection: '',
    platform: initialPlatform(game, preferredPlatformId),
    region: '',
    condition: '',
    purchase_price: '',
    notes: '',
  })
  const [fieldErrors, setFieldErrors] = useState({})
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function loadCollections() {
    setLoadFailed(false)
    try {
      const response = await client.get('/collections/')
      setCollections(response.data)
      if (response.data.length === 1) {
        setValues((current) => ({ ...current, collection: String(response.data[0].id) }))
      }
    } catch {
      setLoadFailed(true)
    }
  }

  function set(name, value) {
    setValues((current) => ({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setFieldErrors({})
    setFormError('')
    setSubmitting(true)
    const price = values.purchase_price.trim().replace(',', '.')
    try {
      await client.post('/items/', {
        collection: values.collection || null,
        game: game.id,
        platform: values.platform || null,
        region: values.region,
        condition: values.condition,
        purchase_price: price === '' ? null : price,
        notes: values.notes,
      })
      onAdded(collections.find((collection) => String(collection.id) === values.collection))
    } catch (error) {
      if (error.response?.status === 400) {
        setFieldErrors(error.response.data)
      } else {
        setFormError(GENERIC_ERROR)
      }
      setSubmitting(false)
    }
  }

  const errorsFor = (name) =>
    fieldErrors[name] && (
      <div id={`add-${name}-error`}>
        {fieldErrors[name].map((message) => (
          <p key={message} className="mt-1 text-sm text-gray-900">
            ⚠ {message}
          </p>
        ))}
      </div>
    )

  const fieldClass = (name) =>
    `w-full rounded-md border bg-white px-3 py-2 focus:ring-2 focus:ring-gray-400 focus:outline-none ${
      fieldErrors[name] ? 'border-gray-800 ring-1 ring-gray-800' : 'border-gray-300'
    }`

  const describedBy = (name, hint) =>
    [hint, fieldErrors[name] && `add-${name}-error`].filter(Boolean).join(' ') || undefined

  useEffect(() => {
    dialog.current.showModal()
    loadCollections()
  }, [])

  const details = [
    game.release_year,
    game.genres.join(', '),
    `Released on: ${game.platforms.map((platform) => platform.abbreviation || platform.name).join(', ')}`,
  ].filter(Boolean)

  return (
    <dialog
      ref={dialog}
      onClose={onClose}
      aria-labelledby="add-to-collection-title"
      className="m-auto w-[calc(100%-2rem)] max-w-2xl rounded-lg border border-gray-300 p-0 backdrop:bg-black/40"
    >
      <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
        <h2 id="add-to-collection-title" className="text-xl font-semibold">
          Add to collection
        </h2>
        <button
          type="button"
          onClick={() => dialog.current.close()}
          aria-label="Close"
          className="rounded-md px-2 text-2xl leading-none hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
        >
          ×
        </button>
      </div>

      <div className="p-6">
        <div className="mb-5 flex gap-4 border-b border-gray-200 pb-5">
          {game.cover_url ? (
            <img src={game.cover_url} alt="" className="h-24 w-18 shrink-0 rounded bg-gray-200 object-cover" />
          ) : (
            <div className="h-24 w-18 shrink-0 rounded border border-gray-300 bg-gray-200" />
          )}
          <div className="min-w-0">
            <p className="text-lg font-semibold">{game.title}</p>
            <p className="text-gray-500">{details.join(' · ')}</p>
          </div>
        </div>

        {loadFailed && (
          <div role="alert" className="rounded-md border border-dashed border-gray-500 p-3">
            <p>⚠ Could not load your collections.</p>
            <button type="button" onClick={loadCollections} className="mt-2 underline">
              Try again
            </button>
          </div>
        )}

        {!collections && !loadFailed && <p className="text-gray-500">Loading…</p>}

        {collections?.length === 0 && (
          <div className="py-4 text-center">
            <p className="mb-4">You have no collections yet.</p>
            <Link to="/collections" className="rounded-md bg-gray-800 px-4 py-2 font-medium text-white hover:bg-gray-700">
              Go to My collections
            </Link>
          </div>
        )}

        {collections?.length > 0 && (
          <form onSubmit={handleSubmit} noValidate>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="add-collection" className={labelClass}>
                  Collection *
                </label>
                <select
                  id="add-collection"
                  value={values.collection}
                  onChange={(event) => set('collection', event.target.value)}
                  aria-invalid={Boolean(fieldErrors.collection)}
                  aria-describedby={describedBy('collection')}
                  className={fieldClass('collection')}
                >
                  <option value="">Select a collection</option>
                  {collections.map((collection) => (
                    <option key={collection.id} value={collection.id}>
                      {collection.name}
                    </option>
                  ))}
                </select>
                {errorsFor('collection')}
              </div>

              <div>
                <label htmlFor="add-platform" className={labelClass}>
                  Platform *
                </label>
                <select
                  id="add-platform"
                  value={values.platform}
                  onChange={(event) => set('platform', event.target.value)}
                  aria-invalid={Boolean(fieldErrors.platform)}
                  aria-describedby={describedBy('platform', 'add-platform-hint')}
                  className={fieldClass('platform')}
                >
                  <option value="">Select a platform</option>
                  {game.platforms.map((platform) => (
                    <option key={platform.id} value={platform.id}>
                      {platform.abbreviation ? `${platform.name} (${platform.abbreviation})` : platform.name}
                    </option>
                  ))}
                </select>
                <p id="add-platform-hint" className="mt-1 text-sm text-gray-500">
                  Only platforms the game was released on
                </p>
                {errorsFor('platform')}
              </div>
            </div>

            <fieldset className="mt-4" aria-describedby={describedBy('region')}>
              <legend className={labelClass}>Region *</legend>
              <div className="flex flex-wrap gap-x-6 gap-y-2">
                {REGIONS.map(([value, label]) => (
                  <label key={value} className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="add-region"
                      checked={values.region === value}
                      onChange={() => set('region', value)}
                    />
                    {label}
                  </label>
                ))}
              </div>
              {errorsFor('region')}
            </fieldset>

            <fieldset className="mt-4" aria-describedby={describedBy('condition')}>
              <legend className={labelClass}>Condition *</legend>
              <div className="grid grid-cols-3 sm:flex">
                {CONDITIONS.map(([value, label]) => (
                  <label
                    key={value}
                    className="flex cursor-pointer items-center justify-center border border-gray-300 bg-white px-2 py-2 text-center text-sm first:rounded-l-md sm:px-4 sm:text-base last:rounded-r-md has-checked:border-gray-800 has-checked:bg-gray-800 has-checked:text-white has-focus-visible:ring-2 has-focus-visible:ring-gray-400"
                  >
                    <input
                      type="radio"
                      name="add-condition"
                      checked={values.condition === value}
                      onChange={() => set('condition', value)}
                      className="sr-only"
                    />
                    {label}
                  </label>
                ))}
              </div>
              {errorsFor('condition')}
            </fieldset>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="add-price" className={labelClass}>
                  Purchase price (€)
                </label>
                <input
                  id="add-price"
                  inputMode="decimal"
                  value={values.purchase_price}
                  onChange={(event) => set('purchase_price', event.target.value)}
                  aria-invalid={Boolean(fieldErrors.purchase_price)}
                  aria-describedby={describedBy('purchase_price', 'add-price-hint')}
                  className={fieldClass('purchase_price')}
                />
                <p id="add-price-hint" className="mt-1 text-sm text-gray-500">
                  Optional · ≥ 0, max. 2 decimals
                </p>
                {errorsFor('purchase_price')}
              </div>
              <div>
                <label htmlFor="add-notes" className={labelClass}>
                  Notes
                </label>
                <textarea
                  id="add-notes"
                  rows={2}
                  value={values.notes}
                  onChange={(event) => set('notes', event.target.value)}
                  aria-invalid={Boolean(fieldErrors.notes)}
                  aria-describedby={describedBy('notes')}
                  className={fieldClass('notes')}
                />
                {errorsFor('notes')}
              </div>
            </div>

            {formError && (
              <p role="alert" className="mt-4 rounded-md border border-dashed border-gray-500 p-3 text-sm">
                ⚠ {formError}
              </p>
            )}

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => dialog.current.close()}
                className="rounded-md border border-gray-300 px-4 py-2 font-medium hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="rounded-md bg-gray-800 px-4 py-2 font-medium text-white hover:bg-gray-700 disabled:opacity-50"
              >
                Add to collection
              </button>
            </div>
          </form>
        )}
      </div>
    </dialog>
  )
}
