import { useState } from 'react'
import { Link } from 'react-router'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'

const GENERIC_ERROR = 'Something went wrong. Please try again.'

const FIELDS = [
  { name: 'username', label: 'Username', type: 'text', autoComplete: 'username' },
  { name: 'password', label: 'Password', type: 'password', autoComplete: 'current-password' },
]

export default function LoginForm() {
  const { startSession } = useAuth()
  const [values, setValues] = useState({ username: '', password: '' })
  const [fieldErrors, setFieldErrors] = useState({})
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function handleChange(event) {
    setValues({ ...values, [event.target.name]: event.target.value })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setFieldErrors({})
    setFormError('')
    setSubmitting(true)
    try {
      const response = await client.post('/auth/login/', values)
      startSession(response.data)
    } catch (error) {
      if (error.response?.status === 400) {
        setFieldErrors(error.response.data)
      } else if (error.response?.status === 401) {
        setFormError(error.response.data.detail)
      } else {
        setFormError(GENERIC_ERROR)
      }
      setSubmitting(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="rounded-lg border border-gray-300 bg-white p-6 sm:p-8"
    >
      <h2 className="mb-5 text-xl font-semibold">Log in</h2>

      {formError && (
        <p role="alert" className="mb-4 rounded-md border border-dashed border-gray-500 p-3 text-sm">
          ⚠ {formError}
        </p>
      )}

      {FIELDS.map((field) => {
        const id = `login-${field.name}`
        const errors = fieldErrors[field.name]
        const errorId = `${id}-error`
        return (
          <div key={field.name} className="mb-4">
            <label
              htmlFor={id}
              className="mb-1 block text-xs font-semibold tracking-wide text-gray-600 uppercase"
            >
              {field.label}
            </label>
            <input
              id={id}
              name={field.name}
              type={field.type}
              autoComplete={field.autoComplete}
              value={values[field.name]}
              onChange={handleChange}
              aria-invalid={Boolean(errors)}
              aria-describedby={errors ? errorId : undefined}
              className={`w-full rounded-md border bg-white px-3 py-2 focus:ring-2 focus:ring-gray-400 focus:outline-none ${
                errors ? 'border-gray-800 ring-1 ring-gray-800' : 'border-gray-300'
              }`}
            />
            {errors && (
              <div id={errorId}>
                {errors.map((message) => (
                  <p key={message} className="mt-1 text-sm text-gray-900">
                    ⚠ {message}
                  </p>
                ))}
              </div>
            )}
          </div>
        )
      })}

      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-gray-500">
          No account?{' '}
          <Link to="/register" className="underline">
            Sign up
          </Link>
        </p>
        <button
          type="submit"
          disabled={submitting}
          className="shrink-0 rounded-md bg-gray-800 px-4 py-2 font-medium text-white hover:bg-gray-700 disabled:opacity-50"
        >
          Log in
        </button>
      </div>
    </form>
  )
}
