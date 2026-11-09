export const PAGE_SIZE = 20

export default function Pagination({ result, loading, onPage, label }) {
  const first = (result.page - 1) * PAGE_SIZE + 1
  const last = first + result.results.length - 1
  const buttonClass =
    'rounded-md border border-gray-300 bg-white px-3 py-1.5 hover:bg-gray-100 disabled:opacity-40 disabled:hover:bg-white'

  return (
    <nav aria-label={label} className="mt-4 flex items-center justify-between gap-3">
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
