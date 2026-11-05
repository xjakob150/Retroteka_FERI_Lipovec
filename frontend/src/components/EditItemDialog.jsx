import { useEffect, useRef, useState } from 'react'
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

export default function EditItemDialog({ item, onClose, onSaved }) {
  const dialog = useRef(null)
  const [values, setValues] = useState({
    platform: String(item.platform.id),
    region: item.region,
    condition: item.condition,
    purchase_price: item.purchase_price ?? '',
    notes: item.notes,
  })
  const [fieldErrors, setFieldErrors] = useState({})
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    dialog.current.showModal()
  }, [])

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
      const response = await client.patch(`/items/${item.id}/`, {
        platform: values.platform,
        region: values.region,
        condition: values.condition,
        purchase_price: price === '' ? null : price,
        notes: values.notes,
      })
      onSaved(response.data)
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
      <div id={`edit-item-${name}-error`}>
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
    [hint, fieldErrors[name] && `edit-item-${name}-error`].filter(Boolean).join(' ') || undefined

  return (
    <dialog
      ref={dialog}
      onClose={onClose}
      aria-labelledby="edit-item-title"
      className="m-auto w-[calc(100%-2rem)] max-w-xl rounded-lg border border-gray-300 p-0 backdrop:bg-black/40"
    >
      <form onSubmit={handleSubmit} noValidate className="p-6">
        <h2 id="edit-item-title" className="text-xl font-semibold">
          Edit copy
        </h2>
        <p className="mb-5 text-gray-500">{item.game.title}</p>

        <div>
          <label htmlFor="edit-item-platform" className={labelClass}>
            Platform *
          </label>
          <select
            id="edit-item-platform"
            value={values.platform}
            onChange={(event) => set('platform', event.target.value)}
            aria-invalid={Boolean(fieldErrors.platform)}
            aria-describedby={describedBy('platform', 'edit-item-platform-hint')}
            className={fieldClass('platform')}
          >
            {item.game.platforms.map((platform) => (
              <option key={platform.id} value={platform.id}>
                {platform.abbreviation ? `${platform.name} (${platform.abbreviation})` : platform.name}
              </option>
            ))}
          </select>
          <p id="edit-item-platform-hint" className="mt-1 text-sm text-gray-500">
            Only platforms the game was released on
          </p>
          {errorsFor('platform')}
        </div>

        <fieldset className="mt-4" aria-describedby={describedBy('region')}>
          <legend className={labelClass}>Region *</legend>
          <div className="flex flex-wrap gap-x-6 gap-y-2">
            {REGIONS.map(([value, label]) => (
              <label key={value} className="flex items-center gap-2">
                <input
                  type="radio"
                  name="edit-item-region"
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
                className="flex cursor-pointer items-center justify-center border border-gray-300 bg-white px-2 py-2 text-center text-sm first:rounded-l-md last:rounded-r-md has-checked:border-gray-800 has-checked:bg-gray-800 has-checked:text-white has-focus-visible:ring-2 has-focus-visible:ring-gray-400 sm:px-4 sm:text-base"
              >
                <input
                  type="radio"
                  name="edit-item-condition"
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
            <label htmlFor="edit-item-price" className={labelClass}>
              Purchase price (€)
            </label>
            <input
              id="edit-item-price"
              inputMode="decimal"
              value={values.purchase_price}
              onChange={(event) => set('purchase_price', event.target.value)}
              aria-invalid={Boolean(fieldErrors.purchase_price)}
              aria-describedby={describedBy('purchase_price', 'edit-item-price-hint')}
              className={fieldClass('purchase_price')}
            />
            <p id="edit-item-price-hint" className="mt-1 text-sm text-gray-500">
              Optional · ≥ 0, max. 2 decimals
            </p>
            {errorsFor('purchase_price')}
          </div>
          <div>
            <label htmlFor="edit-item-notes" className={labelClass}>
              Notes
            </label>
            <textarea
              id="edit-item-notes"
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
            Save changes
          </button>
        </div>
      </form>
    </dialog>
  )
}
