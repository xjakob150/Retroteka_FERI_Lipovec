import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatEuro } from './CollectionItems'
import { formatDate } from './EstimatedPrice'

const dayMonth = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short' })
const LINE = '#374151'

function chartPoints(checks) {
  return checks
    .map((check) => ({
      time: new Date(check.checked_at).getTime(),
      price: check.price === null ? null : Number(check.price),
    }))
    .reverse()
}

function Point({ cx, cy, index, points }) {
  if (cx == null || cy == null) return null
  if (index !== points.length - 1) {
    return <circle cx={cx} cy={cy} r={4} fill="white" stroke={LINE} strokeWidth={2} />
  }
  return (
    <g>
      <circle cx={cx} cy={cy} r={6} fill={LINE} />
      <text x={cx} y={cy - 14} textAnchor="end" fill="#111827" fontSize={14} fontWeight={600}>
        {formatEuro(points[index].price)}
      </text>
    </g>
  )
}

function PriceChart({ checks }) {
  const points = chartPoints(checks)
  return (
    <div className="mb-6 h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 28, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="#e5e7eb" strokeDasharray="4 4" vertical={false} />
          <XAxis
            dataKey="time"
            type="number"
            scale="time"
            domain={['dataMin', 'dataMax']}
            tickFormatter={(time) => dayMonth.format(time).replace('Sept', 'Sep')}
            padding={{ left: 20, right: 20 }}
            tick={{ fill: '#4b5563', fontSize: 13 }}
            stroke="#9ca3af"
            minTickGap={24}
          />
          <YAxis
            domain={['auto', 'auto']}
            tickFormatter={(price) => `€${price}`}
            tick={{ fill: '#4b5563', fontSize: 13 }}
            stroke="#9ca3af"
            width={56}
          />
          <Tooltip
            labelFormatter={(time) => formatDate(time)}
            formatter={(price) => [formatEuro(price), 'Price']}
          />
          <Line
            type="linear"
            dataKey="price"
            stroke={LINE}
            strokeWidth={2}
            connectNulls={false}
            isAnimationActive={false}
            dot={(props) => <Point key={props.index} {...props} points={points} />}
            activeDot={{ r: 6, fill: LINE }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function ChecksTable({ checks }) {
  return (
    <table className="w-full text-left">
      <thead className="text-xs font-semibold tracking-wide text-gray-600 uppercase">
        <tr className="border-b border-gray-300">
          <th scope="col" className="py-2 pr-3">
            Date
          </th>
          <th scope="col" className="py-2 pr-3 text-right">
            Price
          </th>
          <th scope="col" className="py-2 pr-3 text-right">
            Listings
          </th>
          <th scope="col" className="py-2">
            Source
          </th>
        </tr>
      </thead>
      <tbody>
        {checks.map((check, index) => (
          <tr key={check.id} className="border-b border-gray-200 last:border-0">
            <td className="py-2 pr-3 whitespace-nowrap">{formatDate(check.checked_at)}</td>
            <td className={`py-2 pr-3 text-right ${index === 0 ? 'font-semibold' : ''}`}>
              {check.price === null ? '—' : formatEuro(check.price)}
            </td>
            <td className="py-2 pr-3 text-right">{check.listing_count}</td>
            <td className="py-2">{check.source_label}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function PriceHistory({ checks }) {
  return (
    <section aria-labelledby="price-history" className="rounded-lg border border-gray-300 bg-white p-5">
      <h2 id="price-history" className="mb-3 text-xl font-semibold">
        Price history
      </h2>
      {checks.length >= 2 ? (
        <PriceChart checks={checks} />
      ) : (
        <p className="mb-4 text-gray-500">At least two price checks are needed for a chart</p>
      )}
      {checks.length > 0 && <ChecksTable checks={checks} />}
    </section>
  )
}
