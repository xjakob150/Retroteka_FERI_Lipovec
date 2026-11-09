import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import client from '../api/client'
import Pagination from '../components/Pagination'

export default function PublicCollectionsPage() {
  const [result, setResult] = useState(null)
  const [page, setPage] = useState(1)
  const [failed, setFailed] = useState(false)
  const [loading, setLoading] = useState(true)
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let current = true
    setLoading(true)
    setFailed(false)
    client
      .get('/public/collections/', { params: { page } })
      .then((response) => current && setResult(response.data))
      .catch(() => current && setFailed(true))
      .finally(() => current && setLoading(false))
    return () => {
      current = false
    }
  }, [page, attempt])

  function goToPage(next) {
    setPage(next)
    window.scrollTo(0, 0)
  }

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold">Public collections</h1>

      {failed && (
        <div role="alert" className="rounded-md border border-dashed border-gray-500 p-3">
          <p>⚠ Could not load public collections.</p>
          <button type="button" onClick={() => setAttempt(attempt + 1)} className="mt-2 underline">
            Try again
          </button>
        </div>
      )}

      {!result && !failed && <p className="text-gray-500">Loading…</p>}

      {result?.count === 0 && <p className="text-gray-500">No public collections yet.</p>}

      {result?.results.length > 0 && (
        <>
          <ul className="divide-y divide-gray-200 rounded-lg border border-gray-300 bg-white">
            {result.results.map((collection) => (
              <li key={collection.id} className="flex items-center justify-between gap-4 p-4">
                <div className="min-w-0">
                  <Link
                    to={`/public/${collection.id}`}
                    className="text-lg font-semibold break-words hover:underline"
                  >
                    {collection.name}
                  </Link>
                  <p className="text-gray-500">by {collection.owner}</p>
                </div>
                <p className="shrink-0 text-gray-600">
                  {collection.item_count} {collection.item_count === 1 ? 'item' : 'items'}
                </p>
              </li>
            ))}
          </ul>
          <Pagination result={result} loading={loading} onPage={goToPage} label="Public collections pages" />
        </>
      )}
    </div>
  )
}
