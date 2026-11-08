import { useEffect, useState } from 'react'
import client from '../api/client'

export default function PlatformSelect({ value, onChange }) {
  const [platforms, setPlatforms] = useState([])

  useEffect(() => {
    client
      .get('/games/platforms/')
      .then((response) => setPlatforms(response.data))
      .catch(() => setPlatforms([]))
  }, [])

  const generations = []
  for (const platform of platforms) {
    const last = generations.at(-1)
    if (last?.generation === platform.generation) {
      last.platforms.push(platform)
    } else {
      generations.push({ generation: platform.generation, platforms: [platform] })
    }
  }

  return (
    <select
      value={value}
      onChange={(event) => {
        const selected = platforms.find((platform) => String(platform.id) === event.target.value)
        onChange(event.target.value, selected ? selected.abbreviation || selected.name : '')
      }}
      aria-label="Platform"
      className="rounded-md border border-gray-400 bg-white px-3 py-2 focus:ring-2 focus:ring-gray-400 focus:outline-none"
    >
      <option value="">Platform: All</option>
      {generations.map(({ generation, platforms }) => (
        <optgroup key={generation} label={`Generation ${generation}`}>
          {platforms.map((platform) => (
            <option key={platform.id} value={platform.id}>
              {platform.abbreviation ? `${platform.name} (${platform.abbreviation})` : platform.name}
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  )
}
