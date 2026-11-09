import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import client from '../api/client'
import { VisibilityLabel } from '../components/CollectionCard'
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
          <ul className="divide-y divide-gray-200 overflow-hidden rounded-lg border border-gray-300 bg-white">
            {result.results.map((collection) => (
              <li key={collection.id}>
                <Link
                  to={`/public/${collection.id}`}
                  className="flex items-center gap-4 p-4 hover:bg-gray-50 focus-visible:bg-gray-50"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-lg font-semibold break-words">{collection.name}</span>
                      {collection.is_hidden && <VisibilityLabel collection={collection} />}
                    </div>
                    <p className="mt-1 flex items-center gap-2 text-sm text-gray-500">
                      <span aria-hidden="true" className="h-5 w-5 shrink-0 rounded-full bg-gray-200" />
                      by {collection.owner}
                    </p>
                    {collection.description && <p className="mt-1 truncate text-gray-600">{collection.description}</p>}
                  </div>
                  <div className="shrink-0 text-right">
                    <p className="text-xs font-semibold tracking-wide text-gray-600 uppercase">Items</p>
                    <p className="text-xl font-semibold">{collection.item_count}</p>
                  </div>
                  <span aria-hidden="true" className="shrink-0 text-2xl text-gray-400">
                    ›
                  </span>
                </Link>
              </li>
            ))}
          </ul>
          <Pagination result={result} loading={loading} onPage={goToPage} label="Public collections pages" />
        </>
      )}
    </div>
  )
}
