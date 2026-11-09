import { formatEuro } from './CollectionItems'

const date = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })

function signed(value, text) {
  return `${Number(value) < 0 ? '−' : '+'}${text}`
}

function difference(item) {
  const amount = signed(item.price_difference, formatEuro(Math.abs(item.price_difference)))
  const percent =
    item.price_difference_percent === null
      ? ''
      : ` (${signed(item.price_difference_percent, Math.abs(item.price_difference_percent))} %)`
  return `Bought for ${formatEuro(item.purchase_price)} → ${amount}${percent}`
}

function RefreshPrice({ item, refreshing, refreshError, onRefresh }) {
  const locked = !item.can_refresh_price
  return (
    <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2">
      <button
        type="button"
        onClick={onRefresh}
        disabled={locked || refreshing}
        className="rounded-md border border-gray-300 bg-white px-4 py-2 font-medium hover:bg-gray-100 disabled:opacity-50 disabled:hover:bg-white"
      >
        <span aria-hidden="true">↻ </span>
        {refreshing ? 'Refreshing…' : 'Refresh price'}
      </button>
      {refreshError ? (
        <p role="alert" className="text-red-700">
          The price cannot be refreshed right now
        </p>
      ) : (
        locked && <p className="text-gray-500">Available again tomorrow</p>
      )}
    </div>
  )
}

export default function EstimatedPrice({ item, refreshing, refreshError, onRefresh }) {
  const checked = item.price_checked_at && `Checked ${date.format(new Date(item.price_checked_at))}`
  const listings = `${item.listing_count} eBay ${item.listing_count === 1 ? 'listing' : 'listings'}`
  const refresh = (
    <RefreshPrice item={item} refreshing={refreshing} refreshError={refreshError} onRefresh={onRefresh} />
  )

  return (
    <section aria-labelledby="estimated-price" className="rounded-lg border border-gray-300 bg-white p-5">
      <h2 id="estimated-price" className="mb-3 text-xl font-semibold">
        Estimated price
      </h2>
      {item.estimated_price === null ? (
        <>
          <p className="text-2xl font-semibold text-gray-500">Price not available</p>
          {checked && <p className="mt-1 text-gray-500">{checked} · no matching eBay listings</p>}
          {refresh}
        </>
      ) : (
        <>
          <p className="flex flex-wrap items-center gap-3">
            <span className="text-3xl font-bold">≈ {formatEuro(item.estimated_price)}</span>
            <span className="rounded-full border border-gray-300 px-3 py-0.5 text-sm text-gray-600">estimated</span>
          </p>
          <p className="mt-1 text-gray-500">
            {checked} · median of {listings}
          </p>
          {refresh}
          {item.price_difference !== null && <p className="mt-3">{difference(item)}</p>}
        </>
      )}
    </section>
  )
}
