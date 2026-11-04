import { useRef, useState } from 'react'
import client from '../api/client'
import GameResult from '../components/GameResult'
import PlatformSelect from '../components/PlatformSelect'

const MIN_LENGTH = 3
// Enako kot PAGE_SIZE v backend/games/search.py.
const PAGE_SIZE = 20
const TOO_MANY_SEARCHES = 'Too many searches. Please wait a moment and try again.'
const GENERIC_ERROR = 'Something went wrong. Please try again.'

export default function SearchPage() {
  const [text, setText] = useState('')
  const [platform, setPlatform] = useState({ id: '', label: '' })
  const [tooShort, setTooShort] = useState(false)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const latestRequest = useRef(0)

  async function runSearch(query, searchPlatform, page) {
    const request = ++latestRequest.current
    setLoading(true)
    setError('')
    try {
      const params = { q: query, page }
      if (searchPlatform.id) {
        params.platform = searchPlatform.id
      }
      const response = await client.get('/games/search/', { params })
      if (request === latestRequest.current) {
        setResult({ query, platform: searchPlatform, ...response.data })
      }
    } catch (requestError) {
      if (request === latestRequest.current) {
        setResult(null)
        setError(requestError.response?.status === 429 ? TOO_MANY_SEARCHES : GENERIC_ERROR)
      }
    } finally {
      if (request === latestRequest.current) {
        setLoading(false)
      }
    }
  }

  function goToPage(page) {
    runSearch(result.query, result.platform, page)
    window.scrollTo(0, 0)
  }

  function handleSubmit(event) {
    event.preventDefault()
    const query = text.trim()
    if (query.length < MIN_LENGTH) {
      setTooShort(true)
      return
    }
    setTooShort(false)
    runSearch(query, platform, 1)
  }

  return (
    <div>
      <h1 className="mb-5 text-3xl font-bold">Search games</h1>

      <form onSubmit={handleSubmit} role="search" className="flex flex-col gap-3 sm:flex-row">
        <input
          type="search"
          value={text}
          onChange={(event) => setText(event.target.value)}
          aria-label="Game title"
          aria-describedby="search-hint"
          placeholder="Search by title"
          className="min-w-0 flex-1 rounded-md border border-gray-400 bg-white px-3 py-2 focus:ring-2 focus:ring-gray-400 focus:outline-none"
        />
        <PlatformSelect value={platform.id} onChange={(id, label) => setPlatform({ id, label })} />
        <button
          type="submit"
          disabled={loading}
          className="shrink-0 rounded-md bg-gray-800 px-4 py-2 font-medium text-white hover:bg-gray-700 disabled:opacity-50"
        >
          Search
        </button>
      </form>
      <p
        id="search-hint"
        className={`mt-1 text-sm ${tooShort ? 'font-medium text-gray-900' : 'text-gray-500'}`}
      >
        {tooShort ? '⚠ ' : ''}Type at least 3 characters · results from IGDB, retro platforms only
      </p>

      {error && (
        <p role="alert" className="mt-6 rounded-md border border-dashed border-gray-500 p-3">
          ⚠ {error}
        </p>
      )}

      {result?.saved_data && (
        <p role="status" className="mt-6 rounded-md border border-gray-400 bg-gray-100 p-3">
          Showing saved data
        </p>
      )}

      {result && result.results.length > 0 && (
        <>
          <p className="mt-6 text-gray-500">
            {result.count} {result.count === 1 ? 'result' : 'results'} for “{result.query}”{' '}
            {result.platform.id ? `on ${result.platform.label}` : 'on all platforms'}
          </p>
          <ul>
            {result.results.map((game) => (
              <GameResult key={game.id} game={game} />
            ))}
          </ul>
          <Pagination result={result} loading={loading} onPage={goToPage} />
        </>
      )}

      {result && result.results.length === 0 && (
        <div className="mt-10 text-center">
          <p className="text-lg font-semibold">No games found</p>
          <p className="text-gray-500">Check the spelling or try a shorter title.</p>
        </div>
      )}
    </div>
  )
}


function Pagination({ result, loading, onPage }) {
  const first = (result.page - 1) * PAGE_SIZE + 1
  const last = first + result.results.length - 1
  const buttonClass =
    'rounded-md border border-gray-300 bg-white px-3 py-1.5 hover:bg-gray-100 disabled:opacity-40 disabled:hover:bg-white'

  return (
    <nav aria-label="Search results pages" className="mt-4 flex items-center justify-between gap-3">
      <p className="text-gray-500">
        {first}–{last} of {result.count}
      </p>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => onPage(result.page - 1)}
          disabled={loading || result.page === 1}
          className={buttonClass}
        >
          ‹ Prev
        </button>
        <button
          type="button"
          onClick={() => onPage(result.page + 1)}
          disabled={loading || last >= result.count}
          className={buttonClass}
        >
          Next ›
        </button>
      </div>
    </nav>
  )
}
