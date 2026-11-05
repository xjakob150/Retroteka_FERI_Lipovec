import { Link } from 'react-router'

const price = new Intl.NumberFormat('en-IE', { style: 'currency', currency: 'EUR' })

export function purchasePrice(item) {
  return item.purchase_price === null ? '—' : price.format(item.purchase_price)
}

function Cover({ item }) {
  return item.game.cover_url ? (
    <img src={item.game.cover_url} alt="" loading="lazy" className="h-16 w-12 shrink-0 rounded bg-gray-200 object-cover" />
  ) : (
    <div className="h-16 w-12 shrink-0 rounded border border-gray-300 bg-gray-200" />
  )
}

function platformName(item) {
  return item.platform.abbreviation || item.platform.name
}

export default function CollectionItems({ items }) {
  return (
    <>
      {/* Na računalniku tabela po wireframu 4, na telefonu vrstice kot pri iskanju. */}
      <table className="hidden w-full text-left sm:table">
        <thead className="text-xs font-semibold tracking-wide text-gray-600 uppercase">
          <tr className="border-b border-gray-300">
            <th scope="col" className="py-2">
              <span className="sr-only">Cover</span>
            </th>
            <th scope="col" className="py-2">Title</th>
            <th scope="col" className="py-2">Platform</th>
            <th scope="col" className="py-2">Region</th>
            <th scope="col" className="py-2">Condition</th>
            <th scope="col" className="py-2 text-right">Purchase</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-b border-gray-200">
              <td className="py-2 pr-4">
                <Cover item={item} />
              </td>
              <td className="py-2 pr-4 font-semibold">
                <Link to={`/items/${item.id}`} className="hover:underline">
                  {item.game.title}
                </Link>
              </td>
              <td className="py-2 pr-4">{platformName(item)}</td>
              <td className="py-2 pr-4">{item.region_label}</td>
              <td className="py-2 pr-4">{item.condition_label}</td>
              <td className="py-2 text-right whitespace-nowrap">{purchasePrice(item)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <ul className="sm:hidden">
        {items.map((item) => (
          <li key={item.id} className="flex gap-3 border-b border-gray-200 py-3">
            <Cover item={item} />
            <div className="min-w-0">
              <Link to={`/items/${item.id}`} className="font-semibold hover:underline">
                {item.game.title}
              </Link>
              <p className="text-gray-500">
                {[platformName(item), item.region_label, item.condition_label, purchasePrice(item)].join(' · ')}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </>
  )
}
