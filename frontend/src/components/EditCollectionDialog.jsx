import { useEffect, useRef, useState } from 'react'
import client from '../api/client'

const GENERIC_ERROR = 'Something went wrong. Please try again.'

export default function EditCollectionDialog({ collection, onClose, onSaved }) {
  const dialog = useRef(null)
  const [values, setValues] = useState({
    name: collection.name,
    description: collection.description,
    is_public: collection.is_public,
  })
  const [fieldErrors, setFieldErrors] = useState({})
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const publicLocked = collection.is_hidden && !collection.is_public

  useEffect(() => {
    dialog.current.showModal()
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    setFieldErrors({})
    setFormError('')
    setSubmitting(true)
    try {
      const response = await client.patch(`/collections/${collection.id}/`, values)
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

  const fieldClass = (name) =>
    `w-full rounded-md border bg-white px-3 py-2 focus:ring-2 focus:ring-gray-400 focus:outline-none ${
      fieldErrors[name] ? 'border-gray-800 ring-1 ring-gray-800' : 'border-gray-300'
    }`

  const errorsFor = (name) =>
    fieldErrors[name] && (
      <div id={`edit-${name}-error`}>
        {fieldErrors[name].map((message) => (
          <p key={message} className="mt-1 text-sm text-gray-900">
            ⚠ {message}
          </p>
        ))}
      </div>
    )

  return (
    <dialog
      ref={dialog}
      onClose={onClose}
      aria-labelledby="edit-collection-title"
      className="m-auto w-[calc(100%-2rem)] max-w-lg rounded-lg border border-gray-300 p-0 backdrop:bg-black/40"
    >
      <form onSubmit={handleSubmit} noValidate className="p-6">
        <h2 id="edit-collection-title" className="mb-5 text-xl font-semibold">
          Edit collection
        </h2>

        <div className="mb-4">
          <label
            htmlFor="edit-collection-name"
            className="mb-1 block text-xs font-semibold tracking-wide text-gray-600 uppercase"
          >
            Name
          </label>
          <input
            id="edit-collection-name"
            value={values.name}
            onChange={(event) => setValues({ ...values, name: event.target.value })}
            aria-invalid={Boolean(fieldErrors.name)}
            aria-describedby={fieldErrors.name ? 'edit-name-error' : undefined}
            className={fieldClass('name')}
          />
          {errorsFor('name')}
        </div>

        <div className="mb-4">
          <label
            htmlFor="edit-collection-description"
            className="mb-1 block text-xs font-semibold tracking-wide text-gray-600 uppercase"
          >
            Description (optional)
          </label>
          <textarea
            id="edit-collection-description"
            rows={3}
            value={values.description}
            onChange={(event) => setValues({ ...values, description: event.target.value })}
            aria-invalid={Boolean(fieldErrors.description)}
            aria-describedby={fieldErrors.description ? 'edit-description-error' : undefined}
            className={fieldClass('description')}
          />
          {errorsFor('description')}
        </div>

        <fieldset className="mb-5" aria-describedby={publicLocked ? 'edit-visibility-note' : undefined}>
          <legend className="mb-1 text-xs font-semibold tracking-wide text-gray-600 uppercase">
            Visibility
          </legend>
          <div className="flex gap-6">
            {[
              [false, 'Private'],
              [true, 'Public'],
            ].map(([isPublic, label]) => (
              <label key={label} className={`flex items-center gap-2 ${isPublic && publicLocked ? 'text-gray-400' : ''}`}>
                <input
                  type="radio"
                  name="edit-visibility"
                  checked={values.is_public === isPublic}
                  disabled={isPublic && publicLocked}
                  onChange={() => setValues({ ...values, is_public: isPublic })}
                />
                {label}
              </label>
            ))}
          </div>
          {publicLocked && (
            <p id="edit-visibility-note" className="mt-1 text-sm text-gray-500">
              Hidden by a moderator. Only a moderator can make it public again.
            </p>
          )}
          {errorsFor('is_public')}
        </fieldset>

        {formError && (
          <p role="alert" className="mb-4 rounded-md border border-dashed border-gray-500 p-3 text-sm">
            ⚠ {formError}
          </p>
        )}

        <div className="flex justify-end gap-3">
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
